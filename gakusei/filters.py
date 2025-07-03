from .models import Sensei, Estudiante, Clase, Horario, Inscripciones, DiaDeClase, Pagos, MetodosPagos, DescuentoEspecial, Becas, Becados
from django import forms
import django_filters

from django.db.models import Value, CharField
from django.db.models.functions import Concat
from django.db.models import Q

class SenseiFilter(django_filters.FilterSet):
    class Meta:
        model = Sensei
        
        fields = ["status","personal_data__cedula", "nombres", "apellidos", "personal_data__telefono", "personal_data__personal_email", "institucional_email", "EN_level", "JP_level",] 

    status = django_filters.ChoiceFilter(choices=Sensei.Status , widget=forms.RadioSelect, empty_label="Cualquier Status")
    JP_level = django_filters.ChoiceFilter(choices=Sensei.JP_Levels , widget=forms.RadioSelect, empty_label="Cualquier Nivel")
    EN_level = django_filters.ChoiceFilter(choices=Sensei.EN_Levels , widget=forms.RadioSelect, empty_label="Cualquier Nivel")

    personal_data__cedula           = django_filters.NumberFilter(lookup_expr="icontains", label="Cédula", widget=forms.NumberInput(attrs={"max":"999999999", "step":1}))
    personal_data__personal_email   = django_filters.CharFilter(lookup_expr="icontains",   label="Correo Personal",      widget=forms.EmailInput)
    personal_data__telefono         = django_filters.CharFilter(lookup_expr="icontains",   label="Telefono Movil",       widget=forms.TextInput(attrs={"type":"tel", "maxlength":12}))
    institucional_email             = django_filters.CharFilter(lookup_expr="icontains",   label="Correo Institucional", widget=forms.EmailInput)

    nombres = django_filters.CharFilter(method="filter_nombres", label="Nombres")
    apellidos = django_filters.CharFilter(method="filter_apellidos", label="Apellidos")


    def filter_nombres(self, queryset, name, value):

        return queryset.annotate(
            nombres = Concat("personal_data__first_name", Value(" "), "personal_data__middle_name", output_field=CharField())
        ).filter(Q(personal_data__first_name__icontains=value) | Q(personal_data__middle_name__icontains=value) | Q(nombres__icontains=value))


    def filter_apellidos(self, queryset, name, value):
        return queryset.annotate(
            apellidos = Concat("personal_data__last_name_1", Value(" "), "personal_data__last_name_2", output_field=CharField())
        ).filter(Q(personal_data__last_name_1__icontains=value) | Q(personal_data__last_name_2__icontains=value) | Q(apellidos__icontains=value))



class EstudianteFilter(django_filters.FilterSet):
    class Meta:
        model = Estudiante
        fields = ["status","personal_data__cedula", "nombres", "apellidos", "personal_data__telefono", "personal_data__personal_email",] 

    status = django_filters.ChoiceFilter(choices=Estudiante.Status , widget=forms.RadioSelect, empty_label="Cualquier Status")
    
    personal_data__cedula           = django_filters.NumberFilter(lookup_expr="icontains", label="Cédula", widget=forms.NumberInput(attrs={"max":"999999999", "step":1}))
    personal_data__personal_email   = django_filters.CharFilter(lookup_expr="icontains",   label="Correo Personal", widget=forms.EmailInput)
    personal_data__telefono         = django_filters.CharFilter(lookup_expr="icontains",   label="Telefono Movil",  widget=forms.TextInput(attrs={"type":"tel", "maxlength":12}))

    nombres = django_filters.CharFilter(method="filter_nombres", label="Nombres")
    apellidos = django_filters.CharFilter(method="filter_apellidos", label="Apellidos")


    def filter_nombres(self, queryset, name, value):

        return queryset.annotate(
            nombres = Concat("personal_data__first_name", Value(" "), "personal_data__middle_name", output_field=CharField())
        ).filter(Q(personal_data__first_name__icontains=value) | Q(personal_data__middle_name__icontains=value) | Q(nombres__icontains=value))


    def filter_apellidos(self, queryset, name, value):
        return queryset.annotate(
            apellidos = Concat("personal_data__last_name_1", Value(" "), "personal_data__last_name_2", output_field=CharField())
        ).filter(Q(personal_data__last_name_1__icontains=value) | Q(personal_data__last_name_2__icontains=value) | Q(apellidos__icontains=value))



