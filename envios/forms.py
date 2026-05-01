from django import forms
from django.utils import timezone
from .models import Encomienda

class EncomiendaForm(forms.ModelForm):
    fecha_entrega = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'YYYY-MM-DD HH:MM'
        }),
        help_text='Selecciona fecha y hora de entrega'
    )

    class Meta:
        model = Encomienda
        fields = ['codigo', 'descripcion', 'peso', 'remitente', 'destinatario', 'ruta', 'fecha_entrega']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: ENC-001'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el contenido de la encomienda'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Peso en kg',
                'step': '0.01',
                'min': '0.01'
            }),
            'remitente': forms.Select(attrs={
                'class': 'form-control'
            }),
            'destinatario': forms.Select(attrs={
                'class': 'form-control'
            }),
            'ruta': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def clean_fecha_entrega(self):
        fecha_entrega = self.cleaned_data.get('fecha_entrega')
        
        if fecha_entrega and fecha_entrega < timezone.now():
            raise forms.ValidationError(
                'La fecha de entrega no puede ser en el pasado.'
            )
        
        return fecha_entrega

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo and not codigo.startswith('ENC-'):
            raise forms.ValidationError(
                'El código debe comenzar con ENC- (Ej: ENC-001)'
            )
        return codigo

    def clean_peso(self):
        peso = self.cleaned_data.get('peso')
        if peso and peso <= 0:
            raise forms.ValidationError(
                'El peso debe ser mayor a 0 kg'
            )
        return peso