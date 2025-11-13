from django.conf import settings
from django.db import models
from django.db.models import Avg, Count
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # already has: username, first_name, last_name, email, password, etc.
    cedula = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20)
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = "General User"
        verbose_name_plural = "General Users"


class UserVet(User):
    certificado = models.FileField(upload_to='certificados/', blank=True, null=True)
    especializacion = models.CharField(max_length=200, blank=True, null=True)
    recibir_emergencias = models.BooleanField(default=False)  # NEW FIELD
    # Professional profile fields used for the expanded public profile
    nombre_profesional = models.CharField(
        max_length=255, blank=True, null=True, help_text="Nombre de la persona responsable"
    )
    numero_licencia = models.CharField(
        max_length=100, blank=True, null=True, help_text="Número de tarjeta profesional o licencia"
    )
    tipo_profesional = models.CharField(
        max_length=120, blank=True, null=True, help_text="Ej: Médico Veterinario, MVZ, Zootecnista"
    )
    anios_experiencia = models.IntegerField(
        blank=True, null=True, help_text="Años de experiencia profesional"
    )
    formacion_academica = models.TextField(
        blank=True, null=True, help_text="Resumen de títulos y universidades"
    )
    especialidades_adicionales = models.TextField(
        blank=True, null=True, help_text="Lista de subespecialidades"
    )
    servicios_destacados = models.TextField(
        blank=True, null=True, help_text="Procedimientos y servicios más comunes"
    )
    idiomas = models.CharField(
        max_length=120, blank=True, null=True, help_text="Idiomas en los que atiende"
    )
    modalidad_atencion = models.CharField(
        max_length=200, blank=True, null=True, help_text="Modalidad de atención ofrecida"
    )
    horario_atencion = models.TextField(
        blank=True, null=True, help_text="Franja de atención semanal"
    )
    promedio_puntuacion = models.FloatField(blank=True, null=True, help_text="Promedio de calificación (cache).")
    cantidad_valoraciones = models.PositiveIntegerField(default=0, help_text="Número de valoraciones registradas.")

    def __str__(self):
        return self.nombre_profesional or self.username

    def actualizar_cache_valoraciones(self):
        """Recalculate cached rating metrics from related reviews."""
        aggregate = self.valoraciones.aggregate(
            promedio=Avg('puntuacion'),
            total=Count('id')
        )
        self.promedio_puntuacion = aggregate['promedio']
        self.cantidad_valoraciones = aggregate['total']
        self.save(update_fields=['promedio_puntuacion', 'cantidad_valoraciones'])
    
    class Meta:
        verbose_name = "UserVet"
        verbose_name_plural = "UserVets"


class UserPet(User):
    favoritos = models.ManyToManyField('UserVet', blank=True, related_name='favoritos_de')

    def __str__(self):
        return f"{self.username}"

    class Meta:
        verbose_name = "UserPet"
        verbose_name_plural = "UserPets"

class Message(models.Model):
    sender = models.CharField(max_length=100)
    text = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sender}: {self.text[:30]}"


class VeterinaryServiceRequest(models.Model):
    veterinarian_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, blank=True)
    contact_info = models.CharField(max_length=150, blank=True)
    service_type = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    location = models.CharField(max_length=150)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.veterinarian_name} - {self.service_type} on {self.appointment_date}"


class ValoracionVeterinario(models.Model):
    """Rating submitted by a user for a veterinarian."""

    CALIFICACION_CHOICES = [(i, str(i)) for i in range(1, 6)]

    veterinario = models.ForeignKey(
        UserVet,
        on_delete=models.CASCADE,
        related_name='valoraciones'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='valoraciones_veterinario'
    )
    puntuacion = models.IntegerField(choices=CALIFICACION_CHOICES)
    comentario = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Valoración de Veterinario"
        verbose_name_plural = "Valoraciones de Veterinarios"
        constraints = [
            models.UniqueConstraint(
                fields=['veterinario', 'usuario'],
                name='unique_valoracion_por_usuario'
            )
        ]

    def __str__(self):
        return f"Voto {self.puntuacion}/5 para {self.veterinario} por {self.usuario}"


@receiver(post_save, sender=ValoracionVeterinario)
def actualizar_cache_valoracion(sender, instance, **kwargs):
    """Keep veterinarian cached rating metrics in sync after save."""
    instance.veterinario.actualizar_cache_valoraciones()


@receiver(post_delete, sender=ValoracionVeterinario)
def eliminar_cache_valoracion(sender, instance, **kwargs):
    """Keep veterinarian cached rating metrics in sync after delete."""
    instance.veterinario.actualizar_cache_valoraciones()
