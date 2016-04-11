from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from .forms import *
from django.core.urlresolvers import reverse
from secretario.models import *
from django.views import generic
import json
import datetime
from django.utils import timezone
from django.db.models import Q

def index(request):
     return render(request, 'layout.html', {})

def registrarGrupo(request):
     form = CrearGrupo()
     return render(request, 'regGrupo.html', {'form': form})

def grupos_registrar(request):
     _encargado=request.POST['encargado'].upper()
     _auxiliar=request.POST['auxiliar'].upper()
     try:
          verificar = GruposPred.objects.get(encargado=_encargado)
     except(KeyError, GruposPred.DoesNotExist):
          grupo=GruposPred(encargado=_encargado, auxiliar=_auxiliar)
          grupo.save()
          msg={'msg':"Grupo Registrado con exito"}
     else:
          msg = {'msg': "Este encargado se encuentra en otro grupo"}
     return  HttpResponse(json.dumps(msg))
        
def conGrupo(request):
     try:
          request.session['idgrupo']
     except KeyError:
          cGrupo = traerGrupo()
          on = 0
     else:
          fkgrupo = request.session['idgrupo']
          if fkgrupo == "":
               cGrupo = traerGrupo()
               on = 0
          else:
               cGrupo = traerGrupo(initial={'Encargado': fkgrupo })
               request.session['idgrupo']=""
               on = 1

     return render(request, 'conGrupo.html', {'form': cGrupo, 'onPub': on })

def conGrupoofPubs(request, idGrupo):
     cGrupo = traerGrupo(initial={'Encargado': idGrupo})
     return render(request, 'conGrupo.html', {'form': cGrupo, 'onPub': 1 })

def datGrupo(request,idGrupo):
     g = GruposPred.objects.get(pk=idGrupo)
     p = Publicador.objects.filter(FKgrupo=g.pk)

     formDatGrupo = CrearGrupo(instance=g)
     formPub = modalPub()
     modalGrupo = traerGrupo()
     modalInfo = regInforme()
     mes = mesInfor()
     y=datetime.date.today().year
     datos = {'form': formDatGrupo, 'publicadores': p, 'num': g.pk, 'modalPub': formPub, 
            'modalGrupo': modalGrupo, 'modalInfo': modalInfo, 'mes': mes,'y':y,
            }
     return render(request, 'datGrupo.html',datos)

def conPub(request):
     cont=0
     try:
        p=Publicador.objects.get(pk=request.POST['id'])
     except(KeyError, Publicador.DoesNotExist):
        return HttpResponse(json.dumps({'msg':'Error, Publicador no existe'}))
     else:
          p={'nombre':p.nombre, 'apellido':p.apellido,'grupo':p.FKgrupo.pk}
          datos={'pub':p}
          return HttpResponse(json.dumps(datos))

def conPubs(request):
     try:
          request.session['msgpub']
     except KeyError:
          msg=""
     else:
          msg=request.session['msgpub']
          request.session['msgpub']=""
     c=[]
     cont=0
     pubs={}
     p=Publicador.objects.all()
     for i in p:
          inf=Informe.objects.filter(FKpub=i.pk).order_by("-year", "-mes")
          if len(inf)>0:
               status=obtenerStatus(inf[0].mes, inf[0].year)[0]
               intervalo=obtenerStatus(inf[0].mes, inf[0].year)[1]
               fecha=str(inf[0].mes)+"-"+str(inf[0].year)
          else:
               status=3
               intervalo="Este publicador nunca ha informado"
               fecha="Nulo"
          pubs[cont]={'nombre':i.nombre, 'apellido':i.apellido, 'fechaBau':i.fechaBau, 'edad':obteneredad(i), 'FKgrupo':i.FKgrupo, 'id':i.pk, 'g':i.FKgrupo.pk, 'status': status, 'intervalo': intervalo, 'fecha':fecha}
          cont=cont+1
     pubs=pubs.values()
     return render(request, 'conPubs.html',{'pub':pubs,'msg':msg})

