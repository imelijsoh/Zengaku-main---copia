# Para Solvencias
from .models import Solvencias, Clase

from dateutil.relativedelta import relativedelta
from django.utils.timezone import now

# Para Email
from .models import Estudiante
from django.core.mail import send_mail


def solvencias_generator():

    try:
        # Se generan las Solvencias solo de las Clases Activas
        clases_activas = Clase.objects.filter(status=Clase.Status.ACTIVO)

        # Obtenemos las clases activas, las inscripciones de cada uno y revisamos sus solvencias
        for clase in clases_activas:
            print(f"1 {clase}")

            inscripciones = clase.inscripciones.all()
            print(f"1 N. estudiantes: {inscripciones.count()}\n")


            # Fechas para buscar/generar las solvencias
            ahora = now().date()+relativedelta(day=1)
            f_inicio = clase.f_inicio+relativedelta(day=1)

            print(f"2 Ahora: {ahora}")
            print(f"2 Fecha inicio: {f_inicio}")

            # Direferencia de meses
            dif = relativedelta(ahora, f_inicio)
            meses = dif.years*12 + dif.months
            print(f"2 Total meses: {meses}\n")


            # Por cada Estudiante Incrito en una Clase, itera para revisar sus solvencias
            for inscrito in inscripciones:
                print(f"3 {inscrito}")

                # Se agrega un +1 para que cuente el mes inicial de la clase
                for i in range(meses+1):
                    mes_actual = f_inicio+relativedelta(months=+i)

                    sol_nueva, sol_creado = Solvencias.objects.get_or_create(
                            estudiante = inscrito.estudiante,
                            clase = clase,
                            mes = mes_actual,

                            defaults={
                                "pagado": Solvencias.Pagado.SIN_PAGAR,
                                "monto_a_pagar": inscrito.precio_a_pagar,
                                "obs": "SOLVENCIA GENERADA AUTOMATICAMENTE",
                            }
                        )
                    if sol_creado:
                        print(f"4 Solvencia del mes {mes_actual} para {inscrito} no encontrada, y se creo.")
                        print(sol_nueva)

                    else:
                        print(f"4 Solvencia del mes {mes_actual}: {sol_nueva} ya existe.")                    

                print(f"\n")
                
            
            print(f"----\n\n")


        return (True, "Solvencias Generadas Correctamente.")
    
    except:
        return (False, "Error al Generar Solvencias")


def email_sender():
    estudiantes_activos = Estudiante.objects.filter(status=Estudiante.Status.ACTIVO)

    email_list = []

    for estudiante in estudiantes_activos:
        email_list.append(estudiante.personal_data.personal_email)

        if estudiante.representante:
            email_list.append(estudiante.representante.personal_data.personal_email)


    # enviador_de_emails(email_list)
    # send_mass_mail() Usar este

    send_mail(
        subject="Prueba",
        message="Cuerpo der mensaje",
        from_email="5a0819418f5681@demomailtrap.co",
        recipient_list=["rrbastardom2011@gmail.com"],
    )

    return email_list
