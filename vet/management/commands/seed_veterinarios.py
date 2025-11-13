from django.core.management.base import BaseCommand

from vet.models import UserVet

# Demo content reused for both updates and creations so the public profile card looks complete.
DEMO_PROFILES = [
    {
        "first_name": "Laura",
        "last_name": "Gomez",
        "nombre_profesional": "Centro Animal Laureles - Dra. Laura Gomez",
        "email": "demo.laura@vetconnect.test",
        "telefono": "+57 300 123 4567",
        "direccion": "Calle 35 #78-21, Laureles, Medellin",
        "cedula": "900123450",
        "especializacion": "Medicina interna y pacientes felinos",
        "numero_licencia": "MVZ-ANT-4521",
        "tipo_profesional": "Medica Veterinaria",
        "anios_experiencia": 8,
        "formacion_academica": (
            "Medica Veterinaria, Universidad de Antioquia (2016)\n"
            "Diplomado en medicina interna de pequenos animales, CES (2019)"
        ),
        "especialidades_adicionales": "Endocrinologia felina, nutricion clinica, manejo de dolor cronico",
        "servicios_destacados": (
            "Hospitalizacion felina, planes preventivos para gatos senior, teleconsulta de seguimiento"
        ),
        "idiomas": "Espanol, Ingles",
        "modalidad_atencion": "Presencial en clinica, teleconsulta programada",
        "horario_atencion": "Lunes a viernes 8:00-18:00\nSabados 9:00-13:00",
        "latitud": 6.244203,
        "longitud": -75.581212,
        "recibir_emergencias": True,
    },
    {
        "first_name": "Juan",
        "last_name": "Perez",
        "nombre_profesional": "MVZ Juan Perez - Cirugia y ortopedia",
        "email": "demo.juan@vetconnect.test",
        "telefono": "+57 310 555 8899",
        "direccion": "Carrera 48 #26-11, Poblado, Medellin",
        "cedula": "900123451",
        "especializacion": "Cirugia de tejidos blandos y ortopedia",
        "numero_licencia": "MVZ-ANT-4888",
        "tipo_profesional": "MVZ",
        "anios_experiencia": 12,
        "formacion_academica": (
            "MVZ, Universidad Nacional de Colombia (2012)\n"
            "Residencia en cirugia de pequenos animales, UNAM (2016)"
        ),
        "especialidades_adicionales": "Traumatologia, cirugia laparoscopica, medicina del deporte",
        "servicios_destacados": (
            "Reemplazo de cadera, reparacion de ligamento cruzado, planes de rehabilitacion"
        ),
        "idiomas": "Espanol, Portugues tecnico",
        "modalidad_atencion": "Quirofano en clinicas aliadas, visitas a domicilio prequirurgicas",
        "horario_atencion": "Lunes a viernes 7:00-17:00",
        "latitud": 6.210345,
        "longitud": -75.567890,
        "recibir_emergencias": False,
    },
    {
        "first_name": "Camila",
        "last_name": "Restrepo",
        "nombre_profesional": "Unidad Movil Vet al Paso - Dra. Camila Restrepo",
        "email": "demo.camila@vetconnect.test",
        "telefono": "+57 320 777 3344",
        "direccion": "Ruta movil (Itagui, Envigado, Sabaneta)",
        "cedula": "900123452",
        "especializacion": "Medicina preventiva y comportamiento",
        "numero_licencia": "MVZ-ANT-5010",
        "tipo_profesional": "Medica Veterinaria Zootecnista",
        "anios_experiencia": 6,
        "formacion_academica": (
            "MVZ, Universidad CES (2018)\n"
            "Certificacion en etologia clinica, Universidad de Barcelona (2021)"
        ),
        "especialidades_adicionales": "Programas de vacunacion masiva, entrenamiento amable, manejo de ansiedad",
        "servicios_destacados": (
            "Jornadas de vacunacion a domicilio, consultas de comportamiento, talleres para tutores"
        ),
        "idiomas": "Espanol",
        "modalidad_atencion": "Unidad movil, atencion a domicilio, sesiones virtuales breves",
        "horario_atencion": "Martes a sabado 9:00-19:00",
        "latitud": 6.175400,
        "longitud": -75.594377,
        "recibir_emergencias": True,
    },
    {
        "first_name": "Santiago",
        "last_name": "Lopez",
        "nombre_profesional": "Clinica Integral PetSalud - Dr. Santiago Lopez",
        "email": "demo.santiago@vetconnect.test",
        "telefono": "+57 301 222 1199",
        "direccion": "Transversal 32 #30-15, Bello",
        "cedula": "900123453",
        "especializacion": "Diagnostico por imagenes",
        "numero_licencia": "MVZ-ANT-5133",
        "tipo_profesional": "Medico Veterinario",
        "anios_experiencia": 9,
        "formacion_academica": (
            "Medico Veterinario, Universidad de Caldas (2014)\n"
            "Maestria en diagnostico avanzado, Universidad de Cordoba (2019)"
        ),
        "especialidades_adicionales": "Ecografia cardiaca, tomografia computarizada, radiologia digital",
        "servicios_destacados": (
            "Lectura especializada de imagenes, segundas opiniones, capacitacion para colegas"
        ),
        "idiomas": "Espanol, Ingles tecnico",
        "modalidad_atencion": "Centro de imagenologia, apoyo remoto para clinicas asociadas",
        "horario_atencion": "Lunes a viernes 9:00-18:00\nDomingos de guardia alterna",
        "latitud": 6.333321,
        "longitud": -75.558812,
        "recibir_emergencias": False,
    },
]

