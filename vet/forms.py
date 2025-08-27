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
