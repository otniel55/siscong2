#libs propias de python
import datetime
#modulos propios de django
from django.shortcuts import render
#modulos propios de proyecto
from .siscong import *
from secretario.models import Publicador
def consultar(request):
    return render(request, "Privilegio/consultar.html")

def nombrar(request):
    hoy=datetime.date.today()
    data={}
    cont=0
    p=Publicador.objects.exclude(fechaBau__startswith="No").exclude(privilegiopub__status=True)
    for x in p:
       fechaBau=datetime.date(int(x.fechaBau[0:4]), int(x.fechaBau[5:7]), int(x.fechaBau[8:]))
       if getEdad(x.fechaNa, hoy)>17 and x.sexo=="M":
           data[cont]={'pk':x.pk, 'nombre':x.nombre, 'apellido':x.apellido, 'tiempoB':getEdad(fechaBau, hoy), 'fechaBau':x.fechaBau}
           cont+=1
    data=data.values()
    return render(request, "Privilegio/nombrar.html", {'data':data})

def consultarNombrados(request):
    return render(request, "Privilegio/consNombrados.html")