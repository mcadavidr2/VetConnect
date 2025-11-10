from django.contrib import admin

from .models import Message
from .models import Message, User, UserPet, UserVet, VeterinaryServiceRequest

# Register your models here.
admin.site.register(Message)
admin.site.register(User)
admin.site.register(UserVet)
admin.site.register(UserPet)
admin.site.register(VeterinaryServiceRequest)