#libs propios de python
import datetime
import json
#modulos de django
from django.http import HttpResponse
from django.shortcuts import render
#modulos propios del proyecto
from ..forms import traerGrupo, regPub
from .siscong import *
from secretario.models import GruposPred, Publicador

def vistaRegistrar(request):
     formPub = regPub()
     cmbGrupo = traerGrupo()
     return render(request, 'regPubli.html', {'form': formPub, 'form2': cmbGrupo, 'url':2})

def registrar(request):
     hoy=datetime.date.today()
     nums=['Encargado']
     vFechas=['fechaNa']
     validar=gestion(request.POST,nums,vFechas)
     if not validar.error:
          validar.ignore=['email', 'fechaBau']
          datosP=validar.trimUpper()
          _nombre=datosP['nombre']
          _apellido=datosP['apellido']
          _telefono=datosP['telefono']
          _direccion =datosP['direccion']
          _email=datosP['email']
          _fechaBau=datosP['fechaBau']
          _fechaNa=datosP['fechaNa']
          _grupo=datosP['Encargado']
          edad=getEdad(datetime.date(int(_fechaNa[0:4]),int(_fechaNa[5:7]), int(_fechaNa[8:])), hoy)
          if edad>3:
               try:
                    pub=Publicador.objects.get(nombre=_nombre, apellido=_apellido, fechaNa=_fechaNa)
               except(KeyError, Publicador.DoesNotExist):
                    try:
                         g=GruposPred.objects.get(pk=_grupo)
                    except(KeyError, GruposPred.DoesNotExist):
                         msg={'msg':"El grupo no existe"}
                    else:
                         g.publicador_set.create(nombre=_nombre, apellido=_apellido, telefono=_telefono, direccion=_direccion,email=_email, fechaBau=_fechaBau, fechaNa=_fechaNa)
                         msg={'msg':"Publicador Registrado con exito", 'on':1}
               else:
                    msg={ 'msg': "Error! Este publicador ya esta registrado."}
          else:
               msg={'msg':"Error! Para ser registrado debe tener como minimo 4 anios"}
     else:
          msg=validar.mensaje
     return HttpResponse(json.dumps(msg))