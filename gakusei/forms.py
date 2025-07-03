from django import forms

from django.db import transaction, IntegrityError

from .models import Persona, Sensei, Estudiante, Representante, DiaDeClase, Asistencias, Clase, Pagos


from crispy_forms.helper import FormHelper

from crispy_forms.layout import Layout, Div, Field

import datetime
from django import forms

# factura

class PaymentForm(forms.Form):
    issued_by = forms.CharField(label='Emitido por', max_length=100)
    student_name = forms.CharField(label='Nombre del estudiante', max_length=100)
    student_id = forms.CharField(label='Cédula', max_length=20)
    amount = forms.DecimalField(label='Monto', max_digits=10, decimal_places=5)
    reference_code = forms.CharField(label='Código de referencia', max_length=50)
    payment_date = forms.DateField(
        label='Fecha', 
        widget=forms.SelectDateWidget(
            months={
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
                7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }
        )
    )
    payment_method = forms.ChoiceField(label='Método de pago', choices=[
        ('efectivo', 'Efectivo'),
        ('zelle', 'Zelle'),
        ('payPal', 'PayPal'),
        ('pagoMovil', 'Pago Móvil')
    ])
    payment_concept = forms.CharField(label='Concepto de pago', max_length=200)
    email = forms.EmailField(label='Correo electrónico')
    emitted_by = forms.CharField(label='Emitido por (extra)', max_length=100, required=False)
    MONTH_CHOICES = [
        ("Enero", "Enero"),
        ("Febrero", "Febrero"),
        ("Marzo", "Marzo"),
        ("Abril", "Abril"),
        ("Mayo", "Mayo"),
        ("Junio", "Junio"),
        ("Julio", "Julio"),
        ("Agosto", "Agosto"),
        ("Septiembre", "Septiembre"),
        ("Octubre", "Octubre"),
        ("Noviembre", "Noviembre"),
        ("Diciembre", "Diciembre"),
    ]
    month = forms.ChoiceField(label='Mes cancelado', choices=MONTH_CHOICES, required=True)



# persona
class BasePersona:
    """Mixin para Campo de PersonalData. Colocar en los argumentos de las clases de primero al definir la clase."""

    def __init__(self, *args, **kwargs):

        self.instance = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)


        self.fields["nacionalidad"] = forms.ChoiceField(
            choices=Persona.NACIONALITIES,
            initial=Persona.NACIONALITIES.VEN,
            widget=forms.RadioSelect(),
            required=True,
        )

        self.fields["cedula"] = forms.IntegerField(
            label="Cédula",
            min_value=10000,
            max_value=999999999,
            widget=forms.NumberInput(attrs={"autofocus":True}),
        )
        
        self.fields["first_name"]   = forms.CharField(label="Primer Nombre", max_length=255)
        self.fields["middle_name"]	= forms.CharField(label="Segundo Nombre", max_length=255, required=False)
        self.fields["last_name_1"]	= forms.CharField(label="Primer Apellido", max_length=255)
        self.fields["last_name_2"]  = forms.CharField(label="Segundo Apellido", max_length=255, required=False)

        self.fields["telefono"] = forms.RegexField(
            label="Teléfono Movil", 
            max_length=12, 
            regex=r"^(0414|0424|0412|0416|0426)[-][0-9]{7}$",
            widget=forms.TextInput(attrs={"type":"tel"}),
            help_text="Ej.: 0424-1234567",
        )

        self.fields["personal_email"] = forms.EmailField(label="Correo Personal", max_length=254)

        self.order_fields()


    # Reorganiza los campos para que los de Personal_Data siempre esten al incio
    def order_fields(self, *args, **kwargs):

        # Obtenemos los campos de Persona, pero solo los q son "verdaderos" campos
        personal_data_fields = [field.name for field in Persona._meta.get_fields() if field.concrete]

        # Re-declaracion porque con la primera no funciona
        personal_data_fields = [field for field in personal_data_fields if field in self.fields]

        # Obtener los demás campos en su orden original
        other_fields = [field for field in self.fields if field not in personal_data_fields]

        # Aplicamos el Nuevo Orden
        ordered_fields = personal_data_fields + other_fields

        # Redifinimos la variable de los campor con el nuevo orden
        self.fields = {field: self.fields[field] for field in ordered_fields}



    def clean_cedula(self):
        ci = self.cleaned_data["cedula"]

        personal_data    = getattr(self.instance, "personal_data", None)
        personal_data_id = getattr(personal_data, "pk", None)

        if Persona.objects.filter(cedula=ci).exclude(pk=personal_data_id).exists():
            self.add_error("cedula", "Esta cédula ya está registrada.") 

        return ci


