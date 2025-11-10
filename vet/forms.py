from django import forms
from .models import User, UserPet, UserVet, VeterinaryServiceRequest


from django import forms
from .models import UserVet, UserPet

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
        fields = ['cedula', 'direccion', 'telefono', 'certificado', 'especializacion', 'recibir_emergencias']