PROFILE_FIELDS = [
    "nombre_profesional",
    "especializacion",
    "numero_licencia",
    "tipo_profesional",
    "anios_experiencia",
    "formacion_academica",
    "especialidades_adicionales",
    "servicios_destacados",
    "idiomas",
    "modalidad_atencion",
    "horario_atencion",
    "latitud",
    "longitud",
]


def needs_value(current_value):
    """Helper used to decide when we should fill in demo info."""
    if current_value is None:
        return True
    if isinstance(current_value, str):
        return current_value.strip() == ""
    return False


class Command(BaseCommand):
    """Create or fill veterinarian profiles so the public profile page has realistic data."""

    help = "Seeds UserVet records with professional information for development/testing only."

    def handle(self, *args, **options):
        vets = list(UserVet.objects.all().order_by("id"))
        if not vets:
            created = self._create_demo_vets()
            self.stdout.write(self.style.SUCCESS(f"Seeding complete. {created} demo veterinarians created."))
            return

        updated = self._fill_professional_data(vets)
        if updated:
            self.stdout.write(self.style.SUCCESS(f"Datos profesionales completados para {updated} veterinarios existentes."))
        else:
            self.stdout.write("Todos los veterinarios ya tenian informacion profesional.")

    def _fill_professional_data(self, vets):
        """Populate missing fields for every existing UserVet."""
        updated = 0
        for index, vet in enumerate(vets):
            profile = DEMO_PROFILES[index % len(DEMO_PROFILES)]
            changed = False

            for field in PROFILE_FIELDS:
                value = profile.get(field)
                if value and needs_value(getattr(vet, field, None)):
                    setattr(vet, field, value)
                    changed = True

            # Basic identity/contact data - only fill when empty.
            if needs_value(vet.first_name) and profile.get("first_name"):
                vet.first_name = profile["first_name"]
                changed = True
            if needs_value(vet.last_name) and profile.get("last_name"):
                vet.last_name = profile["last_name"]
                changed = True
            if needs_value(vet.telefono) and profile.get("telefono"):
                vet.telefono = profile["telefono"]
                changed = True
            if needs_value(vet.direccion) and profile.get("direccion"):
                vet.direccion = profile["direccion"]
                changed = True
            if needs_value(vet.nombre_profesional) and profile.get("nombre_profesional"):
                vet.nombre_profesional = f"{profile['nombre_profesional']} ({vet.username})"
                changed = True
            if needs_value(vet.email):
                vet.email = f"{vet.username}@vetconnect.test"
                changed = True

            if changed:
                vet.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"Perfil llenado para {vet.username}"))

        return updated

    def _create_demo_vets(self):
        """Create demo users from scratch when no veterinarians exist."""
        prefix = "demo_vet"
        # clean old demo accounts if table was wiped manually but some demo users linger.
        deleted, _ = UserVet.objects.filter(username__startswith=prefix).delete()
        if deleted:
            self.stdout.write(self.style.WARNING(f"Removed {deleted} existing demo veterinarians."))

        created_count = 0
        for index, data in enumerate(DEMO_PROFILES, start=1):
            username = f"{prefix}{index}"
            user = UserVet.objects.create_user(
                username=username,
                email=data["email"],
                password="demo1234",
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                cedula=data["cedula"],
                direccion=data["direccion"],
                telefono=data["telefono"],
            )

            for field in PROFILE_FIELDS:
                setattr(user, field, data.get(field))

            user.recibir_emergencias = data.get("recibir_emergencias", False)
            user.save()
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"Created demo veterinarian: {user.nombre_profesional}"))

        return created_count