# class SenseiForm(BasePersona, forms.Form):
    
#     institucional_email = forms.EmailField(label="Correo Institucional", max_length=254)

#     status = forms.ChoiceField(
#         choices=Sensei.Status,
#         widget=forms.RadioSelect(),
#         initial=Sensei.Status.ACTIVO,
#         required=True,
#     )

#     EN_level = forms.ChoiceField(
#         label="Nivel de Inglés",
#         choices=Sensei.EN_Levels,
#         widget=forms.RadioSelect(),
#         required=True,
#     )

#     JP_level = forms.ChoiceField(
#         label="Nivel de Japonés",
#         choices=Sensei.JP_Levels,
#         widget=forms.RadioSelect(),
#         required=True,
#     )

#     def save(self, commit=True):
#         try:
#             with transaction.atomic():
                
#                 personal_data = Persona.objects.create(
#                     nacionalidad = self.cleaned_data.get("nacionalidad"),
#                     cedula = self.cleaned_data.get("cedula"),
#                     first_name = self.cleaned_data.get("first_name"),
#                     middle_name = self.cleaned_data.get("middle_name"),
#                     last_name_1 = self.cleaned_data.get("last_name_1"),
#                     last_name_2 = self.cleaned_data.get("last_name_2"),
#                     personal_email = self.cleaned_data.get("personal_email"),
#                     telefono = self.cleaned_data.get("telefono"),
#                 )

#                 sensei = Sensei.objects.create(
#                     personal_data = personal_data,
#                     institucional_email = self.cleaned_data.get("institucional_email"),
#                     EN_level = self.cleaned_data.get("EN_level"),
#                     JP_level = self.cleaned_data.get("JP_level"),
#                     status = self.cleaned_data.get("status"),
#                 )

#         except Exception as e:
#             self.add_error(None, f"Error al insertar datos en BDD: {e}")

#         return sensei
    

#     def update(self, commit=True):

#         # try:
#         #     with transaction.atomic():
                
#         #         personal_data = Persona.objects.create(
#         #             nacionalidad = self.cleaned_data.get("nacionalidad"),
#         #             cedula = self.cleaned_data.get("cedula"),
#         #             first_name = self.cleaned_data.get("first_name"),
#         #             middle_name = self.cleaned_data.get("middle_name"),
#         #             last_name_1 = self.cleaned_data.get("last_name_1"),
#         #             last_name_2 = self.cleaned_data.get("last_name_2"),
#         #             personal_email = self.cleaned_data.get("personal_email"),
#         #             telefono = self.cleaned_data.get("telefono"),
#         #         )

#         #         sensei = Sensei.objects.create(
#         #             personal_data = personal_data,
#         #             institucional_email = self.cleaned_data.get("institucional_email"),
#         #             EN_level = self.cleaned_data.get("EN_level"),
#         #             JP_level = self.cleaned_data.get("JP_level"),
#         #             status = self.cleaned_data.get("status"),
#         #         )

#         # except Exception as e:
#         #     self.add_error(None, f"Error al insertar datos en BDD: {e}")

#         print("updateado")

#         return "yes"

