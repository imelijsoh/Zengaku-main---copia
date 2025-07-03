from django.db import models
from django.db import transaction

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

from django.utils.formats import date_format, time_format
from django.utils.safestring import mark_safe

import datetime
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta


# PERSONAS
class Persona(models.Model):

    class NACIONALITIES(models.TextChoices):
        VEN = ('V', 'Venezolano/a')
        EXT = ('E', 'Extranjero/a')

    nacionalidad = models.CharField(max_length=1, choices=NACIONALITIES, default=NACIONALITIES.VEN, db_default=NACIONALITIES.VEN)

    cedula = models.PositiveIntegerField(
        "Cédula",
        unique     = True,
        validators = [MinValueValidator(10000), MaxValueValidator(999999999)]
    )
    
    first_name  = models.CharField("Primer Nombre", max_length=255)
    middle_name	= models.CharField("Segundo Nombre", max_length=255, blank=True)
    last_name_1	= models.CharField("Primer Apellido", max_length=255)
    last_name_2 = models.CharField("Segundo Apellido", max_length=255, blank=True)
    
    personal_email = models.EmailField("Correo Personal", max_length=254)
    telefono  = models.CharField(
        "Teléfono Movil",
        max_length = 12,
        validators = [RegexValidator("^(0414|0424|0412|0416|0426)[-][0-9]{7}$", "El teléfono debe tener el formato 04XX-1234567")],
        help_text="Ej.: 0424-1234567",
    )

    def delete(self, *args, **kwargs):
        if self.cedula == 0:
            raise ValidationError("NO SE DEBE ELIMINAR ESTE REGISTRO")

        super().delete(*args, **kwargs)

    def full_name(self, apellido_primero=False):

        if apellido_primero:
            name = (self.last_name_1 + " ")

            if self.last_name_2:
                name += (self.last_name_2[0] + ". ")

            name += self.first_name

            if self.middle_name:
                name += (" " + self.middle_name[0]+".")
        
        else:
            name = (self.first_name + " ")

            if self.middle_name:
                name += (self.middle_name[0] + ". ")

            name += self.last_name_1

            if self.last_name_2:
                name += (" " + self.last_name_2[0]+".")

        return name

    def get_cedula(self):
        return f"{self.nacionalidad}{self.cedula:08}"
    
    def save(self, *args, **kwargs):
        self.personal_email = self.personal_email.lower()
        super().save(*args, **kwargs)

    def __str__(self):

        cedula = self.get_cedula()
        name   = self.full_name(apellido_primero=False)

        return f"{cedula} - {name}"


class Sensei(models.Model):

    class Meta:
        ordering = ["status", "personal_data__cedula"]

    class EN_Levels(models.TextChoices):
        A1 = "A1"
        A2 = "A2"
        B1 = "B1"
        B2 = "B2"
        C1 = "C1"
        C2 = "C2"

    class JP_Levels(models.TextChoices):
        N5 = "N5"
        N4 = "N4"
        N3 = "N3"
        N2 = "N2"
        N1 = "N1"

    class Status(models.TextChoices):
        ACTIVO  = "Activo"
        RETIRADO = "Retirado"

    personal_data = models.OneToOneField(Persona, on_delete=models.CASCADE, related_name="sensei")

    institucional_email = models.EmailField("Correo Institucional", max_length=254)
    EN_level = models.CharField("Nivel de Inglés", max_length=2, choices=EN_Levels, default=EN_Levels.B1)
    JP_level = models.CharField("Nivel de Japonés", max_length=2, choices=JP_Levels, default=JP_Levels.N4)

    status = models.CharField("Status", max_length=10, choices=Status, default=Status.ACTIVO)

    def full_name(self, apellido_primero=False):
        return self.personal_data.full_name(apellido_primero)
    
    def cedula(self):
        return self.personal_data.get_cedula()


    def clases_activas(self):
        return self.clases.filter(status=Clase.Status.ACTIVO)
    
    def clases_completadas(self):
        return self.clases.filter(status=Clase.Status.COMPLETADO)
    
    def clases_suspendidas_pausa(self):
        return self.clases.filter(status__in=[Clase.Status.SUSPENDIDO, Clase.Status.PAUSADO])


    def save(self, *args, **kwargs):
        self.institucional_email = self.institucional_email.lower()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.pk == 1:
            raise ValidationError("NO SE DEBE ELIMINAR ESTE REGISTRO")

        super().delete(*args, **kwargs)

    def __str__(self):
        return self.personal_data.__str__()