def getDiferenciaMes(mesI, yearI, mesF, yearF):
     if yearF==yearI:
          meses=(mesF-1)-mesI
     else:
          mesYear=(yearF-yearI)*12
          mesYear=mesYear-mesI
          meses=mesYear+(mesF-1)
     return meses

def obtenerStatus(mes, year):
     hoy=datetime.date.today()
     meses=getDiferenciaMes(mes,year,hoy.month,hoy.year)
     if meses<1:
          meses=0
          status=0
     elif meses>0 and meses<7:
          status=1
     else:
          status=2
     return (status, meses)

def obteneredad(persona, tb=0):
     hoy=datetime.date.today()
     if tb==0:
          fecha=persona.fechaNa
     else:
          year=int(persona.fechaBau[0:4])
          mes=int(persona.fechaBau[5:7])
          dia=int(persona.fechaBau[8:])
          fecha=datetime.date(year,mes,dia)
     return hoy.year-fecha.year-((hoy.month, hoy.day)<(fecha.month, fecha.day))

def regPubli(request):
     formPub = regPub()
     cmbGrupo = traerGrupo()
     return render(request, 'regPubli.html', {'form': formPub, 'form2': cmbGrupo})

def publicReg(request):
     _nombre=request.POST['nombre'].upper()
     _apellido=request.POST['apellido'].upper()
     _telefono=request.POST['telefono']
     _direccion =request.POST['direccion'].upper()
     _email=request.POST['email'].upper()
     _fechaBau=request.POST['fechaBau']
     _fechaNa=request.POST['fechaNa']
     _grupo=request.POST['Encargado']
     try:
          pub=Publicador.objects.get(nombre=_nombre, apellido=_apellido, fechaNa=_fechaNa)
     except(KeyError, Publicador.DoesNotExist):
          try:
               g=GruposPred.objects.get(pk=_grupo)
          except(KeyError, GruposPred.DoesNotExist):
               msg={'msg':"El grupo no existe"}
          else:
               g.publicador_set.create(nombre=_nombre, apellido=_apellido, telefono=_telefono, direccion=_direccion,email=_email, fechaBau=_fechaBau, fechaNa=_fechaNa)
               msg={'msg':"Publicador Registrado con exito"}
     else:
          msg={ 'msg': "Error! Este publicador ya esta registrado."}
     return HttpResponse(json.dumps(msg))

def cambiarPub(request):
     _p=request.POST['id']
     _g=request.POST['grupo']
     try:
          p=Publicador.objects.get(pk=_p)
     except(KeyError, Publicador.DoesNotExist):
          msg={'msg':'Publicador no existe'}
     else:
          try:
               g=GruposPred.objects.get(pk=_g)
          except(KeyError, GruposPred.DoesNotExist):
               msg={'msg':'Grupo no existe'}
          else:
               if p.FKgrupo.pk!=g.pk:
                    Publicador.objects.filter(pk=_p).update(FKgrupo=g)
                    msg={'msg':'El publicador ha sido movido con exito', 'on':1}
               else:
                    msg={'msg':'No hubo ningun cambio realizado'}
     return HttpResponse(json.dumps(msg))

def traerPub(request, idpub):
     request.session['pub']=idpub
     p=Publicador.objects.get(pk=idpub)
     formPub = regPub(instance=p)
     cmbGrupo = traerGrupo(initial={'Encargado': p.FKgrupo.pk})
     return render(request, 'regPubli.html', {'form': formPub, 'form2':cmbGrupo, 'on': 1})

def modPub(request):
     _nombre=request.POST['nombre'].upper()
     _apellido=request.POST['apellido'].upper()
     _telefono=request.POST['telefono']
     _direccion =request.POST['direccion'].upper()
     _email=request.POST['email'].upper()
     _fechaBau=request.POST['fechaBau']
     _fechaNa=request.POST['fechaNa']
     _grupo=request.POST['Encargado']
     _id=request.session['pub']
     try:
        p=Publicador.objects.get(pk=_id)
     except(KeyError, Publicador.DoesNotExist):
        msg='Error, publicador no registrado'
     else:
          try:
               g=GruposPred.objects.get(pk=_grupo)
          except(KeyError, GruposPred.DoesNotExist):
               msg='Grupo no existe'
          else:
               Publicador.objects.filter(pk=_id).update(FKgrupo=_grupo)
               p.nombre=_nombre
               p.apellido=_apellido
               p.telefono=_telefono
               p.direccion=_direccion
               p.email=_email
               p.fechaBau=_fechaBau
               p.fechaNa=_fechaNa
               p.save()
               msg='Publicador modificado con exito'
     request.session['msgpub']=msg
     return render(request, 'conPubs.html')

