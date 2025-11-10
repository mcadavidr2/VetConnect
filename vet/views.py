from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .forms import SignUpForm, ProfileForm, VeterinaryServiceRequestForm
from .models import User, UserPet, UserVet, Message, VeterinaryServiceRequest
from math import radians, sin, cos, sqrt, atan2
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json, re
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

@login_required
def edit_profile(request):
    user = request.user

    # Use the right form and instance
    form = ProfileForm(request.POST or None, request.FILES or None, instance=user)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('home')

    return render(request, "edit_profile.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('home')

def logout_page(request):
    return render(request, 'logout.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            tipo = form.cleaned_data.get('tipo_cuenta')
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            cedula = form.cleaned_data['cedula']
            password = form.cleaned_data['password']

            # Crear el usuario adecuado según el tipo de cuenta
            if tipo == 'veterinario':
                user = UserVet.objects.create_user(
                    username=username,
                    email=email,
                    cedula=cedula,
                    certificado=form.cleaned_data.get('certificado'),
                    especializacion=form.cleaned_data.get('especializacion')  # si existe en el form
                )
            else:
                user = UserPet.objects.create_user(
                    username=username,
                    email=email,
                    cedula=cedula,
                )

            user.set_password(password)
            user.save()

            # Loguear automáticamente después de registrarse
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


# Create your views here.
@ensure_csrf_cookie
def home(request):
    return render(request, 'home.html')

def about(request):
    is_vet = False
    is_pet = False

    if request.user.is_authenticated:
        # Check if the logged user has a vet or pet profile
        is_vet = hasattr(request.user, 'uservet')
        is_pet = hasattr(request.user, 'userpet')

    return render(request, 'about.html', {
        'is_vet': is_vet,
        'is_pet': is_pet,
    })


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
    veterinarios = UserVet.objects.all()
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


@login_required
def veterinarios_list(request):
    """Listado completo de veterinarios paginado."""
    veterinarios = UserVet.objects.all().order_by('username')
    page = request.GET.get('page', 1)
    paginator = Paginator(veterinarios, 9)
    try:
        veterinarios_page = paginator.page(page)
    except PageNotAnInteger:
        veterinarios_page = paginator.page(1)
    except EmptyPage:
        veterinarios_page = paginator.page(paginator.num_pages)

    # get UserPet instance if possible
    user_pet = None
    if hasattr(request.user, 'userpet'):
        user_pet = request.user.userpet

    return render(request, 'veterinarios_list.html', {
        'veterinarios': veterinarios_page,
        'user_pet': user_pet,
    })

@login_required
def toggle_favorite(request, vet_id):
    user = request.user

    # try to get UserPet version
    try:
        user_pet = user.userpet
    except UserPet.DoesNotExist:
        return JsonResponse({'error': 'Only pets can favorite vets.'}, status=403)

    vet = get_object_or_404(UserVet, id=vet_id)

    if vet in user_pet.favoritos.all():
        user_pet.favoritos.remove(vet)
        is_favorite = False
    else:
        user_pet.favoritos.add(vet)
        is_favorite = True

    return JsonResponse({'is_favorite': is_favorite})


@login_required
def mis_favoritos(request):
    user = request.user

    # try to get UserPet version
    try:
        user_pet = user.userpet
    except UserPet.DoesNotExist:
        return JsonResponse({'error': 'Only pets can favorite vets.'}, status=403)

    veterinarios = user_pet.favoritos.all()
    return render(request, 'mis_favoritos.html', {'veterinarios': veterinarios})