class Representante(models.Model):
    personal_data = models.OneToOneField(Persona, on_delete=models.CASCADE, related_name="representante")

    def full_name(self, apellido_primero=False):
        return self.personal_data.full_name(apellido_primero)
    
    def cedula(self):
        return self.personal_data.get_cedula()

    def __str__(self):
        return self.personal_data.__str__()


class Estudiante(models.Model):

    class Meta:
        ordering = ["status", "personal_data__cedula"]

    class Status(models.TextChoices):
        ACTIVO  = "Activo"
        RETIRADO = "Retirado"
        PAUSADO = "Pausado"
     

    personal_data = models.OneToOneField(Persona, on_delete=models.CASCADE, related_name="estudiante")
    representante = models.ForeignKey(Representante, blank=True, null=True, on_delete=models.SET_NULL, default=None)
    status = models.CharField("Status", max_length=10, choices=Status, default=Status.ACTIVO)

    def full_name(self, apellido_primero=False):
        return self.personal_data.full_name(apellido_primero)
    
    def cedula(self):
        return self.personal_data.get_cedula()
    
    def beca(self):
        try:
            return self._beca.beca
        except Estudiante._beca.RelatedObjectDoesNotExist:
            return False
        
    def descuento(self):
        try:
            return self._descuento
        except Estudiante._descuento.RelatedObjectDoesNotExist:
            return False



        

    def __str__(self):
        return self.personal_data.__str__()



# CLASES
class Curso(models.Model):
    modulo = models.CharField("Módulo", max_length=50, unique=True)

    def clases_activas(self):
        return self.clases.filter(status=Clase.Status.ACTIVO)
    
    def clases_completadas(self):
        return self.clases.filter(status=Clase.Status.COMPLETADO)
    
    def clases_suspendidas_pausa(self):
        return self.clases.filter(status__in=[Clase.Status.SUSPENDIDO, Clase.Status.PAUSADO])

    def __str__(self):
        return self.modulo


class Sede(models.Model):
    nombre = models.CharField(max_length=50)
    ubicacion = models.TextField("Ubicación")
    contacto = models.TextField("Formas de Contacto")

    # Usar el link (src) que viene en el iframe de insertar un mapa
    maps = models.URLField("Google Maps", max_length=500, blank=True, help_text="Usar el link (src) que viene en el iframe de insertar un mapa")

    def __str__(self):
        return self.nombre


class Clase(models.Model):

    class Meta:
        ordering = ["status", "f_inicio", "curso"]

    class Status(models.TextChoices):
        ACTIVO     = "Activa"
        PAUSADO    = "En Pausa"
        SUSPENDIDO = "Suspendida"
        COMPLETADO = "Terminada"

    def sensei_eliminado():
        s = Sensei.objects.get_or_create(
                personal_data = Persona.objects.get_or_create(
                                    pk=1,
                                    cedula="999999999",
                                    defaults={
                                        "nacionalidad":Persona.NACIONALITIES.VEN,
                                        "first_name":"REGISTRO",
                                        "last_name_1":"ELIMINADO",
                                        "personal_email":"REGISTRO@ELIMINADO.com",
                                        "telefono":"0424-0000000",
                                    }
                                )[0],
                defaults={
                    "pk" : 1,
                    "institucional_email" : "REGISTROELIMINADO@zengaku.com",
                    "status" : Sensei.Status.RETIRADO,
                }
            )[0]
        
        return s

    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name="clases")
    sensei = models.ForeignKey(Sensei, on_delete=models.SET(sensei_eliminado), related_name="clases")
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT, related_name="clases")

    f_inicio = models.DateTimeField("Fecha de Inicio")
    f_cierre = models.DateTimeField("Fecha de Cierre", blank=True, null=True)
    horas_semanales = models.PositiveSmallIntegerField("Horas Semanales")
    precio = models.PositiveSmallIntegerField("Precio ($)")

    individual = models.BooleanField("Clase Individual", default=False)

    status = models.CharField(max_length=10, choices=Status, default=Status.ACTIVO)

    def horarios(self):
        return self.horario.all().order_by("dia_semana")
    
    def dias_de_clase(self):
        return DiaDeClase.objects.filter(horario__in=self.horarios()).order_by("fecha")

    def __str__(self):
        sensei = self.sensei.personal_data.full_name()
        modulo = self.curso
        sede = self.sede
        fecha = date_format(self.f_inicio, 'M. Y')

        return f"{modulo} {sede} ({fecha}) - {sensei}"


