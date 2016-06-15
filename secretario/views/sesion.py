#libs propias de python
import json
#modulos de django
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
#modulos del proyecto
from .siscong import *

def ingreso(request):
     if not request.user.is_anonymous():
          return HttpResponseRedirect('/')
     else:
          return render(request, 'login.html')

def autenticar(request):
     print("orueba")
     msg={}
     validar=gestion(request.POST)
     if not validar.error:
          usuario=request.POST['user']
          password=request.POST['password']
          acceso=authenticate(username=usuario, password=password)
          print("en un momento ...")
          if acceso is not None:
               print("listo!")
               if acceso.is_active:
                    login(request, acceso)
                    msg={'on':1}
               else:
                    msg={'msg':"Error, usuario desactivado"}
          else:
               print("listo pero mal ps!")
               msg={'msg':"Error, usuario o clave incorrecta"}
     else:
          msg=validar.mensaje
     return HttpResponse(json.dumps(msg))

def cerrar(request):
     logout(request)
     return HttpResponseRedirect('/login')