class ClaseFilter(django_filters.FilterSet):
    class Meta:
        model = Clase
        fields = ["status", "curso", "sensei", "sede", "f_inicio", "f_inicio__lt", "f_inicio__gt", "f_cierre", "f_cierre__gt", "f_cierre__lt", "horas_semanales", "precio", "precio__gt", "precio__lt",  "individual", ]

    status = django_filters.ChoiceFilter(choices=Clase.Status , widget=forms.RadioSelect, empty_label="Cualquier Status")
    individual = django_filters.ChoiceFilter(
        widget=forms.RadioSelect, empty_label="Cualquiera", 
        choices=[
            (True, "Si"),
            (False, "No"),
        ]
    )

    precio     = django_filters.NumberFilter(field_name="precio", label="Precio Exacto ($)")
    precio__gt = django_filters.NumberFilter(field_name="precio", label="Mayor a Precio ($)", lookup_expr="gt")
    precio__lt = django_filters.NumberFilter(field_name="precio", label="Menor a Precio ($)", lookup_expr="lt")

    f_inicio     = django_filters.DateFilter(field_name="f_inicio", label="Fecha de Inicio Exacta",     widget=forms.DateInput(attrs={"type":"date"}))
    f_inicio__gt = django_filters.DateFilter(field_name="f_inicio", label="Después de Fecha de Inicio", widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="gt")
    f_inicio__lt = django_filters.DateFilter(field_name="f_inicio", label="Antes de Fecha de Inicio",   widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="lt")

    f_cierre     = django_filters.DateFilter(field_name="f_cierre", label="Fecha de Cierre Exacta",     widget=forms.DateInput(attrs={"type":"date"}))
    f_cierre__gt = django_filters.DateFilter(field_name="f_cierre", label="Después de Fecha de Cierre", widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="gt")
    f_cierre__lt = django_filters.DateFilter(field_name="f_cierre", label="Antes de Fecha de Cierre",   widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="lt")


class HorarioFilter(django_filters.FilterSet):
    class Meta:
        model = Horario
        fields = ["clase", "dia_semana", "hora_entrada_lt", "hora_entrada", "hora_entrada_gt", "hora_salida_lt", "hora_salida", "hora_salida_gt",]

    
    hora_entrada    = django_filters.TimeFilter(field_name="hora_entrada", label="Hora Entrada Exacta",     widget=forms.TimeInput(attrs={"type":"time"}))
    hora_entrada_gt = django_filters.TimeFilter(field_name="hora_entrada", label="Después de Hora Entrada", widget=forms.TimeInput(attrs={"type":"time"}), lookup_expr="gt")
    hora_entrada_lt = django_filters.TimeFilter(field_name="hora_entrada", label="Antes de Hora Entrada",   widget=forms.TimeInput(attrs={"type":"time"}), lookup_expr="lt")

    hora_salida    = django_filters.TimeFilter(field_name="hora_salida", label="Hora Salida Exacta",     widget=forms.TimeInput(attrs={"type":"time"}))
    hora_salida_gt = django_filters.TimeFilter(field_name="hora_salida", label="Después de Hora Salida", widget=forms.TimeInput(attrs={"type":"time"}), lookup_expr="gt")
    hora_salida_lt = django_filters.TimeFilter(field_name="hora_salida", label="Antes de Hora Salida",   widget=forms.TimeInput(attrs={"type":"time"}), lookup_expr="lt")


class InscripcionesFilter(django_filters.FilterSet):
    class Meta:
        model = Inscripciones
        exclude = []

    precio_a_pagar     = django_filters.NumberFilter(field_name="precio_a_pagar", label="Precio a pagar ($) Exacto")
    precio_a_pagar__gt = django_filters.NumberFilter(field_name="precio_a_pagar", label="Mayor a Precio a pagar ($)", lookup_expr="gt")
    precio_a_pagar__lt = django_filters.NumberFilter(field_name="precio_a_pagar", label="Menor a Precio a pagar ($)", lookup_expr="lt")


class DiaDeClaseFilter(django_filters.FilterSet):
    class Meta:
        model = DiaDeClase
        fields = ["status", "horario__clase", "numero", "fecha__lt", "fecha", "fecha__gt",]

    horario__clase = django_filters.ModelChoiceFilter(label="Clase", queryset=Clase.objects.all())

    fecha     = django_filters.DateFilter(field_name="fecha", label="Fecha de Clase Exacta",     widget=forms.DateInput(attrs={"type":"date"}))
    fecha__gt = django_filters.DateFilter(field_name="fecha", label="Después de Fecha de Clase", widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="gt")
    fecha__lt = django_filters.DateFilter(field_name="fecha", label="Antes de Fecha de Clase",   widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="lt")