class Horario(models.Model):

    class Meta:
        ordering = ["-clase", "hora_entrada"]

    class Weekdays(models.TextChoices):
        LUNES     = "Lunes"
        MARTES    = "Martes"
        MIERCOLES = "Miercoles"
        JUEVES    = "Jueves"
        VIERNES   = "Viernes"
        SABADO    = "Sábado"
        DOMINGO   = "Domingo"

    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, related_name="horario")

    dia_semana = models.CharField("Dia de la Semana", max_length=10, choices=Weekdays)
    hora_entrada = models.TimeField()
    hora_salida  = models.TimeField()

    def entrada(self):
        return time_format(self.hora_entrada, "f a")
    
    def salida(self):
        return time_format(self.hora_salida, "f a")
    
    def simplificado(self):
        dia = self.dia_semana
        entrada = self.hora_entrada
        salida = self.hora_salida

        return f"{dia} de {time_format(entrada, "f a")} a {time_format(salida, "f a")}"

    def __str__(self):
        clase = self.clase

        dia = self.dia_semana
        entrada = self.hora_entrada
        salida = self.hora_salida

        return f"{clase} - {dia} de {time_format(entrada, "f a")} a {time_format(salida, "f a")}"



class Inscripciones(models.Model):

    class Meta:
        ordering = ["clase", "precio_a_pagar"]
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"

        constraints = [
            models.UniqueConstraint(
                fields=["clase", "estudiante"],
                name="unique_inscripcion_clase_estudiante",
            )
        ]

    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, related_name="inscripciones")
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="inscripciones")
    precio_a_pagar = models.PositiveSmallIntegerField("Precio a pagar (en $)")

    def __str__(self):
        name = self.estudiante.personal_data.full_name()
        
        return f"{name} en clase {self.clase}"


# BECAS
class Becas(models.Model):
    class Meta:
        verbose_name_plural = "Becas"

    class TipoDescuento(models.TextChoices):
        PORCENTUAL = "Porcentual"
        CARDINAL   = "Cardinal"

    class Status(models.TextChoices):
        ACTIVO = "Activo"
        DESABILITADO = "Deshabilitado"

    nombre = models.CharField(max_length=200)
    descuento = models.PositiveSmallIntegerField()
    tipo_descuento = models.CharField(
        "Tipo de Descuento",
        max_length=10,
        choices=TipoDescuento,
        default=TipoDescuento.PORCENTUAL,
        help_text= mark_safe("<ul><li>PORCENTUAL: Descuento aplicado por porcentuaje. Ej.: 30%</li><li>CARDINAL: Descuento aplicado por una cantidad fija. Ej.: 20$</li></ul>")
    )
    status = models.CharField(max_length=15, choices=Status, default=Status.ACTIVO)

    def descuento_full(self):
        descuento = self.descuento
        tipo_descuento = "%" if self.tipo_descuento==self.TipoDescuento.PORCENTUAL else "$"

        return f"{descuento}{tipo_descuento}"

    def __str__(self):
        tipo = self.descuento_full()
        return f"{self.nombre} ({tipo})"


class Becados(models.Model):

    class Meta:
        verbose_name_plural = "Becados"

    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name="_beca")
    beca = models.ForeignKey(Becas, on_delete=models.CASCADE, related_name="becados")
    obs = models.TextField("Observaciones", blank=True)

    def __str__(self):
        estudiante = self.estudiante.personal_data.full_name()

        return f"{estudiante} becado con {self.beca.nombre}"


