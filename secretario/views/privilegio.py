#libs propias de python
import datetime
import json
#modulos propios de django
from django.shortcuts import render
from django.http import HttpResponse
#modulos propios de proyecto
from .siscong import *
from secretario.models import Publicador
def consultar(request):
    return render(request, "Privilegio/consultar.html")

def Vistanombrar(request):
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
    return render(request, "Privilegio/consNombrados.html")

def nombrar(request):
    hoy=datetime.date.today()
    msg={}
    pubs=json.loads(request.POST['pub'])
    mes=int(request.POST['fechaIni'][0:2])
    year=int(request.POST['fechaIni'][3:])
    validaciones=True
    if getDiferenciaMes(int(mes), int(year),hoy.month, hoy.year)>-2:
        for p in pubs:
            pass
    else:
        msg={'msg':"No se pueden hacer nombramientos del futuro"}
    return HttpResponse(json.dumps(msg))