class PagosFilter(django_filters.FilterSet):
    class Meta:
        model = Pagos
        fields = ["estudiante", "clase", "metodo", "monto_pagado__lt", "monto_pagado", "monto_pagado__gt", "fecha__lt", "fecha", "fecha__gt", "referencia", "fecha_pago__lt", "fecha_pago", "fecha_pago__gt",]


    monto_pagado     = django_filters.NumberFilter(field_name="monto_pagado", label="Monto Pagado Exacto ($)")
    monto_pagado__gt = django_filters.NumberFilter(field_name="monto_pagado", label="Mayor a Monto Pagado ($)", lookup_expr="gt")
    monto_pagado__lt = django_filters.NumberFilter(field_name="monto_pagado", label="Menor a Monto Pagado ($)", lookup_expr="lt")

    referencia   = django_filters.CharFilter(lookup_expr="icontains", label="Referencia")

    fecha     = django_filters.DateFilter(field_name="fecha", label="Fecha de Registro de Pago Exacta",     widget=forms.DateInput(attrs={"type":"date"}))
    fecha__gt = django_filters.DateFilter(field_name="fecha", label="Después de Fecha de Registro de Pago", widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="gt")
    fecha__lt = django_filters.DateFilter(field_name="fecha", label="Antes de Fecha de Registro de Pago",   widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="lt")

    fecha_pago     = django_filters.DateFilter(field_name="fecha_pago", label="Fecha del Pago Exacta",     widget=forms.DateInput(attrs={"type":"date"}))
    fecha_pago__gt = django_filters.DateFilter(field_name="fecha_pago", label="Después de Fecha del Pago", widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="gt")
    fecha_pago__lt = django_filters.DateFilter(field_name="fecha_pago", label="Antes de Fecha del Pago",   widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="lt")


class SolvenciaFilter(django_filters.FilterSet):
    class Meta:
        model = Clase
        fields = ["status", "curso", "sensei", "sede", "f_inicio", "f_inicio__lt", "f_inicio__gt", "f_cierre", "f_cierre__gt", "f_cierre__lt", "horas_semanales", "precio", "precio__gt", "precio__lt",  "individual", ]

    status = django_filters.ChoiceFilter(choices=Clase.Status , widget=forms.RadioSelect, empty_label="Cualquier Status")
    individual = django_filters.ChoiceFilter(
        widget=forms.RadioSelect, empty_label="Cualquiera", 
        choices=[
            (True, "Si"),
            (False, "No"),
        ]
    )

    precio     = django_filters.NumberFilter(field_name="precio", label="Precio Exacto ($)")
    precio__gt = django_filters.NumberFilter(field_name="precio", label="Mayor a Precio ($)", lookup_expr="gt")
    precio__lt = django_filters.NumberFilter(field_name="precio", label="Menor a Precio ($)", lookup_expr="lt")

    f_inicio     = django_filters.DateFilter(field_name="f_inicio", label="Fecha de Inicio Exacta",     widget=forms.DateInput(attrs={"type":"date"}))
    f_inicio__gt = django_filters.DateFilter(field_name="f_inicio", label="Después de Fecha de Inicio", widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="gt")
    f_inicio__lt = django_filters.DateFilter(field_name="f_inicio", label="Antes de Fecha de Inicio",   widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="lt")

    f_cierre     = django_filters.DateFilter(field_name="f_cierre", label="Fecha de Cierre Exacta",     widget=forms.DateInput(attrs={"type":"date"}))
    f_cierre__gt = django_filters.DateFilter(field_name="f_cierre", label="Después de Fecha de Cierre", widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="gt")
    f_cierre__lt = django_filters.DateFilter(field_name="f_cierre", label="Antes de Fecha de Cierre",   widget=forms.DateInput(attrs={"type":"date"}), lookup_expr="lt")



class MetodosPagosFilter(django_filters.FilterSet):
    class Meta:
        model = MetodosPagos
        exclude = ["obs"]

    metodo = django_filters.CharFilter(lookup_expr="icontains", label="Método")
    datos  = django_filters.CharFilter(lookup_expr="icontains", label="Datos de Pago")


class DescuentoEspecialFilter(django_filters.FilterSet):
    class Meta:
        model = DescuentoEspecial
        exclude = ['obs']

    descuento     = django_filters.NumberFilter(field_name="descuento", label="Descuento ($)")
    descuento__gt = django_filters.NumberFilter(field_name="descuento", label="Mayor a Descuento ($)", lookup_expr="gt")
    descuento__lt = django_filters.NumberFilter(field_name="descuento", label="Menor a Descuento ($)", lookup_expr="lt")


class BecasFilter(django_filters.FilterSet):
    class Meta:
        model = Becas
        fields = ["nombre", "descuento", "descuento__gt", "descuento__lt", "tipo_descuento", "status",]

    nombre         = django_filters.CharFilter(lookup_expr="icontains", label="Nombre Beca")

    descuento     = django_filters.NumberFilter(field_name="descuento", label="Descuento Exacto ($ o %)")
    descuento__gt = django_filters.NumberFilter(field_name="descuento", label="Mayor a Descuento ($ o %)", lookup_expr="gt")
    descuento__lt = django_filters.NumberFilter(field_name="descuento", label="Menor a Descuento ($ o %)", lookup_expr="lt")

    tipo_descuento = django_filters.ChoiceFilter(choices=Becas.TipoDescuento , widget=forms.RadioSelect, empty_label="Cualquier Tipo")
    status         = django_filters.ChoiceFilter(choices=Becas.Status , widget=forms.RadioSelect, empty_label="Cualquier Status")


class BecadosFilter(django_filters.FilterSet):
    class Meta:
        model = Becados
        exclude = ["obs"]