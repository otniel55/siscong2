#libs propios de python
import datetime
import json
import re
#modulos de django
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
#modulos propios del proyecto
from .siscong import *
from secretario.models import Publicador, Informe, horasCon

def registrar(request):
     hoy=datetime.date.today()
     nums=['publicaciones', 'videos', 'revisitas', 'estudios', 'publicador', 'horasCons']
     validar=gestion(request.POST,nums, ignorar='horas')
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
          _hour=convertHoursToMinutes(_horas)
          if _hour[0]:
               if getDiferenciaMes(int(_fecha[0:2]), int(_fecha[3:]),hoy.month, hoy.year)>-2:
                    try:
                         p=Publicador.objects.get(pk=_pub)
                    except(KeyError, Publicador.DoesNotExist):
                         msg={'msg':'Publicador no existe'}
                    else:
                         inf=Informe.objects.filter(mes=int(_fecha[0:2]), year=int(_fecha[3:]),FKpub=_pub)
                         if len(inf)==0:
                              if _horas!="0":
                                   p.informe_set.create(minutos=_hour[1], publicaciones=_publicaciones, videos=_videos, revisitas=_revisitas, estudios=_estudios, mes=int(_fecha[0:2]), year=int(_fecha[3:]), observacion=_obs)
                                   msg={'msg':'Informe Registrado con exito', 'on':1}
                                   if _horasCon>0:
                                        informe=Informe.objects.filter(FKpub=p.pk, mes=int(_fecha[0:2]), year=int(_fecha[3:]))
                                        registrarH=regHorasCon(informe[0], _horasCon)
                                        if not registrarH[0]:
                                             msg=registrarH[1]
                              else:
                                   msg={'msg':"Error, Informe vacio"}
                         else:
                              msg={'msg':'Error informe ya existe'}
               else:
                    msg={'msg':"No puede introducir un informe del futuro"}
          else:
               msg=_hour[1]
     else:
          msg=validar.mensaje
     return HttpResponse(json.dumps(msg))

def tarjeta(request, vista, idPub, y):
     yIni=int(y[:4])
     yFin=int(y[4:])
     datos={}
     try:
          p=Publicador.objects.get(pk=idPub)
     except(KeyError, Publicador.DoesNotExist):
          pagina="page404.html"
     else:
          infs=Informe.objects.filter(Q(year=yIni, mes__in=range(9, 13)) | Q(year=yFin, mes__in=range(1,9)), FKpub=idPub)
          if len(infs)>0 and yIni<yFin:
               request.session['tarjetaPub']=idPub
               request.session['tarjetaY']=y
               mesesY=arraymeses(yFin)
               inf=recorrerArrayMeses(mesesY, idPub)[0]
               inf=inf.values()
               totales={'horasC':0, 'publicaciones':0, 'revisitas':0, 'estudios':0, 'videos':0, 'horasCon':0}
               for i in inf:
                    for j in i.keys():
                         if j not in ["mes", "obs", 'pk', 'horas'] and i[j]!="":
                              if j=="horasC":
                                   tH=str(float(totales[j]))
                                   tHoras=str(float(i[j]))
                                   tHInt=int(tH[tH.find(".")+1:])
                                   tHorasInt=int(tHoras[tHoras.find(".")+1:])
                                   if tHInt+tHorasInt>59:
                                        entero=int(tH[:tH.find(".")])+1
                                        decimal=60-tHInt
                                        decimal=tHorasInt-decimal
                                        r=float(str(entero)+"."+str(decimal))
                                        if r.is_integer():
                                             totales[j]=int(r)
                                        else:
                                             totales[j]=r
                              totales[j]+=i[j]
               hT=str(totales['horasC'])
               totales['horas']=hT[:hT.find(".")+3]
               if not float(totales['horas']).is_integer():
                    totales['horas']=addZeroToFinal(float(totales['horas']))
               if totales['horasCon']==0:
                    del totales['horasCon']
               datos={'pub':inf, 'p':p, 'url':2, "total":totales}
          else:
               datos={'vacio':1, 'url':2}
          if vista == '1':
               pagina = 'Informe/conTarjetaGrupoPub.html'
               request.session['idgrupo'] = p.grupo.values()[0]['IDgrupo']
          else:
               pagina = 'Informe/tarjetaPub.html'

     return render(request, pagina , datos)

