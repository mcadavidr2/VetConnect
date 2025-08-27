import json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Message
from .forms import VeterinaryServiceRequestForm
from django.http import JsonResponse
from django.shortcuts import render
from .models import Veterinario
from math import radians, sin, cos, sqrt, atan2

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')


def chat_view(request):
    if request.method == "POST":
        sender = request.POST.get("sender")
        text = request.POST.get("text")
        if sender and text:
            Message.objects.create(sender=sender, text=text)
        return redirect("chat")  # Redirige para limpiar el formulario

    messages = Message.objects.order_by("timestamp")
    return render(request, "chat.html", {"messages": messages})

def request_veterinary_service(request):
    if request.method == "POST":
        form = VeterinaryServiceRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_success')
    else:
        form = VeterinaryServiceRequestForm()

    return render(request, 'request_service.html', {'form': form})

def service_success(request):
    return render(request, 'service_success.html')





# Función para calcular la distancia usando la fórmula Haversine
def calcular_distancia(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia en kilómetros entre dos puntos geográficos
    dados sus latitudes y longitudes utilizando la fórmula Haversine.
    """
    R = 6371  # Radio de la Tierra en km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distancia = R * c  # Resultado en km
    return distancia

# Vista para mostrar veterinarios cercanos
def veterinarios_cercanos(request):
    """
    Recibe las coordenadas (latitud y longitud) del usuario y devuelve
    los veterinarios cercanos en formato JSON.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        lat_usuario = data.get('latitud')
        lon_usuario = data.get('longitud')

        # Buscar veterinarios en la base de datos
        veterinarios = Veterinario.objects.all()

        # Lista para almacenar veterinarios cercanos
        veterinarios_cercanos = []

        # Iterar sobre todos los veterinarios y calcular la distancia
        for vet in veterinarios:
            distancia = calcular_distancia(lat_usuario, lon_usuario, vet.latitud, vet.longitud)
            
            # Filtrar veterinarios dentro de un rango de distancia (por ejemplo, 10 km)
            if distancia <= 10:  # 10 km de distancia
                veterinarios_cercanos.append({
                    'nombre': vet.nombre,
                    'direccion': vet.direccion,
                    'telefono': vet.telefono,
                    'email': vet.email,
                    'distancia': distancia
                })

        return JsonResponse(veterinarios_cercanos, safe=False)
    else:
        #  POST, responder con un error
        return JsonResponse({'error': 'Método no permitido'}, status=405)
