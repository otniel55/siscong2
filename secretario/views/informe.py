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

def verEstadisticas(request):
    return render(request, "Informe/estadisticas.html", {})

def estGlobal(request):
     return render(request, "Informe/estCong.html", {})

def infPrec(request):
     return render(request, "Informe/estadisticasPrec.html", {})

def estPub(request):
     return render(request, "Informe/estPub.html", {})

def obtenerInf(request):
     hoy=datetime.date.today()
     try:
          mes=int(request.POST['fecha'][0:2])
          year=int(request.POST['fecha'][3:])
     except:
          data={'msg':"No intente hacer trampa"}
     else:
          ultimoInf=[]
          primerInf=[]
          cont=0
          data={}
          meses=[]
          meses.append([year, mes])
          for i in range(1, 6):
               mes -= 1
               if mes == 0:
                    mes = 12
                    year -= 1
               meses.append([year, mes])
          meses.sort(reverse=True)
          pu=Publicador.objects.all()
          for i in pu:
               inform=Informe.objects.filter(FKpub=i.pk)
               if len(inform)>0:
                    primerInf.append(inform.order_by("year", "mes")[0])
                    ultimoInf.append(inform.order_by("-year", "-mes")[0])
          for i in meses:
               if hoy.month==i[1] and hoy.year==i[0]:
                    ult=0
               else:
                    ult=-1
               #variables del mes que se analiza
               inf=Informe.objects.filter(mes=i[1], year=i[0])
               actual={}
               actual['reg']=cantPrecursores(pu,i[1],i[0],[3,4]) #3 es el id del precursorado Regular y 4 el del especial
               actual['aux']=cantPrecursores(pu,i[1],i[0],[1,2]) #1 y 2 son los id del precursorado auxiliar
               mal=cantMalos(ultimoInf,i[1], i[0], ult)
               actual['irreg']=mal[0]
               actual['inactivos']=mal[1]
               actual['pubs']=cantPubs(primerInf, i[1], i[0])
               informes = informeTotal(i[1], i[0])
               actual['publicaciones'] = informes['publicaciones']
               actual['revisitas'] = informes['revisitas']
               actual['estudios'] = informes['estudios']
               actual['horas'] = informes['horas']
               actual['videos'] = informes['videos']
               actual['bau']=cantBau(str(i[0])+"-"+addZero(i[1]))
               #variable del mes anterior
               ant={}
               mes = i[1]
               year = i[0]
               mes -= 1
               if mes == 0:
                    mes = 12
                    year -= 1
               informesAnt = Informe.objects.filter(mes=mes, year=year)
               if len(informesAnt)>0:
                    informes=informeTotal(mes, year)
                    ant['publicaciones']=informes['publicaciones']
                    ant['revisitas']=informes['revisitas']
                    ant['estudios']=informes['estudios']
                    ant['horas']=informes['horas']
                    ant['videos']=informes['videos']
                    ant['aux']=cantPrecursores(pu,mes,year,[1,2])
                    ant['reg']=cantPrecursores(pu,mes,year,[3,4])
                    ant['pubs']=cantPubs(primerInf,mes,year)
                    ant['bau']=cantBau(str(year)+"-"+addZero(mes))
                    mal=cantMalos(ultimoInf,mes,year)
                    ant['irreg']=mal[0]
                    ant['inactivos']=mal[1]
                    result={}
                    for j in actual.keys():
                         if actual[j]==0:
                              result[j]=ant[j]*-100
                         else:
                              result[j]=calculo(actual[j], ant[j])-100
                    suma=0
                    contDiv=0
                    for j in result.values():
                         if j!=0:
                              suma+=j
                              contDiv+=1
                    print(suma)
                    total=suma//contDiv
               else:
                    total="No hubo informes en el mes pasado, no se puede comparar"
               if len(inf) > 0:
                    data[cont] =actual
                    data[cont]['mes']=i[1]
                    data[cont]['result']=total
                    if len(informesAnt)>0:
                         data[cont]['torta']=result
                         sumaTotal=0
                         keys=[]
                         if total>0:
                              for pie in data[cont]['torta'].keys():
                                   if data[cont]['torta'][pie]>0:
                                        sumaTotal+=data[cont]['torta'][pie]
                                        keys.append(pie)
                         else:
                              for pie in data[cont]['torta'].keys():
                                   if data[cont]['torta'][pie] < 0:
                                        sumaTotal += data[cont]['torta'][pie]
                                        keys.append(pie)
                         for k in keys:
                              data[cont]['torta']['t'+k[0].upper()+k[1:]]=calculo(data[cont]['torta'][k], sumaTotal)
                    cont += 1
     return HttpResponse(json.dumps(data))

def cantBau(fecha):
     bautizados=Publicador.objects.filter(fechaBau__startswith=fecha)
     return len(bautizados)

def cantPubs(informes, mes, year):
     pubs=0
     for j in informes:
          if j.year==year and j.mes==mes:
               pubs+=1
     return pubs

def cantMalos(informes,mes,year, ult=-1):
     irregulares=0
     inactivos=0
     for j in informes:
          meses=getDiferenciaMes(j.mes,j.year,mes,year)
          if meses>0+ult and meses<7+ult:
               irregulares+=1
          elif meses>6+ult:
               inactivos+=1
     return [irregulares, inactivos]

def informeTotal(mes, year):
     inform={
          'publicaciones':0,
          'revisitas':0,
          'estudios':0,
          'horas':0,
          'videos':0
     }
     informes = Informe.objects.filter(mes=mes, year=year)
     for inf in informes:
          inform['publicaciones'] += inf.publicaciones
          inform['revisitas'] += inf.revisitas
          inform['estudios'] += inf.estudios
          inform['horas'] += inf.horas
          inform['videos'] += inf.videos
     return inform

def cantPrecursores(publicadores, mes, year, precursorado=[]):
     cantPrec=0
     for i in publicadores:
          precurs=PubPrecursor.objects.filter(FKpub=i.pk, FKprecursor__in=precursorado).order_by("-yearIni", "-mesIni")
          for l in precurs:
               if getDiferenciaMes(l.mesIni, l.yearIni, mes, year)>-2:
                    if l.duracion==0:
                         mesF=mes
                         yearF=year
                    else:
                         fechaF=getFechaFin(l.mesIni, l.yearIni, l.duracion)
                         mesF=fechaF[0]
                         yearF=fechaF[1]
                    if getDiferenciaMes(mes, year, mesF, yearF)>-2:
                         cantPrec+=1
                         break
     return cantPrec

def convertToDate(mes):
     return datetime.date(2016,mes[0],4)

def calculo(nro, base):
     try:
          resultado=(nro*100)/base
          resultado=str(resultado)
          resultado=resultado[:resultado.find(".")+3]
          if resultado.find(".")>-1:
               resultado=float(resultado)
          else:
               resultado=int(resultado)
     except ZeroDivisionError:
          resultado=nro*100
     return resultado