class DescuentoEspecial(models.Model):
    class Meta:
        verbose_name_plural = "Descuentos Especiales"

    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name="_descuento")
    # Este descuento siempre es Cardinal, no porcentual
    descuento = models.PositiveSmallIntegerField()
    obs = models.TextField("Observaciones", blank=True)

    def __str__(self):
        estudiante = self.estudiante.personal_data.full_name()

        return f"{estudiante} tiene un Descuento Especial de {self.descuento}$"



# PAGOS
class MetodosPagos(models.Model):
    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pagos"

    metodo = models.CharField("Método", max_length=255)
    datos = models.TextField("Datos de Pago")
    obs = models.TextField("Observaciones", blank=True)

    def __str__(self):
        return self.metodo


class Pagos(models.Model):

    class Meta:
        ordering = ["-fecha",]
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="pagos")
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, related_name="pagos")
    metodo = models.ForeignKey(MetodosPagos, on_delete=models.CASCADE, related_name="pagos")
    monto_pagado = models.PositiveSmallIntegerField(validators = [MinValueValidator(1)])
    referencia = models.CharField(max_length=255)
    fecha = models.DateTimeField("Fecha Registro de Pago", auto_now_add=True)
    fecha_pago = models.DateField("Fecha del Pago", default=now)
    obs = models.TextField("Observaciones", blank=True)

    def __str__(self):
        return f"{self.estudiante.personal_data.full_name()} pagó {self.monto_pagado}$ ({self.metodo.metodo}) para la clase {self.clase}"

    def clean(self):
        if self.estudiante.inscripciones.get(clase=self.clase).precio_a_pagar <= 0:
            raise ValidationError("El estudiante no necesita pagar mensualidad.")

        if not self.clase.inscripciones.filter(estudiante=self.estudiante).exists():
            raise ValidationError("El estudiante no está inscrito en esta clase.")
        
    def save(self, **kwargs):
        # Si skip_reparto=True, solo guarda el pago y NO reparte el abono automáticamente.
        # Esto permite que solo la lógica manual (vista de pagos detail) pueda desmarcar meses pagados.
        # El flujo automático de abonos desde el formulario de facturas solo afecta el mes seleccionado.
        skip_reparto = kwargs.pop('skip_reparto', False)
        if skip_reparto:
            super().save(**kwargs)
            return

        if not self.pk:
            with transaction.atomic():
                super().save(**kwargs)
            
                monto_pagado = self.monto_pagado
                mensualidad = self.estudiante.inscripciones.get(clase=self.clase).precio_a_pagar

                if mensualidad <= 0:
                    raise ValidationError("El estudiante no necesita pagar mensualidad.")
                

                monto_a_repartir = monto_pagado

                # Lista de meses anteriores SIN PAGAR o ABONADOS
                meses_pendientes = Solvencias.objects.filter(
                    estudiante=self.estudiante,
                    clase=self.clase
                ).exclude(pagado=Solvencias.Pagado.PAGADO).order_by("mes")


                # PAGOS DE MESES PENDIENTES
                for mes_pendiente in meses_pendientes:

                    if monto_a_repartir <= 0:
                        break

                    monto_faltante = mes_pendiente.monto_a_pagar - mes_pendiente.monto_abonado

                    if monto_a_repartir >= monto_faltante:
                        monto_a_repartir -= monto_faltante
                        mes_pendiente.monto_abonado += monto_faltante
                        mes_pendiente.pagado = Solvencias.Pagado.PAGADO
                        aplicado = monto_faltante

                    else:
                        mes_pendiente.monto_abonado += monto_a_repartir
                        aplicado = monto_a_repartir
                        monto_a_repartir = 0
                        mes_pendiente.pagado = Solvencias.Pagado.ABONADO


                    mes_pendiente.save()

                    Comprobantes.objects.create(
                        pagos=self,
                        solvencias=mes_pendiente,
                        monto_aplicado=aplicado,
                    )


                # PAGOS DE MESES POR ADELANTADO
                meses_pagados, monto_abonado = divmod(monto_a_repartir, mensualidad)

                # Meses enteros
                for mes in range(meses_pagados):
                    if mes_anterior := Solvencias.objects.filter(estudiante=self.estudiante, clase=self.clase).order_by("mes").last():
                        fecha_vieja = mes_anterior.mes
                        fecha_mes = fecha_vieja + relativedelta(months=+1, day=1)

                    else:
                        fecha_mes = self.clase.f_inicio + relativedelta(day=1)

                    solvencia_full = Solvencias.objects.create(
                        estudiante=self.estudiante,
                        clase=self.clase,
                        mes=fecha_mes,
                        pagado=Solvencias.Pagado.PAGADO,
                        monto_a_pagar=mensualidad,
                        monto_abonado=mensualidad,
                    )

                    Comprobantes.objects.create(
                        pagos=self,
                        solvencias=solvencia_full,
                        monto_aplicado=mensualidad,
                    )

                # Mes sobrante (abonado)
                if monto_abonado:
                    if mes_anterior := Solvencias.objects.filter(estudiante=self.estudiante, clase=self.clase).order_by("mes").last():
                        fecha_vieja = mes_anterior.mes
                        fecha_mes = fecha_vieja + relativedelta(months=+1, day=1)

                    else:
                        fecha_mes = self.clase.f_inicio + relativedelta(day=1)

                    solvencia_abonado = Solvencias.objects.create(
                        estudiante=self.estudiante,
                        clase=self.clase,
                        mes=fecha_mes,
                        pagado=Solvencias.Pagado.ABONADO,
                        monto_a_pagar=mensualidad,
                        monto_abonado=monto_abonado,
                    )

                    Comprobantes.objects.create(
                        pagos=self,
                        solvencias=solvencia_abonado,
                        monto_aplicado=monto_abonado,
                    )

        else:
            super().save(**kwargs)
            
    def delete(self, *args, **kwargs):
        # Revertir solvencias y comprobantes antes de eliminar el pago
        from .models import Solvencias, Comprobantes
        # 1. Eliminar comprobantes asociados a este pago y revertir solvencias
        for comprobante in self.comprobantes.all():
            solvencia = comprobante.solvencias
            # Restar el monto aplicado de la solvencia
            if solvencia:
                solvencia.monto_abonado = max(0, solvencia.monto_abonado - comprobante.monto_aplicado)
                # Si el abono baja a 0, marcar como Sin Pagar
                if solvencia.monto_abonado == 0:
                    solvencia.pagado = Solvencias.Pagado.SIN_PAGAR
                # Si el abono es menor al monto a pagar, marcar como Abonado
                elif solvencia.monto_abonado < solvencia.monto_a_pagar:
                    solvencia.pagado = Solvencias.Pagado.ABONADO
                # Si el abono es igual o mayor, marcar como Pagado
                else:
                    solvencia.pagado = Solvencias.Pagado.PAGADO
                solvencia.save()
            comprobante.delete()
        # 2. Eliminar el pago
        super().delete(*args, **kwargs)