def modGrup(request):
     _encargado=request.POST['enc']
     _auxiliar=request.POST['aux']
     _pk=request.POST['id']
     try:
          g=GruposPred.objects.get(pk=_pk)
     except(KeyError, GruposPred.DoesNotExist):
          msg={'msg':'Grupo no existe'}
     else:
          g.encargado=_encargado
          g.auxiliar=_auxiliar
          g.save()
          msg={'msg':'Grupo modificado con exito', 'on':1}
     return HttpResponse(json.dumps(msg))

def viewInfo(request):
     formInfo = regInforme()
     return render(request, 'regInforme.html', {'form': formInfo})

def regInf(request):
     pass
     _horas = request.POST['horas']
     _publicaciones = request.POST['publicaciones']
     _videos = request.POST['videos']
     _revisitas = request.POST['revisitas']
     _estudios = request.POST['estudios']
     _fecha = request.POST['fecha']
     _pub=request.POST['publicador']
     try:
          p=Publicador.objects.get(pk=_pub)
     except(KeyError, Publicador.DoesNotExist):
          msg={'msg':'Publicador no existe'}
     else:
          inf=Informe.objects.filter(mes=int(_fecha[0:2]), year=int(_fecha[3:]),FKpub=_pub)
          if len(inf)==0:
               p.informe_set.create(horas=_horas, publicaciones=_publicaciones, videos=_videos, revisitas=_revisitas, estudios=_estudios, mes=int(_fecha[0:2]), year=int(_fecha[3:]))
               msg={'msg':'Informe Registrado con exito'}
          else:
               msg={'msg':'Informe ya Fue registrado'}
     return HttpResponse(json.dumps(msg))

def tarjeta(request, vista, idPub, y):
     p=Publicador.objects.get(pk=idPub)
     request.session['idgrupo'] = p.FKgrupo.pk
     inf=Informe.objects.filter(year=y, FKpub=idPub).order_by('mes')
     if len(inf)>0:
          request.session['tarjetaPub']=idPub
          request.session['tarjetaY']=y
          datos={'pub':inf, 'p':p}
     else:
          datos={'vacio':1}

     if vista == '1':
          pagina = 'conTarjetaGrupoPub.html'
     else:
          pagina = 'tarjetaPub.html'

     return render(request, pagina , datos)

def modInf(request):
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
               msg={"msg":"Usted no ha realizado ningún cambio"}
          else:
               inf.horas=horas
               inf.revisitas=revisitas
               inf.estudios=estudios
               inf.publicaciones=publicaciones
               inf.videos=videos
               inf.save()
               msg={"msg":"Datos del informe modificados con exito"}
     HttpResponse(json.dumps(msg))



def conPubG(request):
     cont=0
     pubs={}
     grupo=request.POST['g']
     try:
          g=GruposPred.objects.get(pk=grupo)
     except:
          datos={'on':1, 'msg':"Error grupo no existe"}
     else:
          p=Publicador.objects.filter(FKgrupo=g)
          if len(p)>0:
               for i in p:
                    pubs[cont]={'id':i.pk, 'nombre':i.nombre, 'apellido':i.apellido}
                    cont+=1
               datos={'p':pubs}
          else:
               datos={'on':1, 'msg':'Este grupo no tiene ningun publcador'}
     return HttpResponse(json.dumps(datos))

def verTarjetaPub(request):
     years=[]
     cont=0
     yearHoy=datetime.date.today().year
     while cont<5:
          years.append(yearHoy)
          yearHoy=yearHoy-1
          cont+=1
     cGrupo = traerGrupo()
     return render(request, 'verTarjetaPub.html', {'form': cGrupo, 'years':years})

