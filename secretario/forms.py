'''def __init__(self, *args, **kwargs):
    super(datGrupo, self).__init__(*args, **kwargs)
    self.fields['encargado'].initial = datGrupo._enc
    self.fields['auxiliar'].initial = datGrupo._aux'''

from django import forms
from secretario.models import *

class CrearGrupo(forms.ModelForm):
	class Meta:
		model = GruposPred
		fields = ['encargado', 'auxiliar']
		widgets = {
            'encargado': forms.TextInput(attrs={'class': 'form-control mrg-bottom'}),
            'auxiliar': forms.TextInput(attrs={'class': 'form-control mrg-bottom'})
        }

class traerGrupo(forms.Form):
	Encargado = forms.ModelChoiceField(queryset = GruposPred.objects.all(), 
										empty_label=None, 
										widget=forms.Select(attrs={'class': 'form-control'})
										)

class modalPub(forms.ModelForm):
    class Meta:
        model = Publicador
        fields = ['nombre', 'apellido']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'disabled': 'true'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'disabled': 'true'}),
            }

class regPub(forms.ModelForm):
	class Meta:
		model = Publicador
		fields = ['nombre', 'apellido', 'telefono', 'direccion', 'email', 'fechaBau', 'fechaNa']
		widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control mrg-bottom'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control mrg-bottom'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control mrg-bottom'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control mrg-bottom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control mrg-bottom'}),
            'fechaBau': forms.TextInput(attrs={'class':'form-control '}),
            'fechaNa': forms.DateInput(attrs={'class':'form-control'}),
        }

class regInforme(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ['horas', 'publicaciones', 'videos', 'revisitas', 'estudios']
        widgets = {
            'horas': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'type':'number', 'min':'0'}),
            'publicaciones': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'type':'number', 'min':'0'}),
            'videos': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'type':'number', 'min':'0'}),
            'revisitas': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'type':'number', 'min':'0'}),
            'estudios': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'type':'number', 'min':'0'}),
        }

class mesInfor(forms.Form):   
    fecha = forms.CharField(
        label='Mes a Informar:', 
        max_length=6, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
        )