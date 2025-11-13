from django import forms

from .models import (
    User,
    UserPet,
    UserVet,
    ValoracionVeterinario,
    VeterinaryServiceRequest,
)

TIPO_CUENTA_CHOICES = [
    ('usuario', 'Usuario'),
    ('veterinario', 'Veterinario'),
]

class SignUpForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")
    tipo_cuenta = forms.ChoiceField(choices=TIPO_CUENTA_CHOICES)
    cedula = forms.CharField(max_length=20)
    certificado = forms.FileField(required=False)
    especializacion = forms.CharField(required=False)
    ubicacion_trabajo = forms.CharField(required=False)
    anios_experiencia = forms.IntegerField(required=False, min_value=0, label="Años de experiencia")

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data



class VeterinaryServiceRequestForm(forms.ModelForm):
    class Meta:
        model = VeterinaryServiceRequest
        fields = [
            'veterinarian_name',
            'specialization',
            'contact_info',
            'service_type',
            'cost',
            'appointment_date',
            'appointment_time',
            'location',
            'notes'
        ]
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class VetProfileForm(forms.ModelForm):
    recibir_emergencias = forms.BooleanField(
        required=False,  # important! unchecked will not break validation
        label="Recibir emergencias"
    )

    class Meta:
        model = UserVet
        fields = [
            'cedula',
            'direccion',
            'telefono',
            'certificado',
            'especializacion',
            'recibir_emergencias',
            'anios_experiencia',
            'nombre_profesional',
            'numero_licencia',
            'tipo_profesional',
            'formacion_academica',
            'especialidades_adicionales',
            'servicios_destacados',
            'idiomas',
            'modalidad_atencion',
            'horario_atencion',
        ]


class ValoracionVeterinarioForm(forms.ModelForm):
    """Form to submit or update a veterinarian rating."""

    class Meta:
        model = ValoracionVeterinario
        fields = ['puntuacion', 'comentario']
        labels = {
            'puntuacion': 'Puntuación del servicio',
            'comentario': 'Comentario (opcional)',
        }
        help_texts = {
            'puntuacion': 'Selecciona una calificación de 1 a 5 estrellas.',
        }
        widgets = {
            'puntuacion': forms.Select(
                choices=[(i, f"{i} estrella{'s' if i > 1 else ''}") for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'comentario': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean_puntuacion(self):
        puntuacion = self.cleaned_data.get('puntuacion')
        if puntuacion is None or not (1 <= puntuacion <= 5):
            raise forms.ValidationError("Debes seleccionar un valor entre 1 y 5.")
        return puntuacion