class Solvencias(models.Model):
    class Meta:
        ordering = ["clase__status", "clase__f_inicio", "clase__curso"]
        verbose_name = "Solvencia"
        verbose_name_plural = "Solvencias"

        constraints = [
            models.UniqueConstraint(
                fields=["estudiante", "clase", "mes"],
                name="unique_mes_solvencia",
            )
        ]

    class Pagado(models.TextChoices):
        PAGADO    = "Pagado"
        ABONADO   = "Abonado"
        SIN_PAGAR = "Sin Pagar"

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="solvencias")
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, related_name="solvencias")

    # En el mes se guardaran principalmente el Año y el Mes, el Dia siempre sera 1.
    mes = models.DateField()
    
    pagado = models.CharField(max_length=10, choices=Pagado, default=Pagado.SIN_PAGAR)

    # Monto a pagar se obtiene de Inscripciones
    monto_a_pagar = models.PositiveSmallIntegerField()
    monto_abonado = models.PositiveSmallIntegerField(default=0)
    obs = models.TextField("Observaciones", blank=True)

    def clean(self):
        if not self.clase.inscripciones.filter(estudiante=self.estudiante).exists():
            raise ValidationError("El estudiante no está inscrito en esta clase.")
        
        if self.mes.day != 1:
            self.mes = self.mes.replace(day=1)
        
    def __str__(self):
        return f"{self.estudiante.personal_data.full_name()} a {self.pagado} el mes {self.mes.month} de la clase {self.clase}"
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Comprobantes(models.Model):
    class Meta:
        verbose_name = "Comprobante"
        verbose_name_plural = "Comprobantes"

    pagos = models.ForeignKey(Pagos, on_delete=models.CASCADE, related_name="comprobantes")
    solvencias = models.ForeignKey(Solvencias, on_delete=models.CASCADE, related_name="comprobantes")

    monto_aplicado = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.pagos} - {self.solvencias} ({self.monto_aplicado}$)"



