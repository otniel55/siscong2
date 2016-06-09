#libs propios de python
import datetime
import json
#modulos de django
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse
#modulos propios del proyecto
from secretario.forms import precursorados
from .siscong import *
from secretario.models import Publicador, Informe, nroPrec, Precursor

def vistaNombrar(request):
     sesionGrupo(request)
     hoy = datetime.date.today()
     bajaAuto()
     cont=0
     p={}
     pubs=Publicador.objects.exclude(fechaBau__startswith="No").exclude(pubprecursor__status=True)
     precur= precursorados()
     for x in pubs:
          pasar=True
          precursor=PubPrecursor.objects.filter(FKpub=x.pk).order_by("-yearIni", "-mesIni")
          if len(precursor)>0:
               if precursorActivo(precursor[0], hoy.month, hoy.year):
                   pasar=False
          if pasar:
               fechaBau=datetime.date(int(x.fechaBau[0:4]), int(x.fechaBau[5:7]), int(x.fechaBau[8:]))
               p[cont]={'pk':x.pk, 'nombre':x.nombre, 'apellido':x.apellido, 'tiempoB':getEdad(fechaBau, hoy), 'fechaBau':x.fechaBau}
               cont=cont+1
     p=p.values()
     return render(request, 'Precursor/nombrarPub.html', {'pub':p, 'precur':precur, 'url':3})

def conPrec(request):
     sesionGrupo(request)
     bajaAuto()
     precur= precursorados()
     return render(request, 'Precursor/conPrecur.html', {'precur':precur, 'url':3})

def editPrecur(request):
     sesionGrupo(request)
     return render(request, 'Precursor/editPrecur.html', {'precur': Precursor.objects.all(), 'url':3})

def nombrar(request):
     hoy=datetime.date.today()
     bajaAuto()
     validaciones=True
     cont=0
     msg={}
     p=json.loads(request.POST['pub'])
     mes=int(request.POST['fechaIni'][0:2])
     year=int(request.POST['fechaIni'][3:])
     if getDiferenciaMes(int(mes), int(year),hoy.month, hoy.year)>-2:
          for x in p:
               try:
                    int(x['duracion'])
               except ValueError:
                    validaciones=False
                    msg[cont] = {'msg': 'ha introducido una duracion en un formato no valido para el publicador ' + x['id'] + " pro favor introduzca solo numeros"}
               else:
                    try:
                         pub = Publicador.objects.get(pk=x['id'])
                    except(KeyError, Publicador.DoesNotExist):
                         msg[cont] = {'msg': 'el publicador' + x['id'] + 'no esta registrado'}
                         validaciones = False
                    else:
                         try:
                              prec=Precursor.objects.get(pk=x['precur'])
                         except(KeyError, Precursor.DoesNotExist):
                              msg[cont]={'msg':'El precursorado'+ x['precur'] + ' no existe'}
                              validaciones=False
                         else:
                              verificar = PubPrecursor.objects.filter(FKpub=x['id'], status=True)
                              if len(verificar) > 0:
                                   msg[cont] = {'msg': 'el publicador' + x['id'] + 'ya es precursor'}
                                   validaciones = False
                              else:
                                   if pub.fechaBau[0]!='N':
                                        precurs=PubPrecursor.objects.filter(FKpub=pub.pk).order_by("-yearIni", "-mesIni")
                                        pasar=True
                                        if len(precurs)>0:
                                             for iprecur in precurs:
                                                  if precursorActivo(iprecur, mes, year):
                                                       pasar=False
                                                       break
                                        if pasar:
                                             pubP = PubPrecursor(FKpub=pub, FKprecursor=prec, duracion=x['duracion'], mesIni=mes, yearIni=year, status=True)
                                             pubP.save()
                                             if prec.pk in (3, 4):
                                                  try:
                                                       nro=nroPrec.objects.get(FKpub=pub.pk)
                                                  except(KeyError, nroPrec.DoesNotExist):
                                                       try:
                                                            int(x['nroPrec'])
                                                       except ValueError:
                                                            msg[cont] = {'msg': 'valor no valido para nro de precursor del publicador ' + x['id'] + ' por favor introduzca solo numeros'}
                                                            pubP.delete()
                                                            validaciones=False
                                                       else:
                                                            pub.nroprec_set.create(nroPrec=x['nroPrec'])
                                                            msg[cont] = {'id':x['id'], 'bien':1}
                                                  else:
                                                       msg[cont] = {'id':x['id'], 'bien':1}
                                             else:
                                                  msg[cont] = {'id':x['id'], 'bien':1}
                                        else:
                                             msg[cont] = {'id': x['id'], 'bien':0}
                                             validaciones=False
                                   else:
                                        msg[cont] = {'msg': 'el publicador' + x['id'] + 'no esta bautizado'}
                                        validaciones=False
               cont+= 1
     else:
          msg={'msg':"Error! no intente hacer trampa"}
          validaciones=False
     if validaciones:
          msg={'msg':'Los publicadores han sido nombrados precursores.'}
     return HttpResponse(json.dumps(msg))

