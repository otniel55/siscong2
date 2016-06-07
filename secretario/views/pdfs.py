#libs propios de python
import datetime
import json
#modulos de django
from django.http import HttpResponse
from django.shortcuts import render
#modulos propios del proyecto
from secretario.forms import traerGrupo
from .siscong import *
from secretario.models import Publicador, Informe

def vistaPdfPub(request):
     sesionGrupo(request)
     cGrupo = traerGrupo()
     return render(request, "Informe/pdfTarPub.html", {'form':cGrupo})

def datosPdfPub(request):
     mK=[]
     data={}
     data['on']=1
     nums=['pub', 'year']
     validar=gestion(request.POST, nums)
     if not validar.error:
          idPub=int(request.POST['pub'])
          y=int(request.POST['year'])
          try:
               p=Publicador.objects.get(pk=idPub)
          except(KeyError, Publicador.DoesNotExist):
               data['msg']="Publicador no existe"
          else:
               data['name']=p.nombre + " " + p.apellido
               if y>0:
                    inform=Informe.objects.filter(FKpub=p.pk).order_by("year", "mes")
                    if len(inform)>0:
                         meses=arrayServicio(y)
                         keyM=meses.keys()
                         for i in keyM:
                              mK.append(i)
                         mK.sort(reverse=True)
                         for i in mK:
                              data[i]={}
                              recorrido=recorrerArrayMeses(meses[i], p.pk)
                              data[i]=recorrido[0]
                              if recorrido[1]:
                                   break
                    else:
                         data['msg']="Este publicador nunca ha informado"
               else:
                    data['msg']="La cantidad de anios de servicio no puede ser '0'"
     else:
          data=validar.mensaje
     return HttpResponse(json.dumps(data))

#metodos reutilizables

def arrayServicio(cant):
     meses={}
     yActual=datetime.date.today().year
     mActual=datetime.date.today().month
     if mActual<9:
          servicio=[yActual-1, yActual]
     else:
          servicio=[yActual, yActual+1]
          yActual+=1
     strServicio=str(servicio[0])+"-"+str(servicio[1])
     meses[strServicio]={}
     for i in range(0, cant):
          meses[strServicio]=arraymeses(yActual)
          yActual-=1
          strServicio=str(yActual-1)+"-"+str(yActual)
     return meses
