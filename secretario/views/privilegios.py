#libs propias de python
import datetime
import json
#modulos propios de django
from django.shortcuts import render
from django.http import HttpResponse
#modulos propios de proyecto
from .siscong import *
from secretario.models import Publicador, privilegio, privilegioPub

def consultar(request):
    sesionGrupo(request)
    priv=privilegio.objects.all()
    return render(request, "Privilegio/consultar.html", {'data':priv})

def Vistanombrar(request):
    sesionGrupo(request)
    hoy=datetime.date.today()
    data={}
    cont=0
    p=Publicador.objects.exclude(fechaBau__startswith="No").exclude(privilegiopub__status=True)
    for x in p:
       fechaBau=datetime.date(int(x.fechaBau[0:4]), int(x.fechaBau[5:7]), int(x.fechaBau[8:]))
       if getEdad(x.fechaNa, hoy)>17 and x.sexo=="M":
           data[cont]={'pk':x.pk, 'nombre':x.nombre, 'apellido':x.apellido, 'tiempoB':getEdad(fechaBau, hoy), 'fechaBau':x.fechaBau, 'edad':getEdad(x.fechaNa, hoy)}
           cont+=1
    data=data.values()
    return render(request, "Privilegio/nombrar.html", {'data':data})

def consultarNombrados(request):
    sesionGrupo(request)
    pubs=Publicador.objects.filter(privilegiopub__status=True)
    return render(request, "Privilegio/consNombrados.html", {'data':pubs})

def nombrar(request):
    cont=0
    hoy=datetime.date.today()
    msg={}
    pubs=json.loads(request.POST['pub'])
    mes=int(request.POST['fechaIni'][0:2])
    year=int(request.POST['fechaIni'][3:])
    validaciones=True
    if getDiferenciaMes(int(mes), int(year),hoy.month, hoy.year)>-2:
        for p in pubs:
            try:
                pub=Publicador.objects.get(pk=p['id'])
            except(KeyError, Publicador.DoesNotExist):
                validaciones=False
            else:
                try:
                    priv=privilegio.objects.get(pk=p['privilegio'])
                except(KeyError, privilegio.DoesNotExist):
                    validaciones=False
                else:
                    if pub.fechaBau[0]!="N":
                        try:
                            pPriv=Publicador.objects.get(pk=p['id'], privilegiopub__status=True)
                        except(KeyError, Publicador.DoesNotExist):
                            if getEdad(pub.fechaNa,hoy) >= priv.edadMin:
                                fechaBau=datetime.date(int(pub.fechaBau[0:4]), int(pub.fechaBau[5:7]), int(pub.fechaBau[8:]))
                                if getEdad(fechaBau,hoy)>=priv.tiempoBauMin:
                                    privs=privilegioPub.objects.filter(FKpub=pub.pk).order_by("-year", "-mes")
                                    pasar=True
                                    for i in privs:
                                        if privilegioActivo(i, mes, year):
                                            pasar=False
                                            break
                                    if pasar:
                                        privP=privilegioPub(FKpub=pub, FKpriv=priv, mes=mes, year=year, responsabilidad= p['respon'], status=True, fechaFin="activo")
                                        privP.save()
                                        msg[cont] = {'id':p['id'], 'bien':1}
                                    else:
                                        msg[cont] = {'id': p['id'], 'bien':0}
                                        validaciones=False
                                else:
                                    msg[cont] = {'id': p['id'], 'bien':0}
                                    validaciones=False
                            else:
                                validaciones=False
                                msg[cont] = {'id': p['id'], 'bien':0}
                        else:
                            validaciones=False
                    else:
                        validaciones=False
            cont+=1

    else:
        msg={'msg':"No se pueden hacer nombramientos del futuro"}
        validaciones=False
    if validaciones:
        msg={'msg':'Se han asignado los privilegios con exito.'}
    return HttpResponse(json.dumps(msg))

def modificar(request):
    msg={}
    num=['tiempoBau', 'edad', 'id']
    validar=gestion(request.POST, num)
    validar.validar()
    if not validar.error:
        _id=int(request.POST['id'])
        _tiempo=int(request.POST['tiempoBau'])
        _edadMin=int(request.POST['edad'])
        _nombre=request.POST['nombre']
        try:
            priv=privilegio.objects.get(pk=_id)
        except(KeyError, privilegio.DoesNotExist):
            msg={'msg':"Error, privilegio no existe"}
        else:
            priv.nombre=_nombre
            priv.tiempoBauMin=_tiempo
            priv.edadMin=_edadMin
            priv.save()
            msg={'msg':"Privilegio modificado con exito"}
    else:
        msg=validar.mensaje
    return HttpResponse(json.dumps(msg))

def baja(request):
    msg={}
    try:
        idPub=int(request.POST['id'])
    except ValueError:
        msg={'msg':"Error, No intente hacer trampa"}
    else:
        try:
            p=Publicador.objects.get(pk=idPub)
        except(KeyError, Publicador.DoesNotExist):
            msg={'msg':"Error, Publicador no existe"}
        else:
            hoy=datetime.date.today()
            pass

def privilegioActivo(priv, mes, year):
     activo=False
     if getDiferenciaMes(priv.mes, priv.year, mes, year) > -2:
          if priv.fechaFin == "activo":
               mesF = mes
               yearF = year
          else:

               fechaF = priv.fechaFin
               mesF = int(fechaF[0:2])
               yearF = int(fechaF[3:])
          if getDiferenciaMes(mes, year, mesF, yearF) > -2:
               activo=True
     return activo
