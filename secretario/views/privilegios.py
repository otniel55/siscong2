#libs propias de python
import datetime
import json
#modulos propios de django
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import *
from django.contrib.auth.decorators import login_required
#modulos propios de proyecto
from .siscong import *
from secretario.models import Publicador, privilegio, privilegioPub, GruposPred

@login_required(login_url='/login')
def consultar(request):
    sesionGrupo(request)
    priv=privilegio.objects.all()
    return render(request, "Privilegio/consultar.html", {'data':priv})

@login_required(login_url='/login')
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

@login_required(login_url='/login')
def consultarNombrados(request):
    sesionGrupo(request)
    hoy=datetime.date.today()
    data={}
    pubs=Publicador.objects.filter(privilegiopub__status=True)
    cont=0
    for i in pubs:
        priv=privilegioPub.objects.get(FKpub=i, status=True)
        tiempo=getDiferenciaMes(priv.mes, priv.year, hoy.month, hoy.year)+1
        data[cont]={'pk':i.pk, 'nombre':i.nombre+" "+i.apellido, 'priv':priv.FKpriv.nombre, 'resp':priv.responsabilidad, 'tiempo':tiempoCompleto(tiempo)}
        if len(GruposPred.objects.filter(encargado=i.pk))>0:
            data[cont]['excluye']=1
        cont+=1
    data=data.values()
    return render(request, "Privilegio/consNombrados.html", {'data':data})

@login_required(login_url='/login')
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
        msg={'msg':'Se han asignado los privilegios con exito.', 'on':1}
    return HttpResponse(json.dumps(msg))

@login_required(login_url='/login')
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
            msg={'msg':"Privilegio modificado con exito", 'on':1}
    else:
        msg=validar.mensaje
    return HttpResponse(json.dumps(msg))

@login_required(login_url='/login')
def baja(request):
    msg={}
    try:
        pubs=json.loads(request.POST['pubs'])
    except (ValueError, KeyError):
        msg={'msg':"Error, No intente hacer trampa"}
    else:
        validaciones=True
        cont=0
        for i in pubs:
            try:
                p=Publicador.objects.get(pk=int(i['id']))
            except(KeyError, Publicador.DoesNotExist):
                msg[cont]={'id':i['id'], 'bien':0}
                validaciones=False
            else:
                hoy=datetime.date.today()
                privilegios=privilegioPub.objects.filter(FKpub=p.pk, status=True).order_by("-year", "-mes")
                if len(privilegios)>0:
                    if len(GruposPred.objects.filter(encargado=p.pk))==0:
                        priv=privilegios[0]
                        priv.status=False
                        priv.fechaFin=str(datetime.date.today())[0:7]
                        priv.save()
                        msg[cont]={'id':i['id'], 'bien':1}
                    else:
                        msg[cont]={'id':i['id'], 'bien':0}
                        validaciones=False
                else:
                    msg[cont]={'id':i['id'], 'bien':0}
                    validaciones=False
            cont+=1
        if validaciones:
            msg={'msg':"Varones han sido dados de baja", 'on':1}
        elif len(pubs)==0:
            msg={'msg':"Error, no intente hacer trampa"}
    return HttpResponse(json.dumps(msg))

#metodos reutilizables
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

def tiempoCompleto(meses):
    mes=0
    year=0
    tiempo=""
    if meses==0:
        tiempo="Inicia este mes"
    else:
        for i in range(0,meses):
            mes+=1
            if mes==13:
                year+=1
                mes=1
        if year>0:
            tiempo=str(year)+" anio"
            if year>1:
                tiempo+="s"
            if meses>0:
                tiempo+=" y "+str(mes)+" mes"
                if mes>1:
                    tiempo+="es"
        else:
            tiempo=str(mes)+" mes"
            if mes>1:
                tiempo+="es"
    return tiempo
