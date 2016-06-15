#librerias propias de python
import json
#modulos de django
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
#modulos propios del proyecti
from .siscong import gestion, sesionGrupo

def vistaRegistro(request):
     sesionGrupo(request)
     return render(request, 'usuReg.html')

def registrar(request):
     validar=gestion(request.POST)
     if not validar.error:
          nombre=request.POST['nombre']
          clave=request.POST['pass']
          try:
               newUser=User.objects.create_user(username=nombre, password=clave)
          except:
               msg={'msg':'Usuario ya existe'}
          else:
               newUser.is_staff=True
               newUser.is_active=True
               newUser.is_superuser=True
               newUser.save()
               msg={'msg':'Usuario registrado con exito', 'on':1}
     else:
          msg={'msg':'Por favor no intente hacer trampa'}
     return HttpResponse(json.dumps(msg))
