from django.shortcuts import render, get_object_or_404, redirect
from django.utils import dateformat
from django.utils.timezone import now
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.db import transaction, IntegrityError
from json import loads
import calendar

from django import forms
from django.forms import modelformset_factory
from django.forms.models import model_to_dict
from crispy_forms.utils import render_crispy_form

from .models import Persona, Sensei, Estudiante, Representante, Clase, Horario, Inscripciones, DiaDeClase, Asistencias, Pagos, Sede, Curso, MetodosPagos, DescuentoEspecial, Becas, Becados, Solvencias, FacturaPago, Comprobantes
from .forms import SenseiForm, EstudianteForm, RepresentanteForm, SeleccionAsistenciaForm, AsistenciaForm, DiasForm, AsistenciaRezagadosForm, AsistenciaFormsetHelper, ClaseForm, PaymentForm, PagosForm
from .filters import SenseiFilter, EstudianteFilter, ClaseFilter, HorarioFilter, InscripcionesFilter, DiaDeClaseFilter, PagosFilter, SolvenciaFilter, MetodosPagosFilter, DescuentoEspecialFilter, BecasFilter, BecadosFilter
from django.views.generic import ListView, DetailView, FormView, CreateView, UpdateView, DeleteView

from django.core.paginator import Paginator

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import io
from reportlab.pdfgen import canvas
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
import json

