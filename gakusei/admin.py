from django.contrib import admin

from .models import Persona, Sensei, Estudiante, Representante
from .models import Curso, Sede, Clase, Horario, Inscripciones
from .models import DiaDeClase, Asistencias
from .models import Becas, Becados, DescuentoEspecial
from .models import MetodosPagos, Pagos, Solvencias, Comprobantes

from django.db.models import Value
from django.db.models.functions import Concat
from .models import FacturaPago

# Register your models here.

# Personas
# admin.site.register(Persona)

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ["cedula", "last_name_1", "first_name", "telefono", "personal_email"]

# admin.site.register(Sensei)

@admin.register(Sensei)
class SenseiAdmin(admin.ModelAdmin):
    list_display = ["cedula", "full_name", "telefono", "institucional_email", "EN_level", "JP_level"]
    ordering = ["personal_data__last_name_1"]

    @admin.display(
        description = "Cédula",
        ordering = "personal_data__cedula",
    )
    def cedula(self, obj):
        return obj.personal_data.cedula
    

    @admin.display(
        description = "Nombre Completo",
        ordering    = Concat("personal_data__last_name_1", Value(" "), "personal_data__first_name"),
    )
    def full_name(self, obj):
        return obj.personal_data.full_name(apellido_primero=True)
    

    @admin.display(
        description = "Teléfono",
        ordering    = "personal_data__telefono",
    )
    def telefono(self, obj):
        return obj.personal_data.telefono


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ["cedula", "full_name", "status", "telefono", "personal_email"]
    list_filter = ["status"]
    search_fields = [
        "personal_data__first_name", 
        "personal_data__last_name_1", 
        "personal_data__cedula",
        "personal_data__personal_email"
    ]
    ordering = ["personal_data__last_name_1"]

    @admin.display(
        description="Cédula",
        ordering="personal_data__cedula",
    )
    def cedula(self, obj):
        return obj.cedula()

    @admin.display(
        description="Nombre Completo",
        ordering=Concat("personal_data__last_name_1", Value(" "), "personal_data__first_name"),
    )
    def full_name(self, obj):
        return obj.full_name(apellido_primero=True)

    @admin.display(
        description="Teléfono",
        ordering="personal_data__telefono",
    )
    def telefono(self, obj):
        return obj.personal_data.telefono

    @admin.display(
        description="Correo Personal",
        ordering="personal_data__personal_email",
    )
    def personal_email(self, obj):
        return obj.personal_data.personal_email

admin.site.register(Representante)

# Clases
admin.site.register(Curso)
admin.site.register(Sede)
admin.site.register(Clase)
admin.site.register(Horario)
admin.site.register(Inscripciones)

# Asistencias

@admin.register(DiaDeClase)
class DiaDeClaseAdmin(admin.ModelAdmin):
    # date_hierarchy = "fecha"
    # list_display = ["fecha", 'status']
    ordering = ["-fecha"]

admin.site.register(Asistencias)


# Becas

admin.site.register(Becas)
admin.site.register(Becados)
admin.site.register(DescuentoEspecial)


# Pagos
admin.site.register(MetodosPagos)
admin.site.register(Solvencias)
admin.site.register(Comprobantes)
admin.site.register(Pagos)

# facturapago
@admin.register(FacturaPago)
class FacturaPagoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_student_name',
        'get_student_id',
        'get_email',
        'amount',
        'reference_code',
        'payment_date',
        'payment_method',
        'payment_concept',
        'emitted_by',
        'month',
    ]
    fields = [
        'issued_by',
        'estudiante',
        'amount',
        'reference_code',
        'payment_date',
        'payment_method',
        'payment_concept',
        'emitted_by',
        'month',
    ]
    search_fields = ['estudiante__personal_data__first_name', 'estudiante__personal_data__last_name_1', 'estudiante__personal_data__cedula']
    autocomplete_fields = ['estudiante']

    @admin.display(description="Nombre del estudiante")
    def get_student_name(self, obj):
        return obj.get_student_name()

    @admin.display(description="Cédula")
    def get_student_id(self, obj):
        return obj.get_student_id()

    @admin.display(description="Correo electrónico")
    def get_email(self, obj):
        return obj.get_email()