def conPrecs(request):
     bajaAuto()
     contaux=0
     years=[]
     cont=0
     precs={}
     prec=int(request.POST['precur'])
     request.session['precur']=prec
     status=int(request.POST['status'])
     if status==1:
          status=True
     elif status==2:
          status=False
     try:
          Precursor.objects.get(pk=prec)
     except(KeyError, Precursor.DoesNotExist):
          data={'msg':"Precursorado no existe"}
     else:
          if status:
               if prec==2 or prec==1:
                    p=Publicador.objects.filter(Q(pubprecursor__FKprecursor=1) | Q(pubprecursor__FKprecursor=2), pubprecursor__status=status).distinct()
               else:
                    p=Publicador.objects.filter(pubprecursor__FKprecursor=prec, pubprecursor__status=status).distinct()
          else:
               if prec==2 or prec==1:
                    p=Publicador.objects.filter(Q(pubprecursor__FKprecursor=1) | Q(pubprecursor__FKprecursor=2), pubprecursor__status=status).exclude(pubprecursor__status=not status).distinct()
               else:
                    p=Publicador.objects.filter(pubprecursor__FKprecursor=prec, pubprecursor__status=status).exclude(pubprecursor__status=not status).distinct()
          if len(p)>0:
               for i in p:
                    precs[cont]={'pk':i.pk, 'nombre':i.nombre+" "+i.apellido}
                    cont+=1
               data = {'p':precs}
          else:
               data={'msg':'No hay ningun registro de este tipo de precursor'}
     return HttpResponse(json.dumps(data))

