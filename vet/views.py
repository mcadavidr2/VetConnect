from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .forms import (
    SignUpForm,
    ValoracionVeterinarioForm,
    VeterinaryServiceRequestForm,
    VetProfileForm,
)
from .models import (
    Message,
    User,
    UserPet,
    UserVet,
    ValoracionVeterinario,
    VeterinaryServiceRequest,
)
from math import radians, sin, cos, sqrt, atan2
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json, re
from django.shortcuts import get_object_or_404


def _build_vet_profile_context(request, vet, allow_rating=True, form_override=None, extra_context=None):
    """Common context data for the veterinarian profile template, including ratings info."""
    valoraciones_recientes = list(
        vet.valoraciones.select_related('usuario').order_by('-fecha_creacion')[:5]
    )
    puede_calificar = allow_rating and request.user.is_authenticated and request.user != vet
    usuario_ya_valoro = False
    valoracion_form = None
    if puede_calificar:
        valoracion_existente = ValoracionVeterinario.objects.filter(
            veterinario=vet, usuario=request.user
        ).first()
        usuario_ya_valoro = valoracion_existente is not None
        valoracion_form = ValoracionVeterinarioForm(instance=valoracion_existente)

    if form_override is not None:
        valoracion_form = form_override

    context = {
        'vet': vet,
        'valoraciones_recientes': valoraciones_recientes,
        'valoracion_form': valoracion_form,
        'usuario_ya_valoro': usuario_ya_valoro,
        'puede_calificar': puede_calificar,
    }
    if extra_context:
        context.update(extra_context)
    return context

@login_required
def edit_profile(request):

    # Use the right form depending on user type
    if hasattr(request.user, 'uservet'):  # if the user is a vet
        form = VetProfileForm(request.POST or None, request.FILES or None, instance=request.user.uservet)
    else:
        # normal user form if needed
        form = VetProfileForm(request.POST or None, request.FILES or None, instance=request.user.uservet)

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
                    especializacion=form.cleaned_data.get('especializacion'),
                    anios_experiencia=form.cleaned_data.get('anios_experiencia')
                )
            else:
                user = UserPet.objects.create_user(
                    username=username,
                    email=email,
                    cedula=cedula,
                )

            user.set_password(password)
            user.save()

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
        def _safe_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        lat_usuario = _safe_float(data.get('latitud'))
        lon_usuario = _safe_float(data.get('longitud'))

        if lat_usuario is None or lon_usuario is None:
            return JsonResponse({'error': 'Coordenadas inválidas'}, status=400)

        # Buscar veterinarios en la base de datos
        veterinarios = UserVet.objects.all()

        # Lista para almacenar veterinarios cercanos
        veterinarios_cercanos = []

        # Iterar sobre todos los veterinarios y calcular la distancia
        for vet in veterinarios:
            if vet.latitud is None or vet.longitud is None:
                continue  # skip vets without registered location
            distancia = calcular_distancia(lat_usuario, lon_usuario, vet.latitud, vet.longitud)
            
            # Filtrar veterinarios dentro de un rango de distancia (por ejemplo, 10 km)
            if distancia <= 10:  # 10 km de distancia
                veterinarios_cercanos.append({
                    'nombre': vet.nombre_profesional or f"{vet.first_name} {vet.last_name}".strip() or vet.username,
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
    Busca veterinarios por especializacion (query param: q) y años de experiencia
    (query param: años_exp) y muestra resultados paginados.
    """
    q = request.GET.get('q', '').strip()
    años_exp = request.GET.get('años_exp', '').strip()
    min_rating = request.GET.get('min_rating', '').strip()
    
    veterinarios = UserVet.objects.all()
    
    # Filtrar por nombre o especialización
    if q:
        # Tokenize query and match any token in name or specialization (OR across tokens)
        tokens = [t for t in re.split(r"\s+", q) if t]
        combined_q = None
        for token in tokens:
            token_q = Q(especializacion__icontains=token) | Q(username__icontains=token)
            if combined_q is None:
                combined_q = token_q
            else:
                combined_q |= token_q
        if combined_q is not None:
            veterinarios = veterinarios.filter(combined_q)
    
    # Filtrar por años de experiencia
    if años_exp:
        if años_exp == '0-2':
            veterinarios = veterinarios.filter(anios_experiencia__gte=0, anios_experiencia__lte=2)
        elif años_exp == '3-5':
            veterinarios = veterinarios.filter(anios_experiencia__gte=3, anios_experiencia__lte=5)
        elif años_exp == '6-10':
            veterinarios = veterinarios.filter(anios_experiencia__gte=6, anios_experiencia__lte=10)
        elif años_exp == '10+':
            veterinarios = veterinarios.filter(anios_experiencia__gte=10)

    if min_rating:
        try:
            min_rating_value = float(min_rating)
            veterinarios = veterinarios.filter(promedio_puntuacion__gte=min_rating_value)
        except ValueError:
            pass

    # Ordenar por nombre para estabilidad
    veterinarios = veterinarios.order_by('username')

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
        'años_exp': años_exp,
        'min_rating': min_rating,
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

@login_required
def vet_profile(request):
    """Shows the logged veterinarian's profile."""
    # ensure the user is a vet
    if not hasattr(request.user, 'uservet'):
        return redirect('home')  # or a 403 page if you prefer

    vet = request.user.uservet

    context = _build_vet_profile_context(request, vet, allow_rating=False)
    return render(request, 'vet_profile.html', context)

def vet_detail(request, vet_id):
    vet = get_object_or_404(UserVet, id=vet_id)
    context = _build_vet_profile_context(request, vet)
    return render(request, 'vet_profile.html', context)


@login_required
def valorar_veterinario(request, pk):
    """Allows an authenticated user to create or update a veterinarian rating."""
    vet = get_object_or_404(UserVet, pk=pk)

    if request.user == vet:
        messages.info(request, "No puedes calificar tu propio perfil profesional.")
        return redirect('vet_detail', vet_id=vet.pk)

    valoracion_existente = ValoracionVeterinario.objects.filter(
        veterinario=vet, usuario=request.user
    ).first()

    if request.method == 'POST':
        form = ValoracionVeterinarioForm(request.POST, instance=valoracion_existente)
        if form.is_valid():
            valoracion = form.save(commit=False)
            valoracion.veterinario = vet
            valoracion.usuario = request.user
            valoracion.save()
            messages.success(request, "Tu calificación ha sido registrada correctamente.")
            return redirect('vet_detail', vet_id=vet.pk)
    else:
        form = ValoracionVeterinarioForm(instance=valoracion_existente)

    context = _build_vet_profile_context(
        request,
        vet,
        form_override=form,
        extra_context={'desde_vista_valoracion': True}
    )
    return render(request, 'vet_profile.html', context)
