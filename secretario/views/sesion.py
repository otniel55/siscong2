#libs propias de python
import json
#modulos de django
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
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
          if acceso is not None:
               if acceso.is_active:
                    login(request, acceso)
                    msg={'on':1}
                    request.session['nombre']=request.user.username
               else:
                    msg={'msg':"Error, usuario desactivado"}
          else:
               msg={'msg':"Error, usuario o clave incorrecta"}
     else:
          msg=validar.mensaje
     return HttpResponse(json.dumps(msg))

@login_required(login_url='/login')
def cerrar(request):
     try:
          del request.session['nombre']
     except KeyError:
          pass
     logout(request)
     return HttpResponseRedirect('/login')