def historiaPrec(request, year):
     sesionGrupo(request)
     bajaAuto()
     cont=0
     precurTrue=[]
     entrar=False
     ficha={'on':0}
     data={}
     mesPrecur=[]
     hoy=datetime.date.today()
     prec=request.session['precur']
     pub=request.session['pubprec']
     if prec==2 or prec==1:
          pg="tarjetaPrecAux.html"
          entrar=True
     elif prec==3 or prec==4:
          pg="tarjetaPrecReg.html"
          entrar=True
     else:
          pg="tarjetaPrecAux.html"
          data={'msg':"Tipo de precursorado no existe"}
     if entrar:
          iniM=9
          iniY=int(year[0:4])
          finM=8
          finY=int(year[4:])
          try:
               Publicador.objects.get(pk=pub)
          except(KeyError, Publicador.DoesNotExist):
               data={'msg': "Publicador(a) no esta registrado en el sistema"}
          else:
               if prec==2:
                    p=PubPrecursor.objects.filter(Q(FKprecursor=1) | Q(FKprecursor=2),FKpub=pub).order_by("-yearIni", "-mesIni")
               elif prec==3 or prec==4:
                    p=PubPrecursor.objects.filter(FKpub=pub, FKprecursor=prec).order_by("-yearIni", "-mesIni")
               if len(p)>0:
                    for prec in p:
                         if cont==0:
                              if prec.duracion==0:
                                   fEnd="Realizando Precursorado hasta la actualidad"
                                   fMonth=hoy.month
                                   fYear=hoy.year
                                   duracion=getDiferenciaMes(prec.mesIni,prec.yearIni,fMonth,fYear)+1
                              else:
                                   fEnd=getFechaFin(prec.mesIni,prec.yearIni,prec.duracion)
                                   fMonth=fEnd[0]
                                   fYear=fEnd[1]
                                   fEnd=str(fMonth)+"-"+str(fYear)
                                   duracion=prec.duracion
                              nombre=prec.FKpub.nombre+" "+prec.FKpub.apellido
                              fechaI=str(prec.mesIni)+"-"+str(prec.yearIni)
                              if request.session['precur']==1 or request.session['precur']==2:
                                   ficha={'nombre':nombre, 'fechaI':fechaI, 'fechaF':fEnd, 'duracion':duracion}
                              else:
                                   nrop=nroPrec.objects.get(FKpub=prec.FKpub.pk)
                                   nro=nrop.nroPrec
                                   duracion=getTiempo(p)
                                   ficha={'nombre':nombre, 'fechaI': fechaI, 'fechaBau':prec.FKpub.fechaBau, 'duracion':duracion, 'nroPrec':nro}
                         if prec.duracion==0:
                              mesFin=hoy.month
                              yearFin=hoy.year
                         else:
                              fechaFin=getFechaFin(prec.mesIni, prec.yearIni, prec.duracion)
                              mesFin=fechaFin[0]
                              yearFin=fechaFin[1]
                         duracion=getDiferenciaMes(iniM,iniY,mesFin,yearFin)
                         duracionIni=getDiferenciaMes(prec.mesIni,prec.yearIni,finM,finY)
                         if duracion > -2 and duracionIni > -2:
                              precurTrue.append(prec)
                         cont+=1
                    cont=0
                    if len(precurTrue)>0:
                         for pre in precurTrue:
                              if cont==0:
                                   if pre.duracion==0:
                                        fMonth=hoy.month
                                        fYear=hoy.year
                                   else:
                                        fEnd=getFechaFin(pre.mesIni,pre.yearIni,pre.duracion)
                                        fMonth=fEnd[0]
                                        fYear=fEnd[1]
                              else:
                                   fEnd=getFechaFin(pre.mesIni,pre.yearIni,pre.duracion)
                                   fMonth=fEnd[0]
                                   fYear=fEnd[1]
                              fFin=getDiferenciaMes(finM, finY, fMonth, fYear)
                              if fFin > -2:
                                   fMonth=finM
                                   fYear=finY
                              iMonth=pre.mesIni
                              iYear=pre.yearIni
                              fIni=getDiferenciaMes(iniM,iniY,iMonth,iYear)
                              if fIni < -1:
                                  iMonth=iniM
                                  iYear=iniY
                              duracion=getDiferenciaMes(iMonth,iYear,fMonth,fYear)+2
                              while duracion>0:
                                   mesPrecur.append([iYear, iMonth, pre.FKprecursor.horas, pre.duracion])
                                   if iMonth==hoy.month and iYear==hoy.year:
                                       mesPrecur.pop()
                                   iMonth+=1
                                   if iMonth==13:
                                        iMonth=1
                                        iYear+=1
                                   duracion-=1
                              mesPrecur.sort()
                              cont+=1
                         acum=0
                         cont=0
                         if len(mesPrecur)>0:
                              for f in mesPrecur:
                                   if cont==0:
                                        if f[3]==0:
                                            m=f[1]
                                            if f[1]<9:
                                                m=f[1]+12
                                            horasT=(12-(m-iniM))*f[2]
                                        else:
                                             horasT=len(mesPrecur)*f[2]
                                   try:
                                        inf=Informe.objects.get(FKpub=pub, mes=f[1], year=f[0])
                                   except(KeyError, Informe.DoesNotExist):
                                        if request.session['precur'] in (1, 2):
                                             data[cont]={'fecha':datetime.date(f[0],f[1],15), 'horasR':f[2], 'horasI':0, 'obj':0}
                                        else:
                                             if acum>=f[2]*(cont+1):
                                                  obj=1
                                             else:
                                                  obj=0
                                             data[cont] = {'fecha': datetime.date(f[0], f[1], 15), 'horasI':0, 'horasA':acum, 'horasRes':horasT-acum, 'obj':obj}
                                   else:
                                        if request.session['precur'] in (1,2):
                                             hoursDecimal=int(convertMinutesToHours(inf.minutos))
                                             if hoursDecimal>=f[2]:
                                                  obj=1
                                             else:
                                                  obj=0
                                             data[cont]={'fecha':datetime.date(f[0],f[1],15), 'horasR':f[2], 'horasI':addZeroToFinal(hoursDecimal), 'obj':obj}
                                        else:
                                             acum+=int(convertMinutesToHours(inf.minutos))
                                             if acum>=f[2]*(cont+1):
                                                  obj=1
                                             else:
                                                  obj=0
                                             data[cont]={'fecha':datetime.date(f[0],f[1],15), 'horasI':int(convertMinutesToHours(inf.minutos)), 'horasA':acum, 'horasRes':horasT-acum, 'obj':obj}
                                   cont=cont+1
                         else:
                              precursor=Precursor.objects.get(pk=request.session['precur'])
                              m = hoy.month
                              if m < 9:
                                  m = m + 12
                              horasR=precursor.horas
                              horasT = (12 - (m - iniM)) * horasR
                              if request.session['precur'] in (1, 2):
                                   data[cont] = {'fecha': datetime.date(hoy.year, hoy.month, 15), 'horasR': horasR, 'horasI': "En curso",'obj': 2}
                              else:
                                   data[cont] = {'fecha': datetime.date(hoy.year, hoy.month, 15), 'horasI': "En curso", 'horasA': 0,'horasRes': horasT, 'obj': 2}
                         data=data.values()
                    else:
                         data={'msg':"Esta persona no fue precursor en el periodo "+year}
               else:
                    data={'msg':"Este Publicador nunca ha sido precursor"}
     return render(request, pg, {'ficha':ficha, 'datos':data})

