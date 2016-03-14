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
            'fechaNa': forms.DateInput(attrs={'class':'form-control '}),
        }
