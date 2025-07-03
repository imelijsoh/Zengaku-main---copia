from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate, dispatch_uid="gakusei_default_users")
def default_users(sender, **kwargs):
    from django.contrib.auth.models import User

    if sender.name == 'gakusei':

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", None, "admin")
            print('Superusuario "admin" creado.')
        else:
            print('Superusuario "admin" ya existe.')

        if not User.objects.filter(username="Kita").exists():
            User.objects.create_user("Kita", None, "kita")
            print('Usuario "Kita" creado.')
        else:
            print('Usuario "Kita" ya existe.')



@receiver(post_migrate, dispatch_uid="gakusei_default_sensei")
def default_sensei(sender, **kwargs):
    from .models import Persona, Sensei
    from django.db import transaction

    if sender.name == "gakusei":

        # USUARIO ELIMINADO
        try:
            with transaction.atomic():
                sensei = Sensei.objects.get_or_create(
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

            print("Sensei Default para registros eliminados creado.")
        
        except:
            print("Sensei Default para registros eliminados ya existe.")