def darBaja(request):
     hoy=datetime.date.today()
     data={}
     try:
          pub=request.session['pubprec']
     except(KeyError):
          data={'msg':"Seleccione un Precursor"}
     else:
          try:
               Publicador.objects.get(pk=pub)
          except(KeyError, Publicador.DoesNotExist):
               data={'msg':"Publicador no esta esta registrado en el sistema"}
          else:
               try:
                    precur=PubPrecursor.objects.get(FKpub=pub, status=True)
               except(KeyError, PubPrecursor.DoesNotExist):
                    data={'msg':"Precursor no esta activo o nunca fue precursor"}
               else:
                    precur.status=False
                    if precur.mesIni==hoy.month and precur.yearIni==hoy.year:
                         precur.duracion=getDiferenciaMes(precur.mesIni, precur.yearIni, hoy.month, hoy.year)+2
                    else:
                         precur.duracion=getDiferenciaMes(precur.mesIni, precur.yearIni, hoy.month, hoy.year)+1
                    precur.save()
                    data={'msg':"Precursor dado de baja"}
     return HttpResponse(json.dumps(data))

def yearServicio(request):
     bajaAuto()
     y=[]
     data={}
     pub=int(request.POST['pub'])
     request.session['pubprec']=pub
     prec=int(request.session['precur'])
     try:
          Precursor.objects.get(pk=prec)
     except(KeyError, Precursor.DoesNotExist):
          data={"msg":"tipo de Precursorado no existe"}
     else:
          try:
               Publicador.objects.get(pk=pub)
          except(KeyError, Publicador.DoesNotExist):
               data={'msg':"Publicador no existe"}
          else:
               if prec==2:
                    precur=PubPrecursor.objects.filter(Q(FKprecursor=prec) | Q(FKprecursor=1), FKpub=pub).order_by("-yearIni", "-mesIni")
               else:
                    precur=PubPrecursor.objects.filter(FKpub=pub, FKprecursor=prec).order_by("-yearIni", "-mesIni")
               if len(precur)>0:
                    for p in precur:
                         if p.status:
                              yearFin=datetime.date.today().year
                              mesFin=datetime.date.today().month
                         else:
                              fFin=getFechaFin(p.mesIni, p.yearIni, p.duracion)
                              mesFin=fFin[0]
                              yearFin=fFin[1]
                         for x in (arrayYear(p.mesIni, p.yearIni, mesFin, yearFin)):
                              y.append(x)
                    data={'years':quitarRep(y)}
               else:
                    data={'msg':"Esta persona nunca ha sido precursor."}
     return HttpResponse(json.dumps(data))

#metodos reutilizables
def arrayYear(mesI,yearI,mesF,yearF, normalY=0):
     years=[]
     intervaloY=yearF-yearI
     for i in range(0, intervaloY+1):
          if mesI<9:
               years.append([yearI-1,yearI])
          else:
               years.append([yearI, yearI+1])
          yearI+=1
     if mesI<9 and mesF>8:
          years.append([yearI-1,yearI])
     elif mesI>8 and mesF<9:
          years.pop()
     return years

def quitarRep(arreglo):
     arreglo.sort(reverse=True)
     cont=0
     cont2=0
     for i in arreglo:
          for j in arreglo:
               if i==j:
                    cont2+=1
                    if cont2>1:
                         arreglo.pop(cont)
          cont+=1
          cont2=0
     return arreglo

def getTiempo(precurs):
     tiempo=""
     mes=0
     year=0
     duracion=0
     hoy=datetime.date.today()
     for p in precurs:
          if p.duracion==0:
               dur=getDiferenciaMes(p.mesIni, p.yearIni, hoy.month, hoy.year)+1
          else:
               dur=p.duracion
          duracion+=dur
     for i in range(0, duracion):
          mes+=1
          if mes==12:
               year+=1
               mes=0
     if year>0:
          tiempo=str(year)+" anio"
          if year>1:
               tiempo+="s"
          if mes>0:
               tiempo+=" y "
     if mes>0:
          tiempo+=str(mes)+" mes"
          if mes>1:
               tiempo+="es"
     if len(precurs)==1 and precurs[0].mesIni==hoy.month and precurs[0].yearIni==hoy.year:
          tiempo="En curso"
     return tiempo
