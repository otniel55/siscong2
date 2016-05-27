#libs propios de python
import datetime
import json
#modulos de django
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
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

def modificar(request):
     msg={}
     try:
          y=request.session['tarjetaY']
     except(KeyError):
          msg={'msg':'Seleccione un informe'}
     else:
          try:
               p=request.session['tarjetaPub']
          except(KeyError):
               msg={'msg':'Seleccione un informe'}
     mes=request.POST['mes']
     horas=request.POST['horas']
     revisitas=request.POST['revisitas']
     estudios=request.POST['estudios']
     publicaciones=request.POST['publicaciones']
     videos=request.POST['videos']
     try:
          inf=Informe.objects.get(FKpub=p, year=y, mes=mes)
     except(KeyError):
          msg={"msg":"no existe un informe que haya sido registrado en esa fecha"}
     else:
          if inf.horas==horas and inf.revisitas==revisitas and inf.estudios==estudios and inf.publicaciones==publicaciones and inf.videos==videos:
               msg={"msg":"Usted no ha realizado ningun cambio"}
          else:
               inf.horas=horas
               inf.revisitas=revisitas
               inf.estudios=estudios
               inf.publicaciones=publicaciones
               inf.videos=videos
               inf.save()
               msg={"msg":"Datos del informe modificados con exito"}
     HttpResponse(json.dumps(msg))

def convertToDate(mes):
     return datetime.date(2016,mes[0],4)