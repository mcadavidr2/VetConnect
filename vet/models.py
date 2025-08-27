from django.db import models
from django.utils import timezone

# Create your models here.
class Message(models.Model):
    sender = models.CharField(max_length=100)  # Nombre de quien envía el mensaje
    text = models.TextField()  # Contenido del mensaje
    timestamp = models.DateTimeField(default=timezone.now)  # Hora de envío

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
    


class Veterinario(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=500)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    latitud = models.FloatField()
    longitud = models.FloatField()

    def __str__(self):
        return self.nombre
