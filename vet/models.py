from django.db import models
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

    def __str__(self):
        return f"{self.username}"
    
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