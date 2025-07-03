from django.core.management.base import BaseCommand
from gakusei.models import Solvencias, Estudiante, Clase

class Command(BaseCommand):
    help = 'Elimina solvencias de meses incorrectos para un estudiante y clase.'

    def add_arguments(self, parser):
        parser.add_argument('--cedula', type=str, required=True, help='Cédula del estudiante')
        parser.add_argument('--clase_id', type=int, required=True, help='ID de la clase')
        parser.add_argument('--meses', nargs='+', type=int, help='Meses a conservar (1=Enero, ..., 12=Diciembre)')

    def handle(self, *args, **options):
        cedula = options['cedula']
        clase_id = options['clase_id']
        meses_a_conservar = options['meses']

        estudiante = Estudiante.objects.filter(personal_data__cedula=cedula).first()
        if not estudiante:
            self.stdout.write(self.style.ERROR('Estudiante no encontrado'))
            return
        clase = Clase.objects.filter(id=clase_id).first()
        if not clase:
            self.stdout.write(self.style.ERROR('Clase no encontrada'))
            return

        qs = Solvencias.objects.filter(estudiante=estudiante, clase=clase)
        if meses_a_conservar:
            qs = qs.exclude(mes__month__in=meses_a_conservar)
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f'Se eliminaron {count} solvencias para el estudiante {cedula} en la clase {clase_id} (excepto meses {meses_a_conservar})'))
