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


admin.site.register(Estudiante)
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
admin.site.register(FacturaPago)
