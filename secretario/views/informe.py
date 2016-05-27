#libs propios de python
import datetime
import json
#modulos de django
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
#modulos propios del proyecto
from secretario.forms import traerGrupo
from .siscong import *
from secretario.models import Publicador, Informe

def registrar(request):
     hoy=datetime.date.today()
     nums=['horas', 'publicaciones', 'videos', 'revisitas', 'estudios', 'publicador', 'horasCons']
     validar=gestion(request.POST,nums)
     if not validar.error:
          _horas = request.POST['horas']
          _publicaciones = request.POST['publicaciones']
          _videos = request.POST['videos']
          _revisitas = request.POST['revisitas']
          _estudios = request.POST['estudios']
          _fecha = request.POST['fecha']
          _pub=request.POST['publicador']
          _obs=request.POST['obs']
          _horasCon=int(request.POST['horasCons'])
          if getDiferenciaMes(int(_fecha[0:2]), int(_fecha[3:]),hoy.month, hoy.year)>-2:
               try:
                    p=Publicador.objects.get(pk=_pub)
               except(KeyError, Publicador.DoesNotExist):
                    msg={'msg':'Publicador no existe'}
               else:
                    inf=Informe.objects.filter(mes=int(_fecha[0:2]), year=int(_fecha[3:]),FKpub=_pub)
                    if len(inf)==0:
                         p.informe_set.create(horas=_horas, publicaciones=_publicaciones, videos=_videos, revisitas=_revisitas, estudios=_estudios, mes=int(_fecha[0:2]), year=int(_fecha[3:]), observacion=_obs)
                         msg={'msg':'Informe Registrado con exito', 'on':1}
                         if _horasCon>0:
                              informe=Informe.objects.filter(FKpub=p.pk, mes=int(_fecha[0:2]), year=int(_fecha[3:]))
                              precurs=PubPrecursor.objects.filter(FKpub=p.pk, FKprecursor__in=[3,4]).order_by("-yearIni", "-mesIni")
                              if len(precurs)>0:
                                   for prec in precurs:
                                        if getDiferenciaMes(prec.mesIni, prec.yearIni, int(_fecha[0:2]), int(_fecha[3:])) > -2:
                                             if prec.duracion == 0:
                                                  mesF = int(_fecha[0:2])
                                                  yearF =int(_fecha[3:])
                                             else:
                                                  fechaF = getFechaFin(prec.mesIni, prec.yearIni, prec.duracion)
                                                  mesF = fechaF[0]
                                                  yearF = fechaF[1]
                                             if getDiferenciaMes(int(_fecha[0:2]), int(_fecha[3::]), mesF, yearF) > -2:
                                                  if _horasCon>100:
                                                       informe[0].delete()
                                                       msg={'msg':"Error las horas de consesion NO deben ser mayores a 100"}
                                                  else:
                                                       informe[0].horascon_set.create(horas=_horasCon)
                                             else:
                                                  msg={'msg':"Error esta persona no realizo precursorado en esta fecha"}
                                                  informe[0].delete()
                                        else:
                                             informe[0].delete()
                                             msg={'msg':"Error esta persona no realizo precursorado en esta fecha"}
                              else:
                                   informe.delete()
                                   msg={'msg':"Error esta persona nunca realizo un precursorado regular o especial"}
                    else:
                         msg={'msg':'Error informe ya existe'}
          else:
               msg={'msg':"No puede introducir un informe del futuro"}
     else:
          msg=validar.mensaje
     return HttpResponse(json.dumps(msg))

def tarjeta(request, vista, idPub, y):
     yIni=int(y[:4])
     yFin=int(y[4:])
     datos={}
     cont=0
     inf={}
     try:
          p=Publicador.objects.get(pk=idPub)
     except(KeyError, Publicador.DoesNotExist):
          pagina="page404.html"
     else:
          infs=Informe.objects.filter(Q(year=yIni, mes__in=range(9, 13)) | Q(year=yFin, mes__in=range(1,9)), FKpub=idPub)
          if len(infs)>0 and yIni<yFin:
               request.session['tarjetaPub']=idPub
               request.session['tarjetaY']=y
               inf=arrayObjectToDict(infs,['Idinf', 'year', 'FKpub_id', '_state','mes'],{'mes':{'datos':['mes'],'function':convertToDate}})
               inf=inf.values()
               datos={'pub':inf, 'p':p, 'url':2}
          else:
               datos={'vacio':1, 'url':2}
          if vista == '1':
               pagina = 'Informe/conTarjetaGrupoPub.html'
               request.session['idgrupo'] = p.FKgrupo.pk
          else:
               pagina = 'Informe/tarjetaPub.html'

     return render(request, pagina , datos)

#metodos relacionados con los PDF's
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

#metodos reultilizables para informes
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

def convertToDate(mes):
     return datetime.date(2016,mes[0],4)