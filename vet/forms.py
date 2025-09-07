from django import forms
from django.contrib.auth.models import User
from .models import Perfil


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Password confirmation')
    tipo_cuenta = forms.ChoiceField(
        choices=[('usuario', 'Usuario'), ('veterinario', 'Veterinario')],
        label='Tipo de cuenta',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cedula = forms.CharField(label='Cédula / ID')
    certificado = forms.FileField(label='Certificado', required=False)
    ubicacion_trabajo = forms.CharField(label='Ubicación de trabajo', required=False)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned_data
from django import forms
from .models import VeterinaryServiceRequest

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

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            'cedula',
            'tipo_cuenta',
            'certificado',
            'ubicacion_trabajo'
        ]
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_cuenta': forms.Select(attrs={'class': 'form-control'}),
            'certificado': forms.FileInput(attrs={'class': 'form-control'}),
            'ubicacion_trabajo': forms.TextInput(attrs={'class': 'form-control'}),
        }

