#libs propios de python
import datetime
import json
#modulos de django
from django.http import HttpResponse
from django.shortcuts import render
#modulos propios del proyecto
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
               for i in infs:
                    inf[cont]={'mes':datetime.date(2016,i.mes,4), 'horas':i.horas, 'publicaciones':i.publicaciones, 'videos':i.videos, 'revisitas':i.revisitas, 'estudios':i.estudios}
                    cont+=1
               inf=inf.values()
               datos={'pub':inf, 'p':p, 'url':2}
          else:
               datos={'vacio':1, 'url':2}

          if vista == '1':
               pagina = 'conTarjetaGrupoPub.html'
               request.session['idgrupo'] = p.FKgrupo.pk
          else:
               pagina = 'tarjetaPub.html'

     return render(request, pagina , datos)