def payment_view(request):
    error_message = None
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        print('DEBUG POST DATA:', request.POST)  # <-- Depuración
        if form.is_valid():
            print('DEBUG CLEANED DATA:', form.cleaned_data)  # <-- Depuración
            # Generate PDF
            buffer = io.BytesIO()
            pdf = canvas.Canvas(buffer)

            # Márgenes y disposición inspirados en la imagen de referencia
            margin_x = 50
            margin_y = 60
            page_width = 595  # A4 width in points
            usable_width = page_width - 2 * margin_x
            left_x = margin_x
            right_x = margin_x + usable_width // 2 + 10
            y_start = 670  # Más abajo para que los datos principales estén más bajos
            y = y_start
            line_height = 28

            # Encabezado principal
            pdf.setFont("Helvetica-Bold", 18)
            pdf.drawString(margin_x, 750, "William José Fajardo Cortéz")
            pdf.setFont("Helvetica", 10)
            pdf.drawString(margin_x, 732, "RIF: V-10307741-5")
            pdf.drawString(margin_x, 717, "Caracas, Venezuela")

            # Datos principales en dos columnas, alineados horizontalmente
            pdf.setFont("Helvetica-Bold", 12)
            pdf.setFillColorRGB(0.8, 0.4, 0.1)
            pdf.drawString(left_x, y, "Recibido el:")
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica", 11)
            pdf.drawString(left_x + 80, y, f"{form.cleaned_data['payment_date']}")

            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(right_x, y, "Emitido por:")
            pdf.setFont("Helvetica", 11)
            pdf.drawString(right_x + 80, y, f"{form.cleaned_data['issued_by']}")
            y -= line_height

            # Columna izquierda
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(left_x, y, "He recibido por:")
            pdf.setFont("Helvetica", 11)
            pdf.drawString(left_x + 110, y, f"{form.cleaned_data['student_name']}")
            y -= line_height

            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(left_x, y, "C.I.")
            pdf.setFont("Helvetica", 11)
            pdf.drawString(left_x + 40, y, f"{form.cleaned_data['student_id']}")

            # Columna derecha 
            y2 = y_start - line_height
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(right_x, y2, "codigo de referencia:")
            pdf.setFont("Helvetica", 11)
            # Mover el valor de la referencia 3 espacios más a la derecha respecto a la posición anterior
            pdf.drawString(page_width - margin_x - 100, y2, f"{form.cleaned_data.get('reference_code', '')}")
            y2 -= line_height

            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(right_x, y2, "Método de pago:")
            pdf.setFont("Helvetica", 11)
            pdf.drawString(right_x + 110, y2, f"{form.cleaned_data['payment_method']}")

            # Línea divisoria (subida 3 cm)
            y_line = min(y, y2) - 20 - 35  
            pdf.setStrokeColorRGB(0.7, 0.7, 0.7)
            pdf.setLineWidth(1)
            pdf.line(margin_x, y_line, page_width - margin_x, y_line)

            # Tabla de descripción 
            y_table = y_line - 25
            pdf.setFont("Helvetica-Bold", 12)
            pdf.setFillColorRGB(0.4, 0.7, 0.4)
            pdf.drawString(margin_x, y_table, "Descripción")
            pdf.drawString(margin_x + usable_width // 2 - 40, y_table, "Cantidad")
            pdf.drawString(page_width - margin_x - 100, y_table, "Precio total")
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica", 11)
            y_table -= line_height

            # Filas de la tabla (subidas)
            pdf.drawString(margin_x, y_table, f"{form.cleaned_data.get('payment_concept', '')}")
            pdf.drawString(margin_x + usable_width // 2 - 40, y_table, f"{form.cleaned_data.get('amount', '')}")
            pdf.drawString(page_width - margin_x - 100, y_table, f"{form.cleaned_data.get('amount', '')}")
            y_table -= line_height

            # Línea divisoria inferior
            y_footer = y_table - 80  
            pdf.setStrokeColorRGB(0.7, 0.7, 0.7)
            pdf.line(margin_x, y_footer, page_width - margin_x, y_footer)

            pdf.setFont("Helvetica", 10)
            pdf.setFillColorRGB(0.3, 0.7, 0.3)
            pdf.drawString(margin_x, y_footer - 20, "Teléfonos: 0424-271-04-56 / 0212-266-80-88")
            pdf.drawString(page_width - margin_x - 120, y_footer - 20, "Subtotal")
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica", 11)
            pdf.drawString(page_width - margin_x - 60, y_footer - 20, f"{form.cleaned_data.get('amount', '')}$")

            pdf.setFont("Helvetica-Bold", 12)
            pdf.setFillColorRGB(0.3, 0.7, 0.3)
            pdf.drawString(page_width - margin_x - 120, y_footer - 40, "Total")
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(page_width - margin_x - 60, y_footer - 40, f"{form.cleaned_data.get('amount', '')}$")
            pdf.setFillColorRGB(0, 0, 0)

            # Footer
            pdf.setFont("Helvetica", 14)
            pdf.setFillColorRGB(0.2, 0.2, 0.2)
            pdf.drawCentredString(page_width // 2, margin_y, "Su aporte ha sido recibido satisfactoriamente y agradezco todo el apoyo que brinda")
            pdf.setFillColorRGB(0, 0, 0)

            pdf.save()
            buffer.seek(0)

            # Send email
            cuerpo = (
                f"Buenos dias Sr. {form.cleaned_data['student_name']}.,\n\n"
                "¡Muchas gracias por su pago!\n\n"
                f"Me complace avisarle, que su operación con un monto de {form.cleaned_data['amount']}$ referente a su mensualidad de {form.cleaned_data['month']} ha sido recibido exitosamente.\n\n"
                "Le recordamos que todos los pagos realizados a la Fundación deben realizarse los primeros 5 días del mes para poder disfrutar de la enseñanza del idioma y seguir creciendo junto con nosotros.\n\n"
                "En caso de tener alguna duda u opinión puede contactarnos a través de nuestro correo electrónico o por nuestro número de atención al cliente.\n\n"
                f"Atentamente {form.cleaned_data['issued_by']}\n"
                "Administración de la Fundación Zen Gaku."
            )
            email = EmailMessage(
                'Factura Zengaku',
                cuerpo,
                'noreply@example.com',
                [form.cleaned_data['email']]
            )
            email.attach('Factura_Zengaku.pdf', buffer.getvalue(), 'application/pdf')
            email.send()

            # --- GUARDAR EL PAGO EN LA BASE DE DATOS ---
            try:
                with transaction.atomic():
                    # Buscar o crear Persona y Estudiante
                    cedula = form.cleaned_data['student_id']
                    persona = Persona.objects.filter(cedula=cedula).first()
                    if not persona:
                        # Mejor manejo de nombres: primer nombre, segundo nombre, primer apellido, segundo apellido
                        name_parts = form.cleaned_data['student_name'].strip().split()
                        first_name = name_parts[0] if len(name_parts) > 0 else ''
                        middle_name = name_parts[1] if len(name_parts) > 2 else ''
                        last_name_1 = name_parts[-2] if len(name_parts) > 1 else ''
                        last_name_2 = name_parts[-1] if len(name_parts) > 2 else ''
                        if len(name_parts) == 2:
                            last_name_1 = name_parts[1]
                            last_name_2 = ''
                        persona = Persona.objects.create(
                            nacionalidad='V',  # O ajustar si hay campo en el form
                            cedula=cedula,
                            first_name=first_name,
                            middle_name=middle_name,
                            last_name_1=last_name_1,
                            last_name_2=last_name_2,
                            personal_email=form.cleaned_data['email'],
                            telefono='0424-0000000',  # Default, as not in form
                        )
                    if not persona or not persona.pk:
                        raise Exception('No se pudo crear ni encontrar la Persona para el pago.')
                    estudiante = Estudiante.objects.filter(personal_data=persona).first()
                    if not estudiante:
                        estudiante = Estudiante.objects.create(
                            personal_data=persona,
                            status=Estudiante.Status.ACTIVO
                        )
                    if not estudiante or not estudiante.pk:
                        raise Exception('No se pudo crear ni encontrar el Estudiante para el pago.')

                    # Buscar clase (usando el concepto de pago, si es posible)
                    clase = None
                    concepto = form.cleaned_data['payment_concept']
                    clases = Clase.objects.filter(curso__modulo__icontains=concepto)
                    if clases.exists():
                        clase = clases.first()
                    else:
                        clase = Clase.objects.first()  # fallback: primera clase
                    if not clase or not clase.pk:
                        raise Exception('No se pudo encontrar ninguna Clase para el pago.')

                    # Buscar método de pago
                    metodo = MetodosPagos.objects.filter(metodo__iexact=form.cleaned_data['payment_method']).first()
                    if not metodo:
                        metodo = MetodosPagos.objects.first()  # fallback
                    if not metodo or not metodo.pk:
                        raise Exception('No se pudo encontrar ningún Método de Pago válido.')

                    # Asegurar que el estudiante esté inscrito en la clase
                    inscripcion = Inscripciones.objects.filter(estudiante=estudiante, clase=clase).first()
                    if not inscripcion:
                        inscripcion = Inscripciones.objects.create(estudiante=estudiante, clase=clase, precio_a_pagar=clase.precio)
                    if not inscripcion or not inscripcion.pk:
                        raise Exception('No se pudo crear ni encontrar la Inscripción para el pago.')
                    # Crear el pago (pero NO repartir el monto automáticamente, solo registrar el pago)
                    pago = Pagos(
                        estudiante=estudiante,
                        clase=clase,
                        metodo=metodo,
                        monto_pagado=int(form.cleaned_data['amount']),
                        referencia=form.cleaned_data['reference_code'],
                        fecha_pago=form.cleaned_data['payment_date'],
                        obs=form.cleaned_data['payment_concept'],
                    )
                    pago.save(skip_reparto=True)

                    # Marcar el mes seleccionado como abonado en Solvencias y crear comprobante
                    mes_cancelado = form.cleaned_data['month']
                    meses_es = [
                        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                    ]
                    mes_index = meses_es.index(mes_cancelado) + 1
                    solvencia = Solvencias.objects.filter(
                        estudiante=estudiante,
                        clase=clase,
                        mes__month=mes_index
                    ).order_by('-mes').first()
                    abono = int(form.cleaned_data['amount'])
                    if solvencia:
                        solvencia.monto_abonado += abono
                        if solvencia.monto_abonado >= solvencia.monto_a_pagar:
                            solvencia.pagado = Solvencias.Pagado.PAGADO
                            solvencia.monto_abonado = solvencia.monto_a_pagar
                        else:
                            solvencia.pagado = Solvencias.Pagado.ABONADO
                        solvencia.save()
                    else:
                        from django.utils import timezone
                        from datetime import datetime
                        year = form.cleaned_data['payment_date'].year
                        fecha_mes = datetime(year, mes_index, 1, tzinfo=timezone.get_current_timezone())
                        # Obtener monto a pagar de la inscripción
                        inscripcion = Inscripciones.objects.filter(estudiante=estudiante, clase=clase).first()
                        monto_a_pagar = inscripcion.precio_a_pagar if inscripcion else abono
                        pagado_status = Solvencias.Pagado.PAGADO if abono >= monto_a_pagar else Solvencias.Pagado.ABONADO
                        solvencia = Solvencias.objects.create(
                            estudiante=estudiante,
                            clase=clase,
                            mes=fecha_mes,
                            pagado=pagado_status,
                            monto_a_pagar=monto_a_pagar,
                            monto_abonado=abono,
                        )
                    # Crear comprobante si no existe para este pago y solvencia
                    if not Comprobantes.objects.filter(pagos=pago, solvencias=solvencia).exists():
                        Comprobantes.objects.create(
                            pagos=pago,
                            solvencias=solvencia,
                            monto_aplicado=abono,
                        )

                    # Guardar también en FacturaPago
                    print('DEBUG: Valor de month en cleaned_data:', form.cleaned_data.get('month'))  # <-- Línea de depuración
                    FacturaPago.objects.create(
                        issued_by=form.cleaned_data['issued_by'],
                        student_name=form.cleaned_data['student_name'],
                        student_id=form.cleaned_data['student_id'],
                        amount=form.cleaned_data['amount'],
                        reference_code=form.cleaned_data['reference_code'],
                        payment_date=form.cleaned_data['payment_date'],
                        payment_method=form.cleaned_data['payment_method'],
                        payment_concept=form.cleaned_data['payment_concept'],
                        email=form.cleaned_data['email'],
                        emitted_by=form.cleaned_data['emitted_by'],
                        month=form.cleaned_data['month'],
                    )
            except Exception as e:
                error_message = "Ocurrió un error al guardar el pago. Por favor, verifica los datos ingresados. Si el problema persiste, contacta a soporte."
                print(f"Error guardando el pago: {e}")
            if not error_message:
                # --- REPARTO DE ABONO ENTRE MESES (CORREGIDO) ---
                abono_restante = int(form.cleaned_data['amount'])
                year = form.cleaned_data['payment_date'].year
                from django.utils import timezone
                from datetime import datetime
                meses_es = [
                    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                ]
                mes_index = meses_es.index(form.cleaned_data['month']) + 1
                # 1. Aplicar al mes seleccionado
                fecha_mes = datetime(year, mes_index, 1, tzinfo=timezone.get_current_timezone())
                solvencia = Solvencias.objects.filter(
                    estudiante=estudiante,
                    clase=clase,
                    mes__month=mes_index
                ).order_by('-mes').first()
                inscripcion = Inscripciones.objects.filter(estudiante=estudiante, clase=clase).first()
                monto_a_pagar = inscripcion.precio_a_pagar if inscripcion else abono_restante
                if not solvencia:
                    solvencia = Solvencias.objects.create(
                        estudiante=estudiante,
                        clase=clase,
                        mes=fecha_mes,
                        pagado=Solvencias.Pagado.SIN_PAGAR,
                        monto_a_pagar=monto_a_pagar,
                        monto_abonado=0,
                    )
                abono_faltante = monto_a_pagar - solvencia.monto_abonado
                abono_aplicar = min(abono_restante, abono_faltante)
                solvencia.monto_abonado += abono_aplicar
                if solvencia.monto_abonado >= monto_a_pagar:
                    solvencia.pagado = Solvencias.Pagado.PAGADO
                    solvencia.monto_abonado = monto_a_pagar
                else:
                    solvencia.pagado = Solvencias.Pagado.ABONADO
                solvencia.save()
                if not Comprobantes.objects.filter(pagos=pago, solvencias=solvencia).exists():
                    Comprobantes.objects.create(
                        pagos=pago,
                        solvencias=solvencia,
                        monto_aplicado=abono_aplicar,
                    )
                abono_restante -= abono_aplicar
                # 2. Si hay sobrante, abonar SOLO al mes siguiente inmediato (mes_index + 1)
                if abono_restante > 0 and mes_index < 12:
                    mes_siguiente = mes_index + 1
                    fecha_mes_sig = datetime(year, mes_siguiente, 1, tzinfo=timezone.get_current_timezone())
                    # Buscar o crear la solvencia EXACTAMENTE para el mes siguiente
                    solvencia_sig = Solvencias.objects.filter(
                        estudiante=estudiante,
                        clase=clase,
                        mes__year=year,
                        mes__month=mes_siguiente
                    ).order_by('-mes').first()
                    if not solvencia_sig:
                        solvencia_sig = Solvencias.objects.create(
                            estudiante=estudiante,
                            clase=clase,
                            mes=fecha_mes_sig,
                            pagado=Solvencias.Pagado.SIN_PAGAR,
                            monto_a_pagar=monto_a_pagar,
                            monto_abonado=0,
                        )
                    abono_faltante_sig = monto_a_pagar - solvencia_sig.monto_abonado
                    abono_aplicar_sig = min(abono_restante, abono_faltante_sig)
                    # Limitar el abono para que nunca supere el monto a pagar
                    nuevo_abono = solvencia_sig.monto_abonado + abono_aplicar_sig
                    if nuevo_abono >= monto_a_pagar:
                        solvencia_sig.monto_abonado = monto_a_pagar
                        solvencia_sig.pagado = Solvencias.Pagado.PAGADO
                    elif nuevo_abono > 0:
                        solvencia_sig.monto_abonado = nuevo_abono
                        solvencia_sig.pagado = Solvencias.Pagado.ABONADO
                    else:
                        solvencia_sig.monto_abonado = 0
                        solvencia_sig.pagado = Solvencias.Pagado.SIN_PAGAR
                    solvencia_sig.save()
                    if not Comprobantes.objects.filter(pagos=pago, solvencias=solvencia_sig).exists():
                        Comprobantes.objects.create(
                            pagos=pago,
                            solvencias=solvencia_sig,
                            monto_aplicado=abono_aplicar_sig,
                        )
                    # No seguir abonando a más meses
            # --- NO GUARDAR MESES INHABILITADOS EN LA SESIÓN AQUÍ ---
            from django.shortcuts import redirect
            return redirect("payment_form")
        else: 
            print('DEBUG FORM ERRORS:', form.errors)  # <-- Depuración
    else:
        form = PaymentForm()

    # Obtener historial de pagos
    letra = request.GET.get('letra')
    if letra:
        historial_pagos = FacturaPago.objects.filter(student_name__istartswith=letra).order_by('-payment_date')
    else:
        historial_pagos = FacturaPago.objects.all().order_by('-payment_date')

    # --- RECUPERAR MESES INHABILITADOS PARA EL FORMULARIO ---
    # Buscar estudiante y clase de la inscripción activa o del último pago
    estudiante_id = None
    clase_id = None
    if request.method == 'POST' and form.is_valid():
        # Ya tenemos estudiante y clase del pago
        estudiante_id = estudiante.id if 'estudiante' in locals() and estudiante else None
        clase_id = clase.id if 'clase' in locals() and clase else None
    else:
        # Intentar obtener de la inscripción activa o del último pago
        inscripcion = None
        if 'estudiante' in locals() and 'clase' in locals() and estudiante and clase:
            inscripcion = Inscripciones.objects.filter(estudiante=estudiante, clase=clase).first()
        if not inscripcion:
            ultimo_pago = Pagos.objects.order_by('-fecha_pago').first()
            if ultimo_pago:
                estudiante_id = ultimo_pago.estudiante.id
                clase_id = ultimo_pago.clase.id
        else:
            estudiante_id = inscripcion.estudiante.id
            clase_id = inscripcion.clase.id
    meses_inhabilitados = []
    if estudiante_id and clase_id:
        meses_inhabilitados_key = f"meses_inhabilitados_{estudiante_id}_{clase_id}"
        meses_inhabilitados = request.session.get(meses_inhabilitados_key, [])
    return render(request, 'gakusei/myfactura/payment_form.html', {
        'form': form,
        'historial_pagos': historial_pagos,
        'letra': letra,
        'meses_inhabilitados': meses_inhabilitados,
        'error_message': error_message,
    })



# Filter View + Pagination Function
def paginator_filter_view(request, Model, ModelFilter, items_per_page = 20):
    model_filter = ModelFilter(request.GET, queryset=Model.objects.all())

    paginator = Paginator(model_filter.qs, items_per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return model_filter, page_obj


@login_not_required
def login_view(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "gakusei/login.html", {
                "message": "Usuario o Contraseña Inválida."
            })
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        return render(request, "gakusei/login.html")
    

@login_not_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))



def index(request):
    return render(request, "gakusei/index.html")


# Sensei
sensei_templates = "gakusei/sensei/"
class SenseiListView(ListView):
    model = Sensei
    paginate_by = 20
    template_name = sensei_templates + "list.html"

    def get_queryset(self):
        return super().get_queryset().exclude(pk=1)

class SenseiDetailView(DetailView):
    model = Sensei
    template_name = sensei_templates + "detail.html"


class SenseiCreateView(CreateView):
    model = Sensei
    form_class = SenseiForm
    template_name = sensei_templates + "create.html"

    def get_success_url(self):
        return reverse("sensei-detail", kwargs={"pk":self.object.pk})

    

class SenseiEditView(UpdateView):
    model = Sensei
    form_class = SenseiForm
    template_name = sensei_templates + "edit.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().pk == 1:
            return redirect(reverse_lazy("sensei"))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("sensei-detail", kwargs={"pk":self.object.pk})
    
    def get_form_kwargs(self):
        # Obtenemos los datos que seran colocados en los campos del formulario
        kwargs = super().get_form_kwargs()

        # Obtenemos al objeto que se va a Editar
        sensei = self.get_object()

        # Pegamos los datos de 'Personal Data' a la variable que será procesada en el __init__ del formulario
        kwargs["personal_data"] = {
            "nacionalidad"   : sensei.personal_data.nacionalidad,
            "cedula"         : sensei.personal_data.cedula,
            "first_name"     : sensei.personal_data.first_name,
            "middle_name"    : sensei.personal_data.middle_name,
            "last_name_1"    : sensei.personal_data.last_name_1,
            "last_name_2"    : sensei.personal_data.last_name_2,
            "telefono"       : sensei.personal_data.telefono,
            "personal_email" : sensei.personal_data.personal_email,
        }

        return kwargs


class SenseiDeleteView(DeleteView):
    model = Sensei
    template_name = sensei_templates + "delete.html"
    success_url = reverse_lazy("sensei")

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().pk == 1:
            return redirect(reverse_lazy("sensei"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = self.get_object()
        success_url = self.get_success_url()
        
        p = self.object.personal_data
        p.delete()

        return HttpResponseRedirect(success_url)
    

def SenseiFilterView(request):
    sensei_list = Sensei.objects.all().exclude(pk=1)
    sensei_filter = SenseiFilter(request.GET, queryset=sensei_list)

    paginator = Paginator(sensei_filter.qs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, sensei_templates + "filter.html", {"filter":sensei_filter, "object_list": page_obj})




# Estudiante
estudiante_templates = "gakusei/estudiante/"
class EstudianteListView(ListView):
    model = Estudiante
    paginate_by = 20
    template_name = estudiante_templates + "list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class EstudianteDetailView(DetailView):
    model = Estudiante
    template_name = estudiante_templates + "detail.html"


class EstudianteCreateView(CreateView):
    model = Estudiante
    form_class = EstudianteForm
    template_name = estudiante_templates + "create.html"

    def get_success_url(self):
        return reverse("estudiante-detail", kwargs={"pk":self.object.pk})


class EstudianteEditView(UpdateView):
    model = Estudiante
    form_class = EstudianteForm
    template_name = estudiante_templates + "edit.html"

    def get_success_url(self):
        return reverse("estudiante-detail", kwargs={"pk":self.object.pk})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        estudiante = self.get_object()

        kwargs["personal_data"] = {
            "nacionalidad"   : estudiante.personal_data.nacionalidad,
            "cedula"         : estudiante.personal_data.cedula,
            "first_name"     : estudiante.personal_data.first_name,
            "middle_name"    : estudiante.personal_data.middle_name,
            "last_name_1"    : estudiante.personal_data.last_name_1,
            "last_name_2"    : estudiante.personal_data.last_name_2,
            "telefono"       : estudiante.personal_data.telefono,
            "personal_email" : estudiante.personal_data.personal_email,
        }

        return kwargs


class EstudianteDeleteView(DeleteView):
    model = Estudiante
    template_name = estudiante_templates + "delete.html"
    success_url = reverse_lazy("estudiante")

    def form_valid(self, form):
        self.object = self.get_object()
        success_url = self.get_success_url()
        
        p = self.object.personal_data
        p.delete()

        return HttpResponseRedirect(success_url)


def EstudianteFilterView(request):
    estudiante_filter, page_obj = paginator_filter_view(request, Estudiante, EstudianteFilter)
    
    return render(request, estudiante_templates + "filter.html", {"filter":estudiante_filter, "object_list": page_obj})



    
    
# Representante
representante_templates = "gakusei/representante/"
class RepresentanteCreateView(FormView):
    form_class = RepresentanteForm
    template_name = representante_templates + "create.html"

    success_url = reverse_lazy("index")

    def form_valid(self, form):
        estudiante = form.save()

        return HttpResponseRedirect(reverse("estudiante-detail", kwargs={"pk":estudiante.pk}))
    

class RepresentanteCreatePopup(FormView):
    form_class = RepresentanteForm
    template_name = representante_templates + "create-popup.html"

    success_url = None

    def form_valid(self, form):
        representante = form.save()

        return JsonResponse({"id":  representante.pk,}, status=201)
    
    def form_invalid(self, form):
        return JsonResponse({"error_form": form.as_div()}, status=422)


# Clase
clase_templates = "gakusei/clase/"

class ClaseListView(ListView):
    model = Clase
    paginate_by = 20
    template_name = clase_templates + "list.html"


class ClaseDetailView(DetailView):
    model = Clase
    template_name = clase_templates + "detail.html"


class ClaseCreateView(CreateView):
    model = Clase
    form_class = ClaseForm
    template_name = clase_templates + "create.html"

    def get_success_url(self):
        return reverse("clase-detail", kwargs={"pk": self.object.pk})

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        form.fields["sensei"].queryset = Sensei.objects.filter(status=Sensei.Status.ACTIVO).exclude(pk=1)
        return form

    def form_invalid(self, form):
        print("DEBUG - Form is invalid")
        print("DEBUG - Form errors:", form.errors)
        print("DEBUG - Form data:", form.data)
        print("DEBUG - Cleaned data:", form.cleaned_data)
        return super().form_invalid(form)

    def form_valid(self, form):
        print("DEBUG - Form is valid")
        print("DEBUG - Form data:", form.data)
        print("DEBUG - Cleaned data:", form.cleaned_data)
        try:
            response = super().form_valid(form)
            print("DEBUG - Class created successfully:", self.object)
            print("DEBUG - Class attributes:", vars(self.object))
            return response
        except Exception as e:
            print("DEBUG - Error creating class:", str(e))
            print("DEBUG - Error type:", type(e))
            import traceback
            print("DEBUG - Full traceback:", traceback.format_exc())
            form.add_error(None, f"Error al guardar la clase: {str(e)}")
            return self.form_invalid(form)


class ClaseEditView(UpdateView):
    model = Clase
    form_class = ClaseForm
    template_name = clase_templates + "edit.html"

    def get_success_url(self):
        return reverse("clase-detail", kwargs={"pk": self.object.pk})

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        form.fields["sensei"].queryset = Sensei.objects.filter(status=Sensei.Status.ACTIVO).exclude(pk=1)
        return form
    
class ClaseDeleteView(DeleteView):
    model = Clase
    template_name = clase_templates + "delete.html"
    success_url = reverse_lazy("clase")


def ClaseFilterView(request):
    clase_filter, page_obj = paginator_filter_view(request, Clase, ClaseFilter)
    
    return render(request, clase_templates + "filter.html", {"filter":clase_filter, "object_list": page_obj})




# Horario
horario_templates = "gakusei/horario/"

class HorarioListView(ListView):
    model = Horario
    paginate_by = 20
    template_name = horario_templates + "list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dias_semana = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        for dia in dias_semana:
            context[f'horarios_{dia.lower()}'] = Horario.objects.filter(dia_semana__iexact=dia)
        return context


class HorarioDetailView(DetailView):
    model = Horario
    template_name = horario_templates + "detail.html"


class HorarioCreateView(CreateView):
    model = Horario
    fields = "__all__"
    template_name = horario_templates + "create.html"

    def get_success_url(self):
        return reverse("horario-detail", kwargs={"pk": self.object.pk})

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        form.fields["hora_entrada"].widget = forms.TimeInput(attrs={"type":"time"})
        form.fields["hora_salida"].widget  = forms.TimeInput(attrs={"type":"time"})

        if clase_id := self.request.GET.get("clase"):
            readonly_select = {"onfocus":"this.blur();", "style":"pointer-events: none;", "disabled":"true"}
            form.fields["clase"].widget.attrs.update(readonly_select)

        return form
    
    def get_initial(self):
        initial = super().get_initial()

        clase_id = self.request.GET.get("clase")

        if clase_id:
            initial["clase"] = clase_id

        return initial




class HorarioEditView(UpdateView):
    model = Horario
    fields = "__all__"
    template_name = horario_templates + "edit.html"

    def get_success_url(self):
        return reverse("horario-detail", kwargs={"pk": self.object.pk})

    def get_form(self, form_class = None):

        form = super().get_form(form_class)

        form.fields["hora_entrada"].widget = forms.TimeInput(attrs={"type":"time", "step":"1"})
        form.fields["hora_salida"].widget  = forms.TimeInput(attrs={"type":"time", "step":"1"})

        return form


class HorarioDeleteView(DeleteView):
    model = Horario
    template_name = horario_templates + "delete.html"
    success_url = reverse_lazy("horario")



def HorarioFilterView(request):
    horario_filter, page_obj = paginator_filter_view(request, Horario, HorarioFilter)
    
    return render(request, horario_templates + "filter.html", {"filter":horario_filter, "object_list": page_obj})



# Inscripciones
inscripciones_templates = "gakusei/inscripciones/"

class InscripcionesListView(ListView):
    model = Inscripciones
    paginate_by = 20

    template_name = inscripciones_templates + "list.html"

class InscripcionesDetailView(DetailView):
    model = Inscripciones
    template_name = inscripciones_templates + "detail.html"

class InscripcionesCreateView(CreateView):
    model = Inscripciones
    fields = "__all__"

    template_name = inscripciones_templates + "create.html"

    def get_initial(self):
        initial = super().get_initial()

        if clase_id := self.request.GET.get("clase"):
            initial["clase"] = clase_id

        if estudiante_id := self.request.GET.get("estudiante"):
            initial["estudiante"] = estudiante_id

        return initial


    def get_form(self, form_class = None):

        form = super().get_form(form_class)
        form.fields["clase"].queryset = Clase.objects.filter(status__in=[Clase.Status.ACTIVO, Clase.Status.PAUSADO])
        form.fields["estudiante"].queryset = Estudiante.objects.filter(status=Estudiante.Status.ACTIVO)

        readonly_select = {"onfocus":"this.blur();", "style":"pointer-events: none;", "disabled":"true"}

        if clase_id := self.request.GET.get("clase"):

            form.fields["estudiante"].queryset = Estudiante.objects.filter(
                status=Estudiante.Status.ACTIVO
            ).exclude(
                pk__in=Inscripciones.objects.filter(clase=Clase.objects.filter(pk=clase_id)[0]).values_list("estudiante", flat=True)
            )

            form.fields["clase"].widget.attrs.update(readonly_select)

        if estudiante_id := self.request.GET.get("estudiante"):
            form.fields["estudiante"].widget.attrs.update(readonly_select)

        return form

    def get_success_url(self):
        return reverse("inscripciones-detail", kwargs={"pk":self.object.pk})


class InscripcionesEditView(UpdateView):
    model = Inscripciones
    fields = "__all__"

    template_name = inscripciones_templates + "edit.html"


    def get_form(self, form_class = None):

        form = super().get_form(form_class)
        form.fields["clase"].queryset = Clase.objects.filter(status__in=[Clase.Status.ACTIVO, Clase.Status.PAUSADO])
        form.fields["estudiante"].queryset = Estudiante.objects.filter(status=Estudiante.Status.ACTIVO)

        return form

    def get_success_url(self):
        return reverse("inscripciones-detail", kwargs={"pk":self.object.pk})


class InscripcionesDeleteView(DeleteView):
    model = Inscripciones
    template_name = inscripciones_templates + "delete.html"
    success_url = reverse_lazy("inscripciones")


def InscripcionesFilterView(request):
    inscripciones_filter, page_obj = paginator_filter_view(request, Inscripciones, InscripcionesFilter)
    
    return render(request, inscripciones_templates + "filter.html", {"filter":inscripciones_filter, "object_list": page_obj})



# Dia de Clases
dia_de_clase_templates = "gakusei/dia_de_clase/"

class DiaDeClaseListView(ListView):
    model = DiaDeClase
    paginate_by = 20

    template_name = dia_de_clase_templates + "list.html"


class DiaDeClaseDetailView(DetailView):
    model = DiaDeClase
    template_name = dia_de_clase_templates + "detail.html"


class DiaDeClaseCreateView(CreateView):
    model = DiaDeClase
    fields = "__all__"

    template_name = dia_de_clase_templates + "create.html"

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        form.fields["fecha"].widget = forms.DateInput(attrs={"type":"date"})

        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_clase"] = SeleccionAsistenciaForm()

        return context

    def get_success_url(self):
        return reverse("dia-de-clase-detail", kwargs={"pk":self.object.pk})
    

class DiaDeClaseEditView(UpdateView):
    model = DiaDeClase
    fields = "__all__"

    template_name = dia_de_clase_templates + "edit.html"

    def get_form(self, form_class = None):
        form = super().get_form(form_class)

        print(self.object.clase())
        
        form.fields["horario"].queryset = Horario.objects.filter(clase=self.object.clase())
        form.fields["fecha"].widget = forms.DateInput(attrs={"type":"date"}, format="%Y-%m-%d")

        return form

    def get_success_url(self):
        return reverse("dia-de-clase-detail", kwargs={"pk":self.object.pk})


class DiaDeClaseDeleteView(DeleteView):
    model = DiaDeClase
    template_name = dia_de_clase_templates + "delete.html"
    success_url = reverse_lazy("dia-de-clase")



def DiaDeClaseFilterView(request):
    dia_de_clase_filter, page_obj = paginator_filter_view(request, DiaDeClase, DiaDeClaseFilter)
    
    return render(request, dia_de_clase_templates + "filter.html", {"filter":dia_de_clase_filter, "object_list": page_obj})




# Asistencias
asistencia_templates = "gakusei/asistencia/"

class AsistenciaListView(ListView):
    model = Asistencias
    paginate_by = 20

    template_name = asistencia_templates + "list.html"


class AsistenciaDetailView(DetailView):
    model = Asistencias
    template_name = asistencia_templates + "detail.html"



def AsistenciaCreate(request):

    if request.method == "POST":
        try:
            with transaction.atomic():

                clase = get_object_or_404(klass=Clase, pk=request.POST.get("clase"))
                estudiantes_numero = clase.inscripciones.count()    

                dias_form = DiasForm(request.POST)

                if dias_form.is_valid():
                    dia = dias_form.save()

                    # Como no se puede alterar el formset despues de creado y el request no puede ser modificado,
                    # creamos una copia y agregamos el dia_clase ahi
                    post_data = request.POST.copy()

                    for _ in range(int(post_data["form-TOTAL_FORMS"])):
                        post_data[f"form-{_}-dia_clase"] = dia

                    AsistenciaFormSet = modelformset_factory(Asistencias, form=AsistenciaForm, extra=estudiantes_numero, can_delete=False)
                    formset = AsistenciaFormSet(post_data)


                    if formset.is_valid():
                        formset.save()

                        response = {
                            "url_redirect": reverse("dia-de-clase-detail", kwargs={"pk":dia.pk}),
                        }

                        return JsonResponse(response, status=200)
                    else:
                        print(formset.errors)
                        raise Exception("Formset no valid")
                    
                else:
                    raise Exception("Dias no valid")
        
        except Exception as e:
            return JsonResponse({"error": f"Error al insertar datos en BDD: {e}"}, status=400)



    return render(request, asistencia_templates + "create.html", {
        "clase_form": SeleccionAsistenciaForm()
    })



class AsistenciaCreateViewClasic(CreateView):
    # ASISTENCIAS-CLASIC
    model = Asistencias
    fields = "__all__"

    template_name = asistencia_templates + "create-all-at-once.html"

    def get_success_url(self):
        return reverse("asistencia-detail", kwargs={"pk":self.object.pk})



def AsistenciaCreateRezagados(request):

    if request.method == "POST":
        # SOLO API
        clase = Clase.objects.get(pk=request.POST.get("clase"))

        form = AsistenciaRezagadosForm(request.POST)

        if form.is_valid():
            
            f = form.save()
            dia = f.dia_clase

            return JsonResponse({"url_redirect":reverse("dia-de-clase-detail", kwargs={"pk":dia.pk})}, status=200)
        
        else:
            form.fields["dia_clase"].queryset = DiaDeClase.objects.filter(horario__clase=clase)

        return JsonResponse({"error_form":form.as_div()}, status=400)

    # if "clase" in request.GET:
    #     # Acomodar esto despues para cada clase
    #     print("GET", request.GET)
    #     clase_form = SeleccionAsistenciaForm()
    #     clase_form.fields["clase"].widget = forms.TextInput()
    #     clase_form.fields["clase"].initial = "2"

    else:
        clase_form = SeleccionAsistenciaForm()

    return render(request, asistencia_templates + "create-rezagados.html", {
        "clase_form": clase_form,
    })


class AsistenciaEditView(UpdateView):
    model = Asistencias
    template_name = asistencia_templates + "edit.html"
    fields = "__all__"

    def get_form(self, form_class = None):
        form = super().get_form(form_class)

        readonly_select = {"onfocus":"this.blur();", "style":"pointer-events: none;", "disabled":"true"}
        
        form.fields["dia_clase"].widget.attrs.update(readonly_select)
        form.fields["estudiante"].widget.attrs.update(readonly_select)

        form.fields["presente"].help_text = "Seleccionado: Presente, Sin seleccionar: No Presente"

        return form


    def get_success_url(self):
        return reverse("dia-de-clase-detail", kwargs={"pk":self.object.dia_clase.pk})


# PAGOS
pagos_templates = "gakusei/pagos/"

class PagosListView(ListView):
    model = Pagos
    paginate_by = 20
    template_name = pagos_templates + "list.html"

    def get_queryset(self):
        # Agrupar por estudiante y clase, mostrar solo el pago más reciente por cada combinación
        pagos = super().get_queryset()
        pagos = pagos.order_by('estudiante', 'clase', '-fecha')
        unique = {}
        result = []
        for pago in pagos:
            key = (pago.estudiante_id, pago.clase_id)
            if key not in unique:
                unique[key] = True
                result.append(pago)
        return result



class PagosDetailView(DetailView):
    model = Pagos
    template_name = pagos_templates + "detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meses_lista = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        context["meses_lista"] = meses_lista
        # Prepara solvencias por mes para el template
        solvencias_por_mes = {}
        estudiante = self.object.estudiante
        clase = self.object.clase
        for i, mes in enumerate(meses_lista, start=1):
            solvencia = estudiante.solvencias.filter(clase=clase, mes__month=i).first()
            solvencias_por_mes[mes] = solvencia
        context["solvencias_por_mes"] = solvencias_por_mes
        # Recuperar meses inhabilitados de la sesión si existen
        meses_inhabilitados = self.request.session.get(f"meses_inhabilitados_{self.object.pk}", [])
        context["meses_inhabilitados"] = meses_inhabilitados
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        estudiante = self.object.estudiante
        clase = self.object.clase
        meses_es = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        from .models import Solvencias, Comprobantes
        mes_a_marcar = request.POST.get('marcar_pagado')
        mes_a_desmarcar = request.POST.get('desmarcar_pagado')
        # Procesar inhabilitación de meses
        if request.POST.getlist('meses_inhabilitados'):
            meses_inhabilitados = request.POST.getlist('meses_inhabilitados')
            request.session[f"meses_inhabilitados_{self.object.pk}"] = meses_inhabilitados
        from datetime import datetime
        if mes_a_marcar:
            mes_index = meses_es.index(mes_a_marcar) + 1
            # Buscar la solvencia más reciente para ese mes y clase
            solvencia = estudiante.solvencias.filter(clase=clase, mes__month=mes_index).order_by('-mes').first()
            if solvencia:
                solvencia.pagado = solvencia.Pagado.PAGADO
                solvencia.monto_abonado = solvencia.monto_a_pagar
                solvencia.save()
            else:
                from django.utils import timezone
                year = self.object.fecha_pago.year
                fecha_mes = datetime(year, mes_index, 1, tzinfo=timezone.get_current_timezone())
                solvencia = Solvencias.objects.create(
                    estudiante=estudiante,
                    clase=clase,
                    mes=fecha_mes,
                    pagado=Solvencias.Pagado.PAGADO,
                    monto_a_pagar=0,
                    monto_abonado=0,
                )
            if not Comprobantes.objects.filter(pagos=self.object, solvencias=solvencia).exists():
                Comprobantes.objects.create(
                    pagos=self.object,
                    solvencias=solvencia,
                    monto_aplicado=solvencia.monto_a_pagar,
                )
            messages.success(request, f"Mes {mes_a_marcar} marcado como pagado.")
        elif mes_a_desmarcar:
            mes_index = meses_es.index(mes_a_desmarcar) + 1
            # Buscar la solvencia más reciente para ese mes y clase
            solvencia = estudiante.solvencias.filter(clase=clase, mes__month=mes_index).order_by('-mes').first()
            if solvencia:
                solvencia.pagado = solvencia.Pagado.SIN_PAGAR
                solvencia.monto_abonado = 0
                solvencia.save()
                # Eliminar comprobante asociado a este pago y solvencia
                Comprobantes.objects.filter(pagos=self.object, solvencias=solvencia).delete()
                messages.success(request, f"Mes {mes_a_desmarcar} desmarcado como pagado.")
        return self.get(request, *args, **kwargs)

class PagosCreateView(CreateView):
    model = Pagos
    form_class = PagosForm
    template_name = pagos_templates + "create.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["fecha_pago"].widget = forms.DateInput(attrs={"type": "date"})
        return form
    
    def get_success_url(self):
        return reverse("pagos-detail", kwargs={"pk":self.object.pk})

    def form_valid(self, form):
        # Ya no se requiere clase, solo se guarda el pago
        return super().form_valid(form)

    def form_invalid(self, form):
        from django.contrib import messages
        messages.error(self.request, 'Por favor corrija los errores en el formulario antes de continuar.')
        return super().form_invalid(form)


class PagosDeleteView(DeleteView):
    model = Pagos
    template_name = "gakusei/pagos/delete.html"
    success_url = reverse_lazy("pagos")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Eliminar comprobantes relacionados
        from .models import Comprobantes, Solvencias
        comprobantes = Comprobantes.objects.filter(pagos=self.object)
        # Opcional: actualizar solvencias relacionadas
        for comprobante in comprobantes:
            solvencia = comprobante.solvencias
            # Restar el monto aplicado de este comprobante
            if solvencia.monto_abonado >= comprobante.monto_aplicado:
                solvencia.monto_abonado -= comprobante.monto_aplicado
                # Si el abono baja de lo requerido, actualizar estado
                if solvencia.monto_abonado < solvencia.monto_a_pagar:
                    solvencia.pagado = Solvencias.Pagado.ABONADO if solvencia.monto_abonado > 0 else Solvencias.Pagado.SIN_PAGAR
                solvencia.save()
            comprobante.delete()
        return super().delete(request, *args, **kwargs)
def PagosFilterView(request):
    pagos_filter, page_obj = paginator_filter_view(request, Pagos, PagosFilter)
    
    return render(request, pagos_templates + "filter.html", {"filter":pagos_filter, "object_list": page_obj})




# SOLVENCIAS
solvencias_templates = "gakusei/solvencia/"
 
class SolvenciaClaseListView(ListView):
    model = Clase
    paginate_by = 20
    template_name = solvencias_templates + "list-clase.html"


class SolvenciaClaseDetailView(DetailView):
    model = Clase
    template_name = solvencias_templates + "detail-clase.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        solvencias = self.get_object().solvencias.all().order_by("estudiante", "mes")

        context["solvencias"] = list(solvencias)
        
        return context

def SolvenciaFilterView(request):
    solvencias_filter, page_obj = paginator_filter_view(request, Clase, SolvenciaFilter)
    
    return render(request, solvencias_templates + "filter.html", {"filter":solvencias_filter, "object_list": page_obj})




# Sedes
sede_templates = "gakusei/sede/"

class SedeListView(ListView):
    model = Sede
    paginate_by = 20
    template_name = sede_templates + "list.html"


class SedeDetailView(DetailView):
    model = Sede
    template_name = sede_templates + "detail.html"


class SedeCreateView(CreateView):
    model = Sede
    fields = "__all__"

    template_name = sede_templates + "create.html"

    def get_success_url(self):
        return reverse("sede-detail", kwargs={"pk":self.object.pk})
    

class SedeEditView(UpdateView):
    model = Sede
    fields = "__all__"

    template_name = sede_templates + "edit.html"

    def get_success_url(self):
        return reverse("sede-detail", kwargs={"pk":self.object.pk})



# Curso
curso_templates = "gakusei/curso/"

class CursoListView(ListView):
    model = Curso
    paginate_by = 20
    template_name = curso_templates + "list.html"


class CursoDetailView(DetailView):
    model = Curso
    template_name = curso_templates + "detail.html"


class CursoCreateView(CreateView):
    model = Curso
    fields = "__all__"

    template_name = curso_templates + "create.html"

    def get_success_url(self):
        return reverse("curso-detail", kwargs={"pk":self.object.pk})
    

class CursoEditView(UpdateView):
    model = Curso
    fields = "__all__"

    template_name = curso_templates + "edit.html"

    def get_success_url(self):
        return reverse("curso-detail", kwargs={"pk":self.object.pk})
    




# Métodos de Pago
metodo_templates = "gakusei/metodos_pago/"

class MetodosPagoListView(ListView):
    model = MetodosPagos
    paginate_by = 20
    template_name = metodo_templates + "list.html"


class MetodosPagoDetailView(DetailView):
    model = MetodosPagos
    template_name = metodo_templates + "detail.html"


class MetodosPagoCreateView(CreateView):
    model = MetodosPagos
    fields = "__all__"

    template_name = metodo_templates + "create.html"

    def get_success_url(self):
        return reverse("metodos-pago-detail", kwargs={"pk":self.object.pk})
    

def MetodosPagoFilterView(request):
    metodo_filter, page_obj = paginator_filter_view(request, MetodosPagos, MetodosPagosFilter)
    
    return render(request, metodo_templates + "filter.html", {"filter":metodo_filter, "object_list": page_obj})





# Descuentos Especiales
descuento_templates = "gakusei/descuentos_especiales/"

class DescuentoEspecialListView(ListView):
    model = DescuentoEspecial
    paginate_by = 20
    template_name = descuento_templates + "list.html"


class DescuentoEspecialDetailView(DetailView):
    model = DescuentoEspecial
    template_name = descuento_templates + "detail.html"


class DescuentoEspecialCreateView(CreateView):
    model = DescuentoEspecial
    fields = "__all__"

    template_name = descuento_templates + "create.html"

    def get_success_url(self):
        return reverse("descuento-especial-detail", kwargs={"pk":self.object.pk})


class DescuentoEspecialEditView(UpdateView):
    model = DescuentoEspecial
    fields = "__all__"

    template_name = descuento_templates + "edit.html"

    def get_success_url(self):
        return reverse("descuento-especial-detail", kwargs={"pk":self.object.pk})


class DescuentoEspecialDeleteView(DeleteView):
    model = DescuentoEspecial
    template_name = descuento_templates + "delete.html"
    success_url = reverse_lazy("descuento-especial")


def DescuentoEspecialFilterView(request):
    descuento_filter, page_obj = paginator_filter_view(request, DescuentoEspecial, DescuentoEspecialFilter)
    
    return render(request, descuento_templates + "filter.html", {"filter":descuento_filter, "object_list": page_obj})





# Becas
becas_templates = "gakusei/beca/"

class BecaListView(ListView):
    model = Becas
    paginate_by = 20
    template_name = becas_templates + "list.html"


class BecaDetailView(DetailView):
    model = Becas
    template_name = becas_templates + "detail.html"


class BecaCreateView(CreateView):
    model = Becas
    fields = "__all__"

    template_name = becas_templates + "create.html"

    def get_success_url(self):
        return reverse("becas-detail", kwargs={"pk":self.object.pk})
    

class BecaAssingView(CreateView):
    model = Becados
    fields = "__all__"

    template_name = becas_templates + "asignar.html"

    def get_success_url(self):
        return reverse("becas-detail", kwargs={"pk":self.object.beca.pk})


class BecaDeassingView(DeleteView):
    model = Becados

    template_name = becas_templates + "desasignar.html"

    def get_success_url(self):
        return reverse("becas-detail", kwargs={"pk":self.object.beca.pk})


def BecasFilterView(request):
    becas_filter, page_obj = paginator_filter_view(request, Becas, BecasFilter)
    
    return render(request, becas_templates + "filter.html", {"filter":becas_filter, "object_list": page_obj})

def BecadosFilterView(request):
    becados_filter, page_obj = paginator_filter_view(request, Becados, BecadosFilter)
    
    return render(request, becas_templates + "becados-filter.html", {"filter":becados_filter, "object_list": page_obj})



# API
def Api_RepresentantesGet(request):
    raw_list = Representante.objects.all()

    refined_list = []

    for r in raw_list:
        refined_list.append({
            "id" : r.id, "text" : r.full_name(),
        })

    response = {
        "results": refined_list,
    }

    return JsonResponse(response, status=201)



def Api_ClaseGet(request):

    if request.method != "POST":
        return JsonResponse({"error": "Use method POST."}, status=403)
    

    body = loads(request.body)
    pk = body.get("pk", False)


    if not pk:
        return JsonResponse({"error":"Id no enviado"}, status=400)


    clase = Clase.objects.filter(pk=pk).first()

    if clase:
        return JsonResponse(model_to_dict(clase), status=201)
    
    return JsonResponse({"error": "Clase no encontrada"}, status=404)



def Api_EstudianteGet(request):

    if request.method != "POST":
        return JsonResponse({"error": "Use method POST."}, status=403)
    

    body = loads(request.body)
    pk = body.get("pk", False)


    if not pk:
        return JsonResponse({"error":"Id no enviado"}, status=400)


    try:
        estudiante = Estudiante.objects.filter(pk=pk).first()
    except Estudiante.DoesNotExist:
        return JsonResponse({"error": "Estudiante no encontrado"}, status=404)




    if _ := estudiante.beca():
        beca = model_to_dict(_)
    else:
        beca = False

    if _ := estudiante.descuento():
        descuento = model_to_dict(_)
    else:
        descuento = False


    submit = {
        "estudiante": model_to_dict(estudiante),
        "beca": beca,
        "descuento": descuento,
    }

    
    return JsonResponse(submit, status=201)


def Api_AsistenciaForm(request):
    if request.method != "POST":
        return JsonResponse({"error": "Use method POST."}, status=403)
    

    body = loads(request.body)
    clase_id = body.get("pk", False)


    if not clase_id:
        return JsonResponse({"error":"Id no enviados"}, status=400)


    try:
        clase = Clase.objects.filter(pk=clase_id).first()
    except DiaDeClase.DoesNotExist:
        return JsonResponse({"error": "Clase no encontrado"}, status=404)
    

    estudiantes = Estudiante.objects.filter(inscripciones__clase=clase)

    estudiantes_data = []

    for e in estudiantes:
        estudiantes_data.append(dict(nombre_estudiante=e.full_name(), estudiante=e.pk))

    estudiantes_numero = clase.inscripciones.count()

    AsistenciaFormSet = modelformset_factory(Asistencias, form=AsistenciaForm, extra=estudiantes_numero, can_delete=False)

    formset = AsistenciaFormSet(
        initial=estudiantes_data,
        queryset=Asistencias.objects.none(),
    )

    h = AsistenciaFormsetHelper()

    dia_form = DiasForm()

    dia_form.fields["horario"].queryset = Horario.objects.filter(clase=clase).order_by("dia_semana")

    response = {
        "dias_form": render_crispy_form(dia_form),
        "formset": render_crispy_form(formset, h),
        "estudiantes_count": estudiantes_numero,
    }

    return JsonResponse(response, status=201)



def Api_AsistenciaFormRezagados(request):
    if request.method != "POST":
        return JsonResponse({"error": "Use method POST."}, status=403)
    

    body = loads(request.body)
    pk = body.get("pk", False)


    if not pk:
        return JsonResponse({"error":"Id no enviado"}, status=400)


    try:
        clase = Clase.objects.filter(pk=pk).first()
    except DiaDeClase.DoesNotExist:
        return JsonResponse({"error": "Clase no encontrado"}, status=404)
    
    
    dias = DiaDeClase.objects.filter(horario__clase=clase)

    if not dias:
        return JsonResponse({"error": "No hay Dias de Clases registradas para esta clase."}, status=400)
    

    estudiantes = Estudiante.objects.filter(inscripciones__clase=clase)

    form = AsistenciaRezagadosForm()

    form.fields["dia_clase"].queryset = dias
    form.fields["estudiante"].queryset = estudiantes


    return JsonResponse({"form":render_crispy_form(form)}, status=201)
    


# Obtiene las Clases a las cuales esta inscripto un estudiante.
def Api_Pagos_Clases(request):

    if request.method != "POST":
        return JsonResponse({"error": "Use method POST."}, status=403)
    

    body = loads(request.body)
    pk = body.get("pk", False)


    if not pk:
        return JsonResponse({"error":"Id no enviado"}, status=400)


    try:
        estudiante = Estudiante.objects.filter(pk=pk).first()
    except DiaDeClase.DoesNotExist:
        return JsonResponse({"error": "Estudiante no encontrado"}, status=404)
    

    clases = Clase.objects.filter(inscripciones__estudiante=estudiante)

    if clases:

        results = [
            {"id": c.id, "text": str(c)}
            for c in clases
        ]

        return JsonResponse({"results":results}, status=200)
    
    else:
        return JsonResponse({"error": "Estudiante no esta registrado en ninguna clase."}, status=404)


# Obtiene la mensualidad dado un estudiante y la clase
def Api_Pagos_Mensualidad(request):
    
    if request.method != "POST":
        return JsonResponse({"error": "Use method POST."}, status=403)
    

    body = loads(request.body)
    id_estudiante = body.get("estudiante", False)
    id_clase = body.get("clase", False)


    if not id_estudiante or not id_clase:
        return JsonResponse({"error":"Ids no enviados"}, status=400)
    

    try:
        inscripcion = Inscripciones.objects.filter(estudiante=id_estudiante, clase=id_clase).first()
    except Inscripciones.DoesNotExist:
        return JsonResponse({"error": "Inscripcion no encontrada"}, status=404)
    
    lista_solvencias = list(Solvencias.objects.filter(estudiante=id_estudiante, clase=id_clase).values("mes","pagado","monto_a_pagar","monto_abonado"))

    for s in lista_solvencias:
        s["mes"] = dateformat.format(s["mes"], "M. Y")
        s["monto_a_pagar"] = f"{s["monto_a_pagar"]}$"
        s["monto_abonado"] = f"{s["monto_abonado"]}$"

    solvencias = {
        "estudiante": str(inscripcion.estudiante),
        "solvencias": lista_solvencias,
    }

    return JsonResponse({"mensualidad":inscripcion.precio_a_pagar, "solvencias":solvencias}, status=200)




def Api_DiasDeClase_Form(request):
    if request.method != "POST":
        return JsonResponse({"error": "Use method POST."}, status=403)
    

    body = loads(request.body)
    clase_id = body.get("pk", False)


    if not clase_id:
        return JsonResponse({"error":"Id no enviado"}, status=400)


    try:
        clase = Clase.objects.filter(pk=clase_id).first()
    except Clase.DoesNotExist:
        return JsonResponse({"error": "Clase no encontrado"}, status=404)
    

    dia_form = DiasForm()
    dia_form.fields["horario"].queryset = Horario.objects.filter(clase=clase).order_by("dia_semana")


    return JsonResponse({"dias_form": render_crispy_form(dia_form)}, status=201)


def SolvenciaGenerator(request):
    from .solvencias_emails import solvencias_generator

    status, message = solvencias_generator()
    
    return JsonResponse({"status": status, "mensaje": message,})


def EmailSender(request):
    from .solvencias_emails import email_sender

    emails = email_sender()

    print(emails)

    return HttpResponse(emails)

class FacturaPagoDeleteView(DeleteView):
    model = FacturaPago
    template_name = "gakusei/myfactura/facturapago_confirm_delete.html"
    success_url = "/myfactura/"




