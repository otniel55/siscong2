#libs propios de python
import datetime
import json
#modulos de django
from django.http import HttpResponse
from django.shortcuts import render
#modulos propios del proyecto
from .siscong import *
from secretario.models import Publicador, Informe

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
          meses=arrayUltSixMonth(mes, year)
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

def conInfPrec(request):
     cont = 0
     data = {}
     try:
          mes = int(request.POST['fecha'][0:2])
          year = int(request.POST['fecha'][3:])
     except:
          data = {'msg': "No intente hacer trampa"}
     else:
          meses = arrayUltSixMonth(mes, year)
          precurs = PubPrecursor.objects.all().order_by("-yearIni", "-mesIni")
          for i in meses:
               promH = []
               promE = []
               promR = []
               contP = 0
               data[cont]={'mes':i[1], 'year':i[0]}
               for p in precurs:
                    if precursorActivo(p, i[1], i[0]):
                         data[cont][contP] = {'nombre': p.FKpub.nombre + " " + p.FKpub.apellido,
                                              'tipo': p.FKprecursor.nombre}
                         try:
                              inf = Informe.objects.get(FKpub=p.FKpub.pk, mes=i[1], year=i[0])
                         except:
                              promH.append(0)
                              promE.append(0)
                              promR.append(0)
                         else:
                              promH.append(inf.horas)
                              promE.append(inf.estudios)
                              promR.append(inf.revisitas)
                         contP += 1
               if len(data[cont]) > 1:
                    data[cont]['promH'] = prom(promH)
                    data[cont]['promE'] = prom(promE)
                    data[cont]['promR'] = prom(promR)
               cont += 1
     return HttpResponse(json.dumps(data))

def conEstPub(request):
     data={}
     try:
          mes = int(request.POST['fecha'][0:2])
          year = int(request.POST['fecha'][3:])
     except:
          data = {'msg': "No intente hacer trampa"}
     else:
          cont=0
          meses = arrayUltSixMonth(mes, year)
          for i in meses:
               pubH=[]
               horas=[]
               revisitas=[]
               estudios=[]
               infs=Informe.objects.filter(mes=i[1], year=i[0])
               if len(infs)>0:
                    for inf in infs:
                         add=True
                         prec=PubPrecursor.objects.filter(FKpub=inf.FKpub.pk).order_by("-yearIni", "-mesIni")
                         for p in prec:
                              if precursorActivo(p, i[1], i[0]):
                                   add=False
                                   break
                         horas.append(inf.horas)
                         revisitas.append(inf.revisitas)
                         estudios.append(inf.estudios)
                         if add:
                              pubH.append(inf.horas)
                    data[cont]={'year':i[0],'mes':i[1], 'promE':prom(estudios), 'promH':prom(horas), 'promR':prom(revisitas)}
                    if len(pubH)>0:
                         data[cont]['promP']=prom(pubH)
                    else:
                         data[cont]['promP']=0
                    cont+=1
     return HttpResponse(json.dumps(data))

#metodos reutilizables
def arrayUltSixMonth(mes, year):
     meses = []
     meses.append([year, mes])
     for i in range(1, 6):
          mes -= 1
          if mes == 0:
               mes = 12
               year -= 1
          meses.append([year, mes])
     meses.sort(reverse=True)
     return meses

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
               if precursorActivo(l, mes, year):
                    cantPrec+=1
                    break
     return cantPrec

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

def precursorActivo(precursorado, mes, year):
     activo=False
     if getDiferenciaMes(precursorado.mesIni, precursorado.yearIni, mes, year) > -2:
          if precursorado.duracion == 0:
               mesF = mes
               yearF = year
          else:
               fechaF = getFechaFin(precursorado.mesIni, precursorado.yearIni, precursorado.duracion)
               mesF = fechaF[0]
               yearF = fechaF[1]
          if getDiferenciaMes(mes, year, mesF, yearF) > -2:
               activo=True
     return activo