def editPrecur(request):
     return render(request, 'editPrecur.html', {'precur': Precursor.objects.all()})

def vistaNombrar(request):
     cont=0
     p={}
     pubs=Publicador.objects.exclude(fechaBau__startswith="No").exclude(pubprecursor__status=True)
     precur= precursorados()
     for x in pubs:
          p[cont]={'pk':x.pk, 'nombre':x.nombre, 'apellido':x.apellido, 'tiempoB':obteneredad(x, 1), 'fechaBau':x.fechaBau}
          cont=cont+1
     p=p.values()
     return render(request, 'nombrarPub.html', {'pub':p, 'precur':precur})

def NombrarPrecur(request):
     validaciones=True
     cont=0
     msg={}
     p=json.loads(request.POST['pub'])
     mes=request.POST['fechaIni'][0:2]
     year=request.POST['fechaIni'][3:]
     for x in p:
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
                              if len(precurs)==0:
                                   diferencia=0
                              else:
                                   iniF=getFechaFin(precurs[0].mesIni,precurs[0].yearIni,precurs[0].duracion)
                                   iniMes=iniF[0]
                                   iniYear=iniF[1]
                                   diferencia=getDiferenciaMes(iniMes,iniYear, mes, year)
                              if diferencia>-1:
                                   pubP = PubPrecursor(FKpub=pub, FKprecursor=prec, duracion=x['duracion'], mesIni=mes, yearIni=year, status=True)
                                   pubP.save()
                                   if prec.pk in (3, 4):
                                        try:
                                             nro=nroPrec.objects.get(FKpub=pub.pk)
                                        except(KeyError, nroPrec.DoesNotExist):
                                             pub.nroprec_set.create(nroPrec=request.POST['nroPrec'])
                                   msg[cont] = {'msg': 'el publicador' + x['id'] + 'fue nombrado con exito'}
                              else:
                                   msg[cont] = {'msg': 'el publicador' + x['id'] + 'tenia un precursorado activo en la fecha que usted acaba de asignar'}
                         else:
                              msg[cont] = {'msg': 'el publicador' + x['id'] + 'no esta bautizado'}
                              validaciones=False
          cont += 1
     if validaciones:
          msg={'msg':'Los publicadores han sido nombrados precursores.'}
     else:
          msg=msg.values()
     return HttpResponse(json.dumps(msg))

def conPrec(request):
     precur= precursorados()
     return render(request, 'conPrecur.html', {'precur':precur})

def conPrecs(request):
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
                    p=Publicador.objects.filter(Q(pubprecursor__FKprecursor=1) | Q(pubprecursor__FKprecursor=2), pubprecursor__status=status)
               else:
                    p=Publicador.objects.filter(pubprecursor__FKprecursor=prec, pubprecursor__status=status)
          else:
               if prec==2 or prec==1:
                    p=Publicador.objects.filter(Q(pubprecursor__FKprecursor=1) | Q(pubprecursor__FKprecursor=2), pubprecursor__status=status).exclude(pubprecursor__status=not status)
               else:
                    p=Publicador.objects.filter(pubprecursor__FKprecursor=prec, pubprecursor__status=status).exclude(pubprecursor__status=not status)
          if len(p)>0:
               for i in p:
                    precs[cont]={'pk':i.pk, 'nombre':i.nombre+" "+i.apellido}
                    cont+=1
               data = {'p':precs}
          else:
               data={'msg':'No hay ningun registro de este tipo de precursor'}
     return HttpResponse(json.dumps(data))

