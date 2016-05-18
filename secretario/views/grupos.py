#libs propios de python
import json
#modulos de django
from django.http import HttpResponse
from django.shortcuts import render
#modulos propios del proyecto
from ..forms import CrearGrupo
from .siscong import validacion
#modelos
from secretario.models import GruposPred

def Vista_registrar(request):
     form = CrearGrupo()
     return render(request, 'regGrupo.html', {'form': form, 'url':1})

def registrar(request):
     msg={}
     validar=validacion(request.POST)
     validar.validar()
     if not validar.error:
          _encargado=request.POST['encargado'].upper()
          _auxiliar=request.POST['auxiliar'].upper()
          _encargado=_encargado.strip()
          _auxiliar=_auxiliar.strip()
          try:
               verificar = GruposPred.objects.get(encargado=_encargado)
          except(KeyError, GruposPred.DoesNotExist):
               grupo=GruposPred(encargado=_encargado, auxiliar=_auxiliar)
               grupo.save()
               msg={'msg':"Grupo Registrado con exito", 'on':1}
          else:
               msg = {'msg': "Este encargado se encuentra en otro grupo"}
     else:
          msg=validar.mensaje
     return  HttpResponse(json.dumps(msg))