# ASISTENCIAS
class DiaDeClase(models.Model):

    class Meta:
        ordering = ["-fecha"]

    class Status(models.TextChoices):
        IMPARTIDA  = "Impartida"
        SUSPENDIDA = "Suspendida"
        CANCELADA  = "Cancelada"

    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name="dias_de_clase")
    numero = models.PositiveSmallIntegerField("Número de Clase")
    fecha = models.DateField()
    status = models.CharField(max_length=10, choices=Status, default=Status.IMPARTIDA)
    obs = models.TextField("Observaciones", blank=True)

    def clase(self):
        return self.horario.clase

    def simple_str(self):
        return f"Clase N° {self.numero} ({self.status}) - {date_format(self.fecha, 'D d M, Y')}"

    def __str__(self):
        # Clase N. {} - ZGN5 Altamira - Mika Ruft 

        return f"Clase N° {self.numero} {self.horario.clase} ({self.status}) - {date_format(self.fecha, 'D d M, Y')}"



class Asistencias(models.Model):
    
    dia_clase = models.ForeignKey(DiaDeClase, on_delete=models.CASCADE, related_name="asistencias")
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="asistencias")
    presente = models.BooleanField(default=False)

    class Meta:
        ordering = ["dia_clase"]
        verbose_name_plural = "Asistencias"

        constraints = [
            # models.UniqueConstraint(
            #     fields=["dia_clase", "estudiante"],
            #     name="unique_asistencia_estudiante",
            # )
        ]
    
    def clean(self):
        # Estudiante no Inscripto en la Clase
        if not self.dia_clase.horario.clase.inscripciones.filter(estudiante=self.estudiante).exists():
            raise ValidationError("El estudiante no está inscrito en esta clase.")
        
        # Estudiante ya Asistió al Dia de Clase
        if Asistencias.objects.filter(dia_clase=self.dia_clase, estudiante=self.estudiante).exclude(pk=self.pk).exists():
            raise ValidationError(f"El estudiante {self.estudiante.personal_data.full_name()} ya asistió a este Dia de Clase: {self.dia_clase}")
        

        
    def __str__(self):
        name = self.estudiante.personal_data.full_name()

        presente = "presente".upper() if self.presente else "no presente".upper()

        return f"{self.dia_clase} - {name} ({presente})"


class FacturaPago(models.Model):
    issued_by = models.CharField("Emitido por", max_length=100)
    student_name = models.CharField("Nombre del estudiante", max_length=100)
    student_id = models.CharField("Cédula", max_length=20)
    amount = models.DecimalField("Monto", max_digits=10, decimal_places=5)
    reference_code = models.CharField("Código de referencia", max_length=50)
    payment_date = models.DateField("Fecha de pago")
    payment_method = models.CharField("Método de pago", max_length=50)
    payment_concept = models.CharField("Concepto de pago", max_length=200)
    email = models.EmailField("Correo electrónico")
    emitted_by = models.CharField("Emitido por (extra)", max_length=100, blank=True, null=True)
    month = models.CharField("Mes cancelado", max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Factura de {self.student_name} ({self.amount}$, {self.payment_date})"
