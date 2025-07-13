from django.urls import path

from . import views
from .views import FacturaPagoDeleteView
from gakusei.views import  payment_view
from .views import buscar_estudiante_por_cedula
from .views import autocomplete_estudiante
urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("", views.index, name="index"),
    # factura
    path('myfactura/', payment_view, name='payment_form'),
    path('myfactura/delete/<int:pk>/', FacturaPagoDeleteView.as_view(), name='facturapago-delete'),
    path('estudiantes-autocomplete/', views.estudiantes_autocomplete, name='estudiantes-autocomplete'),

    path("sensei/", views.SenseiListView.as_view(), name="sensei"),
    path("sensei/<int:pk>", views.SenseiDetailView.as_view(), name="sensei-detail"),
    path('buscar-estudiante/', views.buscar_estudiante_por_cedula, name='buscar_estudiante'),
    path("sensei/registrar", views.SenseiCreateView.as_view(), name="sensei-create"),
    path("sensei/editar/<int:pk>", views.SenseiEditView.as_view(), name="sensei-edit"),
    path("sensei/eliminar/<int:pk>", views.SenseiDeleteView.as_view(), name="sensei-delete"),
    path("sensei/buscar", views.SenseiFilterView, name="sensei-filter"),

    path("estudiante/", views.EstudianteListView.as_view(), name="estudiante"),
    path("estudiante/<int:pk>", views.EstudianteDetailView.as_view(), name="estudiante-detail"),
    path("estudiante/registrar", views.EstudianteCreateView.as_view(), name="estudiante-create"),
    path("estudiante/editar/<int:pk>", views.EstudianteEditView.as_view(), name="estudiante-edit"),
    path("estudiante/eliminar/<int:pk>", views.EstudianteDeleteView.as_view(), name="estudiante-delete"),
    path("estudiante/registrar/representante", views.RepresentanteCreatePopup.as_view(), name="estudiante-create-representante"),
    path("estudiante/buscar", views.EstudianteFilterView, name="estudiante-filter"),


    path("representante/registrar", views.RepresentanteCreateView.as_view(), name="representante-create"),


    path("clase/", views.ClaseListView.as_view(), name="clase"),
    path("clase/<int:pk>", views.ClaseDetailView.as_view(), name="clase-detail"),
    path("clase/registrar", views.ClaseCreateView.as_view(), name="clase-create"),
    path("clase/editar/<int:pk>", views.ClaseEditView.as_view(), name="clase-edit"),
    path("clase/eliminar/<int:pk>", views.ClaseDeleteView.as_view(), name="clase-delete"),
    path("clase/buscar", views.ClaseFilterView, name="clase-filter"),


    path("horario/", views.HorarioListView.as_view(), name="horario"),
    path("horario/<int:pk>", views.HorarioDetailView.as_view(), name="horario-detail"),
    path("horario/registrar", views.HorarioCreateView.as_view(), name="horario-create"),
    path("horario/editar/<int:pk>", views.HorarioEditView.as_view(), name="horario-edit"),
    path("horario/eliminar/<int:pk>", views.HorarioDeleteView.as_view(), name="horario-delete"),
    path("horario/buscar", views.HorarioFilterView, name="horario-filter"),


    path("inscripciones/", views.InscripcionesListView.as_view(), name="inscripciones"),
    path("inscripciones/<int:pk>", views.InscripcionesDetailView.as_view(), name="inscripciones-detail"),
    path("inscripciones/registrar", views.InscripcionesCreateView.as_view(), name="inscripciones-create"),
    path("inscripciones/editar/<int:pk>", views.InscripcionesEditView.as_view(), name="inscripciones-edit"),
    path("inscripciones/eliminar/<int:pk>", views.InscripcionesDeleteView.as_view(), name="inscripciones-delete"),
    path("inscripciones/buscar", views.InscripcionesFilterView, name="inscripciones-filter"),


    path("diadeclase/", views.DiaDeClaseListView.as_view(), name="dia-de-clase"),
    path("diadeclase/<int:pk>", views.DiaDeClaseDetailView.as_view(), name="dia-de-clase-detail"),
    path("diadeclase/registrar", views.DiaDeClaseCreateView.as_view(), name="dia-de-clase-create"),
    path("diadeclase/editar/<int:pk>", views.DiaDeClaseEditView.as_view(), name="dia-de-clase-edit"),
    path("diadeclase/eliminar/<int:pk>", views.DiaDeClaseDeleteView.as_view(), name="dia-de-clase-delete"),
    path("diadeclase/buscar", views.DiaDeClaseFilterView, name="dia-de-clase-filter"),


    path("asistencia/", views.AsistenciaListView.as_view(), name="asistencia"),
    path("asistencia/<int:pk>", views.AsistenciaDetailView.as_view(), name="asistencia-detail"),
    path("asistencia/registrar", views.AsistenciaCreate, name="asistencia-create"),
    path("asistencia/registrar-rezagados", views.AsistenciaCreateRezagados, name="asistencia-create-rezagados"),
    path("asistencia/editar/<int:pk>", views.AsistenciaEditView.as_view(), name="asistencia-edit"),


    path("pagos/", views.PagosListView.as_view(), name="pagos"),
    path("pagos/<int:pk>", views.PagosDetailView.as_view(), name="pagos-detail"),
    path("pagos/registrar", views.PagosCreateView.as_view(), name="pagos-create"),
    path("pagos/eliminar/<int:pk>", views.PagosDeleteView.as_view(), name="pagos-delete"),
    path("pagos/buscar", views.PagosFilterView, name="pagos-filter"),


    path("solvencias/", views.SolvenciaClaseListView.as_view(), name="solvencias-clase"),
    path("solvencias/clase-<int:pk>", views.SolvenciaClaseDetailView.as_view(), name="solvencias-clase-detail"),
    path("solvencias/buscar", views.SolvenciaFilterView, name="solvencias-filter"),


    path("sedes/", views.SedeListView.as_view(), name="sede"),
    path("sedes/<int:pk>", views.SedeDetailView.as_view(), name="sede-detail"),
    path("sedes/registrar", views.SedeCreateView.as_view(), name="sede-create"),
    path("sedes/editar/<int:pk>", views.SedeEditView.as_view(), name="sede-edit"),


    path("cursos/", views.CursoListView.as_view(), name="curso"),
    path("cursos/<int:pk>", views.CursoDetailView.as_view(), name="curso-detail"),
    path("cursos/registrar", views.CursoCreateView.as_view(), name="curso-create"),
    path("cursos/editar/<int:pk>", views.CursoEditView.as_view(), name="curso-edit"),


    path("metodosdepago/", views.MetodosPagoListView.as_view(), name="metodos-pago"),
    path("metodosdepago/<int:pk>", views.MetodosPagoDetailView.as_view(), name="metodos-pago-detail"),
    path("metodosdepago/registrar", views.MetodosPagoCreateView.as_view(), name="metodos-pago-create"),
    path("metodosdepago/buscar", views.MetodosPagoFilterView, name="metodos-pago-filter"),

    


    path("descuentosespeciales/", views.DescuentoEspecialListView.as_view(), name="descuento-especial"),
    path("descuentosespeciales/<int:pk>", views.DescuentoEspecialDetailView.as_view(), name="descuento-especial-detail"),
    path("descuentosespeciales/registrar", views.DescuentoEspecialCreateView.as_view(), name="descuento-especial-create"),
    path("descuentosespeciales/editar/<int:pk>", views.DescuentoEspecialEditView.as_view(), name="descuento-especial-edit"),
    path("descuentosespeciales/eliminar/<int:pk>", views.DescuentoEspecialDeleteView.as_view(), name="descuento-especial-delete"),
    path("descuentosespeciales/buscar", views.DescuentoEspecialFilterView, name="descuento-especial-filter"),


    path("becas/", views.BecaListView.as_view(), name="becas"),
    path("becas/<int:pk>", views.BecaDetailView.as_view(), name="becas-detail"),
    path("becas/registrar", views.BecaCreateView.as_view(), name="becas-create"),
    path("becas/asignar", views.BecaAssingView.as_view(), name="becas-asignar"),
    path("becas/desasingar/<int:pk>", views.BecaDeassingView.as_view(), name="becas-desasignar"),
    path("becas/buscar", views.BecasFilterView, name="becas-filter"),
    path("becados/buscar", views.BecadosFilterView, name="becados-filter"),


    # API
    path("api/representantes/", views.Api_RepresentantesGet, name="api-representantes-get"),
    path("api/clase/", views.Api_ClaseGet, name="api-clase-get"),
    path("api/estudiante/", views.Api_EstudianteGet, name="api-estudiante-get"),

    path("api/diasdeclase/form", views.Api_DiasDeClase_Form, name="api-dia-de-clase-form"),

    path("api/asistencia/form", views.Api_AsistenciaForm, name="api-asistencia-form"),
    path("api/asistencia/form-rezagados/", views.Api_AsistenciaFormRezagados, name="api-asistencia-form-rezagados"),


    path("api/pagos/clases/", views.Api_Pagos_Clases, name="api-pagos-clases"),
    path("api/pagos/mensualidad/", views.Api_Pagos_Mensualidad, name="api-pagos-mensualidad"),


    # Solvencias Generator / Email Sender
    path("api/solvencias/generate", views.SolvenciaGenerator, name="api-solvencias-generator"),
    path("api/emails/send", views.EmailSender, name="api-email-send"),
    
]

urlpatterns += [
    path('autocomplete-estudiante/', autocomplete_estudiante, name='autocomplete_estudiante'),
]