class SenseiForm(BasePersona, forms.ModelForm):

    class Meta:
        model = Sensei
        fields = ["institucional_email", "status", "EN_level", "JP_level"]
        widgets = {
            "status":   forms.RadioSelect(),
            "EN_level": forms.RadioSelect(),
            "JP_level": forms.RadioSelect(),
        }


    # Pegamos los datos "extras" (personal_data) a los campos del mixin.
    def __init__(self, *args, **kwargs):

        # Tomamos 'personal_data' de los datos entrantes (cuando se hace un Update)
        personal_data = kwargs.pop("personal_data", None)

        # Inicializamos el formulario
        super().__init__(*args, **kwargs)

        # Pegamos los datos en los campos del formulario recien inicializado
        if personal_data:
            self.fields["nacionalidad"].initial =   personal_data.get("nacionalidad", "")
            self.fields["cedula"].initial =         personal_data.get("cedula", "")
            self.fields["first_name"].initial =     personal_data.get("first_name", "")
            self.fields["middle_name"].initial =    personal_data.get("middle_name", "")
            self.fields["last_name_1"].initial =    personal_data.get("last_name_1", "")
            self.fields["last_name_2"].initial =    personal_data.get("last_name_2", "")
            self.fields["telefono"].initial =       personal_data.get("telefono", "")
            self.fields["personal_email"].initial = personal_data.get("personal_email", "")


    def save(self, commit=True):

        # Get Sensei PK or None
        sensei_id = getattr(self.instance, "pk", None)

        # Get Personal Data PK or None
        _personal_data   = getattr(self.instance, "personal_data", None)
        personal_data_id = getattr(_personal_data, "pk", None)

        print(personal_data_id)

        try:
            with transaction.atomic():

                personal_data, pd_creado = Persona.objects.update_or_create(
                    pk = personal_data_id,
                    defaults={
                        "nacionalidad"   : self.cleaned_data.get("nacionalidad"),
                        "cedula"         : self.cleaned_data.get("cedula"),
                        "first_name"     : self.cleaned_data.get("first_name"),
                        "middle_name"    : self.cleaned_data.get("middle_name"),
                        "last_name_1"    : self.cleaned_data.get("last_name_1"),
                        "last_name_2"    : self.cleaned_data.get("last_name_2"),
                        "personal_email" : self.cleaned_data.get("personal_email"),
                        "telefono"       : self.cleaned_data.get("telefono"),
                    }
                )


                sensei, s_creado = Sensei.objects.update_or_create(
                    pk = sensei_id,
                    defaults={
                        "personal_data"         : personal_data,
                        "institucional_email"   : self.cleaned_data.get("institucional_email"),
                        "EN_level"              : self.cleaned_data.get("EN_level"),
                        "JP_level"              : self.cleaned_data.get("JP_level"),
                        "status"                : self.cleaned_data.get("status"),
                    }
                )

        except Exception as e:
            self.add_error(None, f"Error al insertar datos en BDD: {e}")
            return None

        return sensei
    

    





class EstudianteForm(BasePersona, forms.ModelForm):

    class Meta:
        model = Estudiante
        exclude = ["personal_data"]
        widgets = {
            "status": forms.RadioSelect(),
        }


    # Pegamos los datos "extras" (personal_data) a los campos del mixin.
    def __init__(self, *args, **kwargs):
        personal_data = kwargs.pop("personal_data", None)
        super().__init__(*args, **kwargs)

        if personal_data:
            self.fields["nacionalidad"].initial   =  personal_data.get("nacionalidad", "")
            self.fields["cedula"].initial         =  personal_data.get("cedula", "")
            self.fields["first_name"].initial     =  personal_data.get("first_name", "")
            self.fields["middle_name"].initial    =  personal_data.get("middle_name", "")
            self.fields["last_name_1"].initial    =  personal_data.get("last_name_1", "")
            self.fields["last_name_2"].initial    =  personal_data.get("last_name_2", "")
            self.fields["telefono"].initial       =  personal_data.get("telefono", "")
            self.fields["personal_email"].initial =  personal_data.get("personal_email", "")


    def save(self, commit=True):

        estudiante_id = getattr(self.instance, "pk", None)

        _personal_data = getattr(self.instance, "personal_data", None)
        personal_data_id = getattr(_personal_data, "pk", None)

        try:
            with transaction.atomic():
                
                personal_data, pd_creado = Persona.objects.update_or_create(
                    pk = personal_data_id,
                    defaults={
                        "nacionalidad"   : self.cleaned_data.get("nacionalidad"  ),
                        "cedula"         : self.cleaned_data.get("cedula"        ),
                        "first_name"     : self.cleaned_data.get("first_name"    ),
                        "middle_name"    : self.cleaned_data.get("middle_name"   ),
                        "last_name_1"    : self.cleaned_data.get("last_name_1"   ),
                        "last_name_2"    : self.cleaned_data.get("last_name_2"   ),
                        "personal_email" : self.cleaned_data.get("personal_email"),
                        "telefono"       : self.cleaned_data.get("telefono"      ),
                    }
                )

                estudiante, s_creado = Estudiante.objects.update_or_create(
                    pk = estudiante_id,
                    defaults={
                        "personal_data" : personal_data,
                        "representante" : self.cleaned_data.get("representante"),
                        "status"        : self.cleaned_data.get("status"),
                    }
                )

        except Exception as e:
            self.add_error(None, f"Error al insertar datos en BDD: {e}")
            return None

        return estudiante



class RepresentanteForm(BasePersona, forms.Form):
    
    def save(self, commit=True):

        try:
            with transaction.atomic():
                
                personal_data = Persona.objects.create(
                    nacionalidad    = self.cleaned_data.get("nacionalidad"),
                    cedula          = self.cleaned_data.get("cedula"),
                    first_name      = self.cleaned_data.get("first_name"),
                    middle_name     = self.cleaned_data.get("middle_name"),
                    last_name_1     = self.cleaned_data.get("last_name_1"),
                    last_name_2     = self.cleaned_data.get("last_name_2"),
                    personal_email  = self.cleaned_data.get("personal_email"),
                    telefono        = self.cleaned_data.get("telefono"),
                )

                representante = Representante.objects.create(
                    personal_data = personal_data,
                )

        except Exception as e:
            self.add_error(None, f"Error al insertar datos en BDD: {e}")

        return representante



class SeleccionAsistenciaForm(forms.Form):

    clase = forms.ModelChoiceField(Clase.objects.filter(status=Clase.Status.ACTIVO))


class DiasForm(forms.ModelForm):
    class Meta:
        model = DiaDeClase
        fields = "__all__"
        widgets = {
            "fecha": forms.DateInput(attrs={"type":"date"}),
            "status": forms.RadioSelect(),
        }


class AsistenciaForm(forms.ModelForm):

    nombre_estudiante = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={"readonly":True}))

    class Meta:
        model = Asistencias
        fields = ["nombre_estudiante", "presente", "estudiante","dia_clase"]
        widgets = {
            "nombre_estudiante": forms.TextInput(attrs={"readonly":True}),
            "estudiante": forms.HiddenInput(attrs={"readonly":True,}),
            "dia_clase": forms.HiddenInput(attrs={"readonly":True}),
        }
        labels = {
            "nombre_estudiante": "",
        }
        


class AsistenciaFormsetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(AsistenciaFormsetHelper, self).__init__(*args, **kwargs)
        self.layout = Layout(
            Div(
                Field('nombre_estudiante', wrapper_class='me-auto flex-grow-1'),
                Field('presente',          wrapper_class='mx-auto ps-5 pe-3'),  
                Field('estudiante'),  
                Field('dia_clase'),  
                css_class='d-flex align-items-baseline'
            ) 
        )
        


class AsistenciaRezagadosForm(forms.ModelForm):

    class Meta:
        model = Asistencias
        exclude = []
        help_texts = {
            "presente": "Seleccionado: Presente, Sin seleccionar: No Presente",
        }

    