def modificar(request):
     msg={}
     hoy=datetime.date.today()
     nums=['publicaciones', 'videos', 'revisitas', 'estudios', 'publicador', 'horasCons']
     validar=gestion(request.POST,nums, ignorar='horas')
     if not validar.error:
          _horas=request.POST['horas']
          _id=int(request.POST['id'])
          _fecha = request.POST['fecha']
          revisitas=int(request.POST['revisitas'])
          estudios=int(request.POST['estudios'])
          publicaciones=int(request.POST['publicaciones'])
          videos=int(request.POST['videos'])
          obs=request.POST['obs']
          HorasC=int(request.POST['horasCons'])
          _hour=convertHoursToMinutes(_horas)
          if _hour[0]:
               try:
                    inf=Informe.objects.get(pk=_id)
               except(KeyError):
                    msg={"msg":"Informe no existe"}
               else:
                    if getDiferenciaMes(int(_fecha[0:2]), int(_fecha[3:]),hoy.month, hoy.year)>-2:
                         if _horas!="0":
                              informes=Informe.objects.filter(mes=int(_fecha[0:2]), year=int(_fecha[3:]), FKpub=inf.FKpub).exclude(pk=inf.pk)
                              if len(informes)==0:
                                   inf.mes=int(_fecha[0:2])
                                   inf.year=int(_fecha[3:])
                                   inf.minutos=_hour[1]
                                   inf.revisitas=revisitas
                                   inf.estudios=estudios
                                   inf.publicaciones=publicaciones
                                   inf.videos=videos
                                   inf.obs=obs
                                   inf.save()
                                   msg={"msg":"Datos del informe modificados con exito"}
                                   if HorasC>0:
                                        try:
                                             hC=horasCon.objects.get(FKinf=inf.pk)
                                        except(KeyError, horasCon.DoesNotExist):
                                             registrarH=regHorasCon(inf, HorasC, False)
                                             if not registrarH[0]:
                                                  msg=registrarH[1]
                                        else:
                                             if horas>100:
                                                  msg={'msg':"Error las horas de consesion NO deben ser mayores a 100"}
                                             else:
                                                  hC.horas=_horasC
                                                  hC.save()
                              else:
                                   msg={'msg':"Error ya existe otro informe con esta fecha"}
                         else:
                              msg={'msg':"Error, el informe no puede estar vacio"}
                    else:
                         msg={'msg':"Error, Informe no puede ser del futuro"}
          else:
               msg=_hour[1]
     else:
          msg=validar.mensaje
     return HttpResponse(json.dumps(msg))

#metodos reutilizables
def regHorasCon(inf, horas, borrar=True):
     msg={}
     validate=False
     idPub=inf.FKpub.pk
     precurs=PubPrecursor.objects.filter(FKpub=idPub, FKprecursor__in=[3,4]).order_by("-yearIni", "-mesIni")
     if len(precurs)>0:
          for prec in precurs:
               if precursorActivo(prec, inf.mes, inf.year):
                    if horas>100:
                         if borrar:
                              inf.delete()
                         msg={'msg':"Error las horas de consesion NO deben ser mayores a 100"}
                    else:
                         inf.horascon_set.create(horas=horas)
                         validate=True
               else:
                    if borrar:
                         inf.delete()
                    msg={'msg':"Error esta persona no realizo precursorado en esta fecha"}
     else:
          if borrar:
               inf.delete()
          msg={'msg':"Error esta persona nunca realizo un precursorado regular o especial"}
     return [validate, msg]

def convertToDate(mes):
     return datetime.date(2016,mes[0],4)

def convertHoursToMinutes(hora):
     result=[]
     hour=0
     minutos=0
     hora=float(hora)
     if hora<1:
          if hora==0.15 or hora==0.30 or hora==0.45:
               hora=str(hora)
               minutos=int(hora[hora.find(".")+1:])
               hour=int(hora[:hora.find(".")])
               minutos=(hour*60)+minutos
               result= [True, minutos]
          else:
               result= [False ,{'msg':'Formato de horas no valido'}]
     else:
          if hora.is_integer():
               result= [True, int(hora)*60]
          else:
               result= [False ,{'msg':'Formato de horas no valido'}]
     return result
