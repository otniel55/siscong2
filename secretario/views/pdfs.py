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
     cGrupo = traerGrupo()
     return render(request, "Informe/pdfTarPub.html", {'form':cGrupo})

def datosPdfPub(request):
     mK=[]
     fin=False
     cont=0
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
                         ultimoInf=Informe.objects.filter(FKpub=p.pk).order_by("-year", "-mes")[0]
                         mesPrimerInf=inform[0].mes
                         yearPrimerInf=inform[0].year
                         meses=arrayServicio(y)
                         keyM=meses.keys()
                         for i in keyM:
                              mK.append(i)
                         mK.sort(reverse=True)
                         for i in mK:
                              cont=0
                              data[i]={}
                              for j in meses[i]:
                                   if getDiferenciaMes(j[1],j[0],ultimoInf.mes,ultimoInf.year)>-2:
                                        try:
                                             inf=Informe.objects.get(FKpub=p.pk, mes=j[1], year=j[0])
                                        except:
                                             if not fin:
                                                  data[i][cont]={'vacio':1, 'mes':j[1]}
                                             else:
                                                  data[i][cont]={'mes':j[1], 'horas':"", 'publicaciones':"",
                                                      'revisitas':"", 'estudios':"", 'videos':""
                                                      }
                                        else:
                                             data[i][cont]={'mes':j[1], 'horas':inf.horas, 'publicaciones':inf.publicaciones,
                                                      'revisitas':inf.revisitas, 'estudios':inf.estudios, 'videos':inf.videos, 'obs':inf.observacion
                                                      }
                                             if mesPrimerInf==j[1] and yearPrimerInf==j[0]:
                                                  fin=True
                                                  data[i][cont]['obs']="Primer Informe."
                                   else:
                                        data[i][cont]={'mes':j[1], 'horas':"", 'publicaciones':"",
                                                      'revisitas':"", 'estudios':"", 'videos':""
                                                      }
                                   cont+=1
                              data[i]=reverseDict(data[i])
                              if fin:
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
     cont=0
     cantM=cant*12
     meses={}
     yActual=datetime.date.today().year
     mActual=datetime.date.today().month
     if mActual<9:
          servicio=[yActual-1, yActual]
     else:
          servicio=[yActual, yActual+1]
          yActual+=1
     mActual=8
     strServicio=str(servicio[0])+"-"+str(servicio[1])
     meses[strServicio]=[[yActual, mActual]]
     for i in range(1, cantM):
          mActual-=1
          if mActual==0:
               mActual=12
               yActual-=1
          if mActual==8:
               cont+=1
               if cont==cant:
                    break
               strServicio=str(yActual-1)+"-"+str(yActual)
               meses[strServicio]=[[yActual,mActual]]
          else:
               meses[strServicio].append([yActual,mActual])
     return meses

def reverseDict(dict):
     dictReverse={}
     keys=[]
     cont=0
     for i in dict.keys():
          keys.append(i)
     keys.reverse()
     for i in keys:
          dictReverse[cont]=dict[i]
          cont+=1
     return dictReverse