class ClaseForm(forms.ModelForm):
    # Campos separados para fecha y hora
    fecha_inicio = forms.DateField(
        label="Fecha de Inicio",
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    hora_inicio = forms.TimeField(
        label="Hora de Inicio",
        required=True,
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        }),
        help_text="Seleccione la hora de inicio de la clase"
    )
    fecha_cierre = forms.DateField(
        label="Fecha de Cierre",
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    hora_cierre = forms.TimeField(
        label="Hora de Finalización",
        required=False,
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        }),
        help_text="Seleccione la hora de finalización de la clase"
    )

    class Meta:
        model = Clase
        fields = ['curso', 'sensei', 'sede', 'horas_semanales', 'precio', 'individual', 'status']
        widgets = {
            'curso': forms.Select(attrs={'class': 'form-control'}),
            'sensei': forms.Select(attrs={'class': 'form-control'}),
            'sede': forms.Select(attrs={'class': 'form-control'}),
            'horas_semanales': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'individual': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            # Si estamos editando una clase existente, separamos la fecha y hora
            initial = kwargs.get('initial', {})
            if instance.f_inicio:
                initial['fecha_inicio'] = instance.f_inicio.date()
                initial['hora_inicio'] = instance.f_inicio.time()
            if instance.f_cierre:
                initial['fecha_cierre'] = instance.f_cierre.date()
                initial['hora_cierre'] = instance.f_cierre.time()
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        # Obtener los campos de fecha y hora
        fecha_inicio = cleaned_data.get('fecha_inicio')
        hora_inicio = cleaned_data.get('hora_inicio')
        fecha_cierre = cleaned_data.get('fecha_cierre')
        hora_cierre = cleaned_data.get('hora_cierre')

        print("DEBUG - Datos limpios:", cleaned_data)
        print("DEBUG - Fecha inicio:", fecha_inicio)
        print("DEBUG - Hora inicio:", hora_inicio)

        # Validar que tengamos tanto fecha como hora de inicio
        if not fecha_inicio:
            self.add_error('fecha_inicio', 'La fecha de inicio es requerida')
        if not hora_inicio:
            self.add_error('hora_inicio', 'La hora de inicio es requerida')

        # Si tenemos fecha de cierre, requerimos hora de cierre y viceversa
        if fecha_cierre and not hora_cierre:
            self.add_error('hora_cierre', 'Si especifica fecha de cierre, debe especificar hora de cierre')
        elif hora_cierre and not fecha_cierre:
            self.add_error('fecha_cierre', 'Si especifica hora de cierre, debe especificar fecha de cierre')

        # Si tenemos todos los datos necesarios, combinar fecha y hora
        if fecha_inicio and hora_inicio:
            try:
                cleaned_data['f_inicio'] = datetime.datetime.combine(fecha_inicio, hora_inicio)
                print("DEBUG - f_inicio combinado:", cleaned_data['f_inicio'])
            except Exception as e:
                print("DEBUG - Error al combinar f_inicio:", str(e))
                self.add_error(None, f"Error al procesar la fecha y hora de inicio: {str(e)}")

        if fecha_cierre and hora_cierre:
            try:
                cleaned_data['f_cierre'] = datetime.datetime.combine(fecha_cierre, hora_cierre)
                print("DEBUG - f_cierre combinado:", cleaned_data['f_cierre'])
                # Validar que la fecha/hora de cierre sea posterior a la de inicio
                if cleaned_data['f_cierre'] <= cleaned_data['f_inicio']:
                    raise forms.ValidationError("La fecha y hora de finalización debe ser posterior a la fecha y hora de inicio.")
            except Exception as e:
                print("DEBUG - Error al combinar f_cierre:", str(e))
                self.add_error(None, f"Error al procesar la fecha y hora de cierre: {str(e)}")

        return cleaned_data

    def save(self, commit=True):
        try:
            instance = super().save(commit=False)
            print("DEBUG - Guardando instancia...")
            
            # Asignar los valores combinados de fecha y hora
            if self.cleaned_data.get('fecha_inicio') and self.cleaned_data.get('hora_inicio'):
                instance.f_inicio = datetime.datetime.combine(
                    self.cleaned_data['fecha_inicio'],
                    self.cleaned_data['hora_inicio']
                )
                print("DEBUG - f_inicio asignado:", instance.f_inicio)
            
            if self.cleaned_data.get('fecha_cierre') and self.cleaned_data.get('hora_cierre'):
                instance.f_cierre = datetime.datetime.combine(
                    self.cleaned_data['fecha_cierre'],
                    self.cleaned_data['hora_cierre']
                )
                print("DEBUG - f_cierre asignado:", instance.f_cierre)
            
            if commit:
                instance.save()
                print("DEBUG - Instancia guardada exitosamente")
            return instance
        except Exception as e:
            print("DEBUG - Error al guardar:", str(e))
            raise

class PagosForm(forms.ModelForm):
    class Meta:
        model = Pagos
        fields = '__all__'