from django.contrib import admin

from .models import Message
from .models import Message, Veterinario, VeterinaryServiceRequest

# Register your models here.
admin.site.register(Message)
admin.site.register(Veterinario)
admin.site.register(VeterinaryServiceRequest)