def historiaPrec(request, year):
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
          iniM=1
          iniY=int(year)
          finM=12
          finY=int(year)
     elif prec==3 or prec==4:
          pg="tarjetaPrecReg.html"
          entrar=True
          iniM=9
          iniY=int(year[0:4])
          finM=8
          finY=int(year[4:])
     else:
          pg="tarjetaPrecAux.html"
          data={'msg':"Tipo de precursorado no existe"}
     if entrar:
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
                              lol=str(mesFin)+"-"+str(yearFin)
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
                                        duracion=getDiferenciaMes(pre.mesIni,pre.yearIni,fMonth,fYear)+1
                                   else:
                                        fEnd=getFechaFin(pre.mesIni,pre.yearIni,pre.duracion)
                                        fMonth=fEnd[0]
                                        fYear=fEnd[1]
                                        duracion=pre.duracion
                              else:
                                   fEnd=getFechaFin(pre.mesIni,pre.yearIni,pre.duracion)
                                   fMonth=fEnd[0]
                                   fYear=fEnd[1]
                                   duracion=pre.duracion
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
                                             horasT=(12-(f[1]-iniM))*f[2]
                                        else:
                                             horasT=len(mesPrecur)*f[2]
                                   try:
                                        inf=Informe.objects.get(FKpub=pub, mes=f[1], year=f[0])
                                   except(KeyError, Informe.DoesNotExist):
                                        if request.session['precur'] in (1, 2):
                                             data[cont]={'fecha':datetime.date(f[0],f[1],15), 'horasR':f[2], 'horasI':0, 'obj':0}
                                        else:
                                             data[cont] = {'fecha': datetime.date(f[0], f[1], 15), 'horasI':0, 'horasA':acum, 'horasRes':horasT-acum, 'obj':0}
                                   else:
                                        if request.session['precur'] in (1,2):
                                             if inf.horas>=f[2]:
                                                  obj=1
                                             else:
                                                  obj=0
                                             data[cont]={'fecha':datetime.date(f[0],f[1],15), 'horasR':f[2], 'horasI':inf.horas, 'obj':obj}
                                        else:
                                             acum+=inf.horas
                                             if acum>=f[2]*(cont):
                                                  obj=1
                                             else:
                                                  obj=0
                                             data[cont]={'fecha':datetime.date(f[0],f[1],15), 'horasI':inf.horas, 'horasA':acum, 'horasRes':horasT-acum, 'obj':obj}
                                   cont=cont+1
                         else:
                              precursor=Precursor.objects.get(pk=request.session['precur'])
                              horasR=precursor.horas
                              if request.session['precur'] in (1, 2):
                                   data[cont] = {'fecha': datetime.date(hoy.year, hoy.month, 15), 'horasR': horasR, 'horasI': "En curso",'obj': 2}
                              else:
                                   data[cont] = {'fecha': datetime.date(hoy.year, hoy.month, 15), 'horasI': "En curso", 'horasA': 0,'horasRes': horasR*12, 'obj': 2}
                         data=data.values()
                    else:
                         data={'msg':"Esta persona no fue precursor en el periodo "+year}
               else:
                    data={'msg':"Este Publicador nunca ha sido precursor"}
     return render(request, pg, {'ficha':ficha, 'datos':data})

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
     return tiempo


def yearServicio(request):
     normalY=0
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
                    normalY=1
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
                         for x in (arrayYear(p.mesIni, p.yearIni, mesFin, yearFin, normalY)):
                              y.append(x)
                    data={'years':quitarRep(y)}
               else:
                    data={'msg':"Esta persona nunca ha sido precursor."}
     return HttpResponse(json.dumps(data))

def getFechaFin(mesI, yearI, duracion):
     for i in range(1, duracion):
          mesI+=1
          if mesI==13:
               mesI=1
               yearI+=1
     fecha=[mesI, yearI]
     return fecha

def arrayYear(mesI,yearI,mesF,yearF, normalY=0):
     years=[]
     intervaloY=yearF-yearI
     for i in range(0, intervaloY+1):
          if normalY==1:
               years.append(yearI)
          else:
               if mesI<9:
                    years.append([yearI-1,yearI])
               else:
                    years.append([yearI, yearI+1])
          yearI+=1
     if normalY==0:
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
                    precur.duracion=getDiferenciaMes(precur.mesIni, precur.yearIni, hoy.month, hoy.year)+1
                    precur.save()
                    data={'msg':"Precursor dado de baja"}
          return HttpResponse(json.dumps(data))


