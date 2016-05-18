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

def consultarNameGroup(request):
     try:
        p=Publicador.objects.get(pk=request.POST['id'])
     except(KeyError, Publicador.DoesNotExist):
        return HttpResponse(json.dumps({'msg':'Error, Publicador no existe'}))
     else:
          p={'nombre':p.nombre, 'apellido':p.apellido,'grupo':p.FKgrupo.pk}
          datos={'pub':p}
          return HttpResponse(json.dumps(datos))

def cambiarPub(request):
     n=['id','grupo']
     validar=gestion(request.POST,n)
     if not validar.error:
          _p=request.POST['id']
          _g=request.POST['grupo']
          try:
               p=Publicador.objects.get(pk=_p)
          except(KeyError, Publicador.DoesNotExist):
               msg={'msg':'Publicador no existe'}
          else:
               try:
                    g=GruposPred.objects.get(pk=_g)
               except(KeyError, GruposPred.DoesNotExist):
                    msg={'msg':'Grupo no existe'}
               else:
                    if p.FKgrupo.pk!=g.pk:
                         Publicador.objects.filter(pk=_p).update(FKgrupo=g)
                         msg={'msg':'El publicador ha sido movido con exito', 'on':1}
                    else:
                         msg={'msg':'No hubo ningun cambio realizado'}
     else:
          msg=validar.mensaje
     return HttpResponse(json.dumps(msg))