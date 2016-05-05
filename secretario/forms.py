
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
										empty_label="--SELECCIONE UN ENCARGADO--",
										widget=forms.Select(attrs={'class': 'form-control'})
									)

class precursorados(forms.Form):
    precur = forms.ModelChoiceField(queryset = Precursor.objects.all().order_by('pk'),
                                        empty_label='Tipos de Precursorados', 
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
		fields = ['nombre', 'apellido', 'telefono', 'direccion', 'email']
		widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control mrg-bottom'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control mrg-bottom'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control mrg-bottom'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control mrg-bottom'}),
            'email': forms.TextInput(attrs={'class': 'form-control mrg-bottom'}),
        }

class regInforme(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ['horas', 'publicaciones', 'videos', 'revisitas', 'estudios', 'observacion']
        widgets = {
            'horas': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'type':'number', 'min':'0'}),
            'publicaciones': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'type':'number', 'min':'0'}),
            'videos': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'type':'number', 'min':'0'}),
            'revisitas': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'type':'number', 'min':'0'}),
            'estudios': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'type':'number', 'min':'0'}),
            'observacion': forms.TextInput(attrs={'class': 'form-control mrg-bottom', 'type':'text'}),
        }
