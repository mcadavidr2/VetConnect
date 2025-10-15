from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import SignUpForm
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Veterinario, Perfil

@login_required
def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    # Obtener o crear el perfil asociado al usuario
    try:
        perfil = request.user.perfil
    except Exception:
        Perfil = __import__('vet.models', fromlist=['Perfil']).Perfil
        perfil = Perfil.objects.create(usuario=request.user, cedula='', tipo_cuenta='usuario')

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.usuario = request.user
            perfil.save()
            return redirect('home')
    else:
        form = ProfileForm(instance=perfil)

    return render(request, "edit_profile.html", {"form": form})



from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('home')

# Vista para registro básico
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Crear Perfil asociado
            tipo = form.cleaned_data.get('tipo_cuenta')
            cedula = form.cleaned_data.get('cedula')
            certificado = form.cleaned_data.get('certificado')
            ubicacion = form.cleaned_data.get('ubicacion_trabajo')
            Perfil = __import__('vet.models', fromlist=['Perfil']).Perfil
            Perfil.objects.create(
                usuario=user,
                cedula=cedula,
                tipo_cuenta=tipo,
                certificado=certificado,
                ubicacion_trabajo=ubicacion,
            )
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Message
from .forms import VeterinaryServiceRequestForm
from django.http import JsonResponse
from django.shortcuts import render
from .models import Veterinario
from math import radians, sin, cos, sqrt, atan2
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re

# Create your views here.
@ensure_csrf_cookie
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

@ensure_csrf_cookie
def veterinarios_por_especializacion(request):
    """
    Busca veterinarios por especializacion (query param: q) y muestra resultados paginados.
    """
    q = request.GET.get('q', '').strip()
    veterinarios = Veterinario.objects.all()
    if q:
        # Tokenize query and match any token in name or specialization (OR across tokens)
        tokens = [t for t in re.split(r"\s+", q) if t]
        combined_q = None
        for token in tokens:
            token_q = Q(especializacion__icontains=token) | Q(nombre__icontains=token)
            if combined_q is None:
                combined_q = token_q
            else:
                combined_q |= token_q
        if combined_q is not None:
            veterinarios = veterinarios.filter(combined_q)

    # Ordenar por nombre para estabilidad
    veterinarios = veterinarios.order_by('nombre')

    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(veterinarios, 9)  # 9 por página
    try:
        veterinarios_page = paginator.page(page)
    except PageNotAnInteger:
        veterinarios_page = paginator.page(1)
    except EmptyPage:
        veterinarios_page = paginator.page(paginator.num_pages)

    return render(request, 'veterinarios_por_especializacion.html', {
        'veterinarios': veterinarios_page,
        'q': q,
        'paginator': paginator,
    })


@ensure_csrf_cookie
def veterinarios_list(request):
    """Listado completo de veterinarios paginado."""
    veterinarios = Veterinario.objects.all().order_by('nombre')
    page = request.GET.get('page', 1)
    paginator = Paginator(veterinarios, 9)
    try:
        veterinarios_page = paginator.page(page)
    except PageNotAnInteger:
        veterinarios_page = paginator.page(1)
    except EmptyPage:
        veterinarios_page = paginator.page(paginator.num_pages)

    return render(request, 'veterinarios_list.html', {
        'veterinarios': veterinarios_page,
        'paginator': paginator,
    })

@login_required
def toggle_favorite(request, vet_id):
    perfil = Perfil.objects.get(usuario=request.user)
    veterinario = Veterinario.objects.get(id=vet_id)

    if veterinario in perfil.favoritos.all():
        perfil.favoritos.remove(veterinario)
        is_favorite = False
    else:
        perfil.favoritos.add(veterinario)
        is_favorite = True

    return JsonResponse({'is_favorite': is_favorite})

@login_required
def mis_favoritos(request):
    perfil = Perfil.objects.get(usuario=request.user)
    veterinarios = perfil.favoritos.all()  # all favorite vets of this user
    return render(request, 'mis_favoritos.html', {'veterinarios': veterinarios})