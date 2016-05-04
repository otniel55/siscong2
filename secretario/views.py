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
from django.contrib.auth.models import User

def index(request):
     return render(request, 'layout.html', {'url':0})

def registrarGrupo(request):
     form = CrearGrupo()
     return render(request, 'regGrupo.html', {'form': form, 'url':1})

def validarVacio(elements, numerosKeys=[], fechaKeys=[]):
     elemento=[]
     vacio=True
     for i in elements.keys():
          if i in numerosKeys:
               try:
                    int(elements[i])
               except(ValueError):
                    vacio=False
                    elemento.append(i)
          elif i in fechaKeys:
               try:
                    datetime.date(int(elements[i][0:4]), int(elements[i][5:7]), int(elements[i][8:]))
               except(ValueError):
                    vacio=False
                    elemento.append(i)
          else:
               if elements[i].strip()=="":
                    vacio=False
                    elemento.append(i)
     return [vacio, elemento]

def grupos_registrar(request):
     msg={}
     validar=validarVacio(request.POST)
     if validar[0]:
          _encargado=request.POST['encargado'].upper()
          _auxiliar=request.POST['auxiliar'].upper()
          _encargado=_encargado.strip()
          _auxiliar=_auxiliar.strip()
          try:
               verificar = GruposPred.objects.get(encargado=_encargado)
          except(KeyError, GruposPred.DoesNotExist):
               grupo=GruposPred(encargado=_encargado, auxiliar=_auxiliar)
               grupo.save()
               msg={'msg':"Grupo Registrado con exito", 'on':1}
          else:
               msg = {'msg': "Este encargado se encuentra en otro grupo"}
     else:
          msg=msgVacio(validar[1])
     return  HttpResponse(json.dumps(msg))

def msgVacio(vacios):
     msg={}
     if len(vacios)>0:
          msg={'msg':"Por favor no intente hacer trampa"}
     return msg

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
     return render(request, 'conGrupo.html', {'form': cGrupo, 'onPub': on, 'url':1 })

def conGrupoofPubs(request, idGrupo):
     cGrupo = traerGrupo(initial={'Encargado': idGrupo})
     return render(request, 'conGrupo.html', {'form': cGrupo, 'onPub': 1, 'url':1 })

def datGrupo(request,idGrupo):
     try:
          g = GruposPred.objects.get(pk=idGrupo)
     except(KeyError, GruposPred.DoesNotExist):
          datos={"msg":"Este grupo no esta registrado"}
     else:
          request.session['conGrupoId']=idGrupo
          p = Publicador.objects.filter(FKgrupo=g.pk)
          formDatGrupo = CrearGrupo(instance=g)
          formPub = modalPub()
          modalGrupo = traerGrupo()
          modalInfo = regInforme()
          y=str(datetime.date.today().year-1)+""+str(datetime.date.today().year)
          datos = {'form': formDatGrupo, 'publicadores': p, 'num': g.pk, 'modalPub': formPub,
                 'modalGrupo': modalGrupo, 'modalInfo': modalInfo, 'y':y, 'url':1,
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
     bajaAuto()
     promInf=[]
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
               if status==0:
                    mesi=inf[0].mes
                    yeari=inf[0].year
                    mesi-=1
                    if mesi==0:
                         mesi=12
                         yeari-=1
                    informes=Informe.objects.filter(mes=mesi, year=yeari)
                    if len(informes)>0:
                         for infs in informes:
                              add=True
                              pre=PubPrecursor.objects.filter(FKpub=infs.FKpub.pk).order_by("-yearIni", "-mesIni")
                              if len(pre)>0:
                                   if pre[0].duracion==0:
                                        add=False
                                   else:
                                        fechaF=getFechaFin(pre[0].mesIni,pre[0].yearIni,pre[0].duracion)
                                        diferencia=getDiferenciaMes(fechaF[0],fechaF[1],mesi,yeari)
                                        if diferencia<0:
                                             add=False
                              if add:
                                   promInf.append(infs.horas)
                         if len(promInf)>0:
                              if prom(promInf)>inf[0].horas:
                                   status=4
          else:
               status=3
               intervalo="Este publicador nunca ha informado"
               fecha="Nulo"
          pubs[cont]={'nombre':i.nombre, 'apellido':i.apellido, 'fechaBau':i.fechaBau, 'edad':obteneredad(i), 'FKgrupo':i.FKgrupo, 'id':i.pk, 'g':i.FKgrupo.pk, 'status': status, 'intervalo': intervalo, 'fecha':fecha}
          cont=cont+1
     pubs=pubs.values()
     return render(request, 'conPubs.html',{'pub':pubs,'msg':msg, 'url':2})

def prom(nums):
     acum=0
     for i in nums:
          acum+=i
     if len(nums)>0:
          acum=acum//len(nums)
     return acum

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
     return render(request, 'regPubli.html', {'form': formPub, 'form2': cmbGrupo, 'url':2})

def publicReg(request):
     hoy=datetime.date.today()
     nums=['Encargado']
     vFechas=['fechaNa']
     validar=validarVacio(request.POST, nums, vFechas)
     if validar[0]:
          datosP=trimUpper(request.POST, ['email', 'fechaBau'])
          _nombre=datosP['nombre']
          _apellido=datosP['apellido']
          _telefono=datosP['telefono']
          _direccion =datosP['direccion']
          _email=datosP['email']
          _fechaBau=datosP['fechaBau']
          _fechaNa=datosP['fechaNa']
          _grupo=datosP['Encargado']
          edad=hoy.year-int(_fechaNa[0:4])-((hoy.month, hoy.day)<(int(_fechaNa[5:7]), (int(_fechaNa[8:]))))
          if edad>3:
               try:
                    pub=Publicador.objects.get(nombre=_nombre, apellido=_apellido, fechaNa=_fechaNa)
               except(KeyError, Publicador.DoesNotExist):
                    try:
                         g=GruposPred.objects.get(pk=_grupo)
                    except(KeyError, GruposPred.DoesNotExist):
                         msg={'msg':"El grupo no existe"}
                    else:
                         g.publicador_set.create(nombre=_nombre, apellido=_apellido, telefono=_telefono, direccion=_direccion,email=_email, fechaBau=_fechaBau, fechaNa=_fechaNa)
                         msg={'msg':"Publicador Registrado con exito", 'on':1}
               else:
                    msg={ 'msg': "Error! Este publicador ya esta registrado."}
          else:
               msg={'msg':"Error! Para ser registrado debe tener como minimo 4 anios"}
     else:
          msg=msgVacio(validar[1])
     return HttpResponse(json.dumps(msg))

def cambiarPub(request):
     validar=validarVacio(request.POST)
     if validar[0]:
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
     else:
          msg=msgVacio(validar[1])
     return HttpResponse(json.dumps(msg))

def traerPub(request, idpub):
     data={}
     try:
          p=Publicador.objects.get(pk=idpub)
     except(KeyError, Publicador.DoesNotExist):
          pg="page404.html"
     else:
          pg='regPubli.html'
          request.session['pub']=idpub
          formPub = regPub(instance=p)
          cmbGrupo = traerGrupo(initial={'Encargado': p.FKgrupo.pk})
          data={'form': formPub, 'form2':cmbGrupo, 'on': 1, 'url':2}
     return render(request, pg, data)

def modPub(request):
     nums=['Encargado']
     vFecha=['fechaNa']
     validar=validarVacio(request.POST,nums,vFecha)
     if validar[0]:
          datosP=trimUpper(request.POST,['fechaBau', 'email'])
          _nombre=datosP['nombre']
          _apellido=datosP['apellido']
          _telefono=datosP['telefono']
          _direccion =datosP['direccion']
          _email=datosP['email']
          _fechaBau=datosP['fechaBau']
          _fechaNa=datosP['fechaNa']
          _grupo=datosP['Encargado']
          try:
               _id=request.session['pub']
          except KeyError:
               msg="Error! Antes de modificar seleccione un publicador"
          else:
               p=Publicador.objects.get(pk=_id)
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
     else:
          msg="Error introdujo algun campo invalido"
     request.session['msgpub']=msg
     return HttpResponse(json.dumps({'msg':msg}))

def trimUpper(elements, no=[]):
     modElemets={}
     for i in elements.keys():
          if i not in no:
               try:
                    modElemets[i]=elements[i].upper().strip()
               except(AttributeError):
                    modElemets[i]=elements[i]
          else:
               modElemets[i]=elements[i]
     return modElemets

def modGrup(request):
     validar=validarVacio(request.POST)
     if validar[0]:
          datosG=trimUpper(request.POST)
          _encargado=datosG['enc']
          _auxiliar=datosG['aux']
          try:
               _pk=request.session['conGrupoId']
          except(KeyError):
               msg={'msg':'Seleccione un grupo.'}
          else:
               try:
                    g=GruposPred.objects.get(pk=_pk)
               except(KeyError, GruposPred.DoesNotExist):
                    msg={'msg':'Grupo no existe'}
               else:
                    g.encargado=_encargado
                    g.auxiliar=_auxiliar
                    g.save()
                    msg={'msg':'Grupo modificado con exito', 'on':1}
     else:
          msg=msgVacio(validar[1])
     return HttpResponse(json.dumps(msg))

def viewInfo(request):
     formInfo = regInforme()
     return render(request, 'regInforme.html', {'form': formInfo})

def regInf(request):
     hoy=datetime.date.today()
     nums=['horas', 'publicaciones', 'videos', 'revisitas', 'estudios', 'publicador']
     validar=validarVacio(request.POST, nums)
     if validar[0]:
          _horas = request.POST['horas']
          _publicaciones = request.POST['publicaciones']
          _videos = request.POST['videos']
          _revisitas = request.POST['revisitas']
          _estudios = request.POST['estudios']
          _fecha = request.POST['fecha']
          _pub=request.POST['publicador']
          if getDiferenciaMes(int(_fecha[0:2]), int(_fecha[3:]),hoy.month, hoy.year)>-2:
               try:
                    p=Publicador.objects.get(pk=_pub)
               except(KeyError, Publicador.DoesNotExist):
                    msg={'msg':'Publicador no existe'}
               else:
                    inf=Informe.objects.filter(mes=int(_fecha[0:2]), year=int(_fecha[3:]),FKpub=_pub)
                    if len(inf)==0:
                         p.informe_set.create(horas=_horas, publicaciones=_publicaciones, videos=_videos, revisitas=_revisitas, estudios=_estudios, mes=int(_fecha[0:2]), year=int(_fecha[3:]))
                         msg={'msg':'Informe Registrado con exito', 'on':1}
                    else:
                         msg={'msg':'Error informe ya existe'}
          else:
               msg={'msg':"No puede introducir un informe del futuro"}
     else:
          msg=msgVacio(validar[1])
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
          years.append([yearHoy-1, yearHoy])
          yearHoy=yearHoy-1
          cont+=1
     cGrupo = traerGrupo()
     return render(request, 'verTarjetaPub.html', {'form': cGrupo, 'years':years, 'url':2})

def editPrecur(request):
     return render(request, 'editPrecur.html', {'precur': Precursor.objects.all(), 'url':3})

def vistaNombrar(request):
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
               final=getFechaFin(precursor[0].mesIni, precursor[0].yearIni, precursor[0].duracion)
               mesI=final[0]
               yearI=final[1]
               if mesI==hoy.month and yearI==hoy.year:
                    pasar=False
          if pasar:
               p[cont]={'pk':x.pk, 'nombre':x.nombre, 'apellido':x.apellido, 'tiempoB':obteneredad(x, 1), 'fechaBau':x.fechaBau}
               cont=cont+1
     p=p.values()
     return render(request, 'nombrarPub.html', {'pub':p, 'precur':precur, 'url':3})

def NombrarPrecur(request):
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

def conPrec(request):
     bajaAuto()
     precur= precursorados()
     return render(request, 'conPrecur.html', {'precur':precur, 'url':3})

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
     hoy=datetime.date.today()
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
                                             data[cont] = {'fecha': datetime.date(f[0], f[1], 15), 'horasI':0, 'horasA':acum, 'horasRes':horasT-acum, 'obj':0, 'horastot':horasT}
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
                                             data[cont]={'fecha':datetime.date(f[0],f[1],15), 'horasI':inf.horas, 'horasA':acum, 'horasRes':horasT-acum, 'obj':obj, 'horasto':horasT}
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

def bajaAuto():
     hoy=datetime.date.today()
     precs=PubPrecursor.objects.filter(Q(FKprecursor=1) | Q(FKprecursor=2),status=True)
     for i in precs:
          if i.duracion!=0:
               fechaF=getFechaFin(i.mesIni,i.yearIni, i.duracion)
               diferenciaMes=getDiferenciaMes(fechaF[0],fechaF[1], hoy.month, hoy.year)
               if diferenciaMes>-1:
                    i.status=False
                    i.save()

def usuReg(request):
     return render(request, 'usuReg.html')

def Regusu(request):
     validar=validarVacio(request.POST)
     if validar[0]:
          nombre=request.POST['nombre']
          clave=request.POST['pass']
          try:
               newUser=User.objects.create_user(username=nombre, password=clave)
          except:
               msg={'msg':'Usuario ya existe'}
          else:
               newUser.is_staff=True
               newUser.save()
               msg={'msg':'Usuario registrado con exito', 'on':1}
     else:
          msg={'msg':'Por favor no intente hacer trampa'}
     return HttpResponse(json.dumps(msg))

def estadisticas(request):
    return render(request, "estadisticas.html", {})

def obtenerInf(mes, year, alreves=True):
     esp=False
     mesesReg=[]
     mesesAux=[]
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
     meses.sort(reverse=alreves)
     pu=Publicador.objects.all()
     for i in pu:
          infP=Informe.objects.filter(FKpub=i.pk).order_by("year", "mes")
          if len(infP)>0:
               primerInf.append(infP[0])
          infU=Informe.objects.filter(FKpub=i.pk).order_by("-year", "-mes")
          if len(infU)>0:
              ultimoInf.append(infU[0])
     for i in meses:
          precReg=0
          precAux=0
          precEsp=0
          irregulares=0
          inactivos=0
          pubs=0
          publicaciones = 0
          revisitas = 0
          estudios = 0
          horas = 0
          videos = 0
          strMes=str(i[1])
          if i[1]<10:
               strMes="0"+str(i[1])
          b=Publicador.objects.filter(fechaBau__startswith=str(i[0])+"-"+strMes)
          bau=len(b)
          for j in primerInf:
               if j.year==i[0] and j.mes==i[1]:
                    pubs+=1
          for j in ultimoInf:
               meses=getDiferenciaMes(j.mes,j.year,i[1],i[0])
               if meses>0 and meses<7:
                    irregulares+=1
               elif meses>6:
                    inactivos+=1
          informes = Informe.objects.filter(mes=i[1], year=i[0])
          for inf in informes:
               publicaciones += inf.publicaciones
               revisitas += inf.revisitas
               estudios += inf.estudios
               horas += inf.horas
               videos += inf.videos
          for k in pu:
               aux=False
               reg=False
               precurs=PubPrecursor.objects.filter(FKpub=k.pk, FKprecursor__in=[1,2]).order_by("-yearIni", "-mesIni")
               for l in precurs:
                    if getDiferenciaMes(l.mesIni, l.yearIni, i[1], i[0])>-2:
                         if l.duracion==0:
                              mesF=i[1]
                              yearF=i[0]
                         else:
                              fechaF=getFechaFin(l.mesIni, l.yearIni, l.duracion)
                              mesF=fechaF[0]
                              yearF=fechaF[1]
                         if getDiferenciaMes(i[1], i[0], mesF, yearF)>-2:
                              precAux+=1
                              aux=True
                              break
               if not aux:
                    precurs=PubPrecursor.objects.filter(FKpub=k.pk, FKprecursor=3).order_by("-yearIni", "-mesIni")
                    for l in precurs:
                         if getDiferenciaMes(l.mesIni, l.yearIni, i[1], i[0])>-2:
                              if l.duracion==0:
                                   mesF=i[1]
                                   yearF=i[0]
                              else:
                                   fechaF=getFechaFin(l.mesIni, l.yearIni, l.duracion)
                                   mesF=fechaF[0]
                                   yearF=fechaF[1]
                              if getDiferenciaMes(i[1], i[0], mesF, yearF)>-2:
                                   precReg+=1
                                   reg=True
                                   break
               elif not reg:
                    precurs=PubPrecursor.objects.filter(FKpub=k.pk, FKprecursor=4).order_by("-yearIni", "-mesIni")
                    for l in precurs:
                         if getDiferenciaMes(l.mesIni, l.yearIni, i[1], i[0])>-2:
                              if l.duracion==0:
                                   mesF=i[1]
                                   yearF=i[0]
                              else:
                                   fechaF=getFechaFin(l.mesIni, l.yearIni, l.duracion)
                                   mesF=fechaF[0]
                                   yearF=fechaF[1]
                              if getDiferenciaMes(i[1], i[0], mesF, yearF)>-2:
                                   precEsp+=1
                                   esp=True
                                   break

          mes = i[1]
          year = i[0]
          mes -= 1
          if mes == 0:
               mes = 12
               year -= 1
          informesAnt = Informe.objects.filter(mes=mes, year=year)
          p=0
          r=0
          e=0
          h=0
          v=0
          auxAnt=0
          pubsAnt=0
          regAnt=0
          espAnt=0
          strMes=str(mes)
          if mes<10:
               strMes="0"+str(mes)
          b=Publicador.objects.filter(fechaBau__startswith=str(year)+"-"+strMes)
          bauAnt=len(b)
          irregularesAnt=0
          inactivosAnt=0
          for inf in informesAnt:
               p += inf.publicaciones
               r += inf.revisitas
               e += inf.estudios
               h += inf.horas
               v += inf.videos
          if len(informesAnt)>0:
               for k in pu:
                    aux=False
                    reg=False
                    precurs=PubPrecursor.objects.filter(FKpub=k.pk, FKprecursor__in=[1,2]).order_by("-yearIni", "-mesIni")
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
                                   auxAnt+=1
                                   aux=True
                                   break
                    if not aux:
                         precurs=PubPrecursor.objects.filter(FKpub=k.pk, FKprecursor=3).order_by("-yearIni", "-mesIni")
                         for l in precurs:
                              if getDiferenciaMes(l.mesIni, l.yearIni, mes, year)>-2:
                                   if l.duracion==0:
                                        mesF=i[1]
                                        yearF=i[0]
                                   else:
                                        fechaF=getFechaFin(l.mesIni, l.yearIni, l.duracion)
                                        mesF=mes
                                        yearF=year
                                   if getDiferenciaMes(mes, year, mesF, yearF)>-2:
                                        regAnt+=1
                                        reg=True
                                        break
                    elif not reg:
                         precurs=PubPrecursor.objects.filter(FKpub=k.pk, FKprecursor=4).order_by("-yearIni", "-mesIni")
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
                                        espAnt+=1
                                        esp=True
                                        break
               for j in primerInf:
                    if j.mes==mes and j.year==year:
                         pubsAnt+=1
               for j in ultimoInf:
                    meses=getDiferenciaMes(j.mes,j.year,mes,year)
                    if meses>0 and meses<7:
                         irregularesAnt+=1
                    elif meses>6:
                         inactivosAnt+=1
               if publicaciones==0:
                    resultP=p*-100
               else:
                    try:
                         resultP = ((publicaciones*100)//p)-100
                    except ZeroDivisionError:
                         resultP = (((publicaciones+1)*100)//(p+1))-100
               if revisitas==0:
                    resultR=r*-100
               else:
                    try:
                         resultR = ((revisitas*100)//r)-100
                    except ZeroDivisionError:
                         resultR = (((revisitas+1)*100)//(r+1))-100
               if estudios==0:
                    resultE=e*-100
               else:
                    try:
                         resultE = ((estudios*100)//e)-100
                    except ZeroDivisionError:
                         resultE = (((estudios+1)*100)//(e+1))-100
               if horas==0:
                    resultH=h*-100
               else:
                    try:
                         resultH = ((horas*100)//h)-100
                    except ZeroDivisionError:
                         resultH = (((horas+1)*100)//(h+1))-100
               if videos==0:
                    resultV=v*-100
               else:
                    try:
                         resultV = ((videos*100)//v)-100
                    except ZeroDivisionError:
                          resultV = (((videos+1)*100)//(v+1))-100
               if pubs==0:
                    resultPubs=pubsAnt*-100
               else:
                    try:
                         resultPubs=((pubs*100)//pubsAnt)-100
                    except ZeroDivisionError:
                         resultPubs=(((pubs+1)*100)//(pubsAnt+1))-100
               if bau==0:
                    resultBau=bauAnt*-100
               else:
                    try:
                         resultBau=((bau*100)//bauAnt)-100
                    except ZeroDivisionError:
                         resultBau=(((bau+1)*100)//(bauAnt+1))-100
               if irregulares==0:
                    resultI=irregularesAnt*100
               else:
                    try:
                         resultI=(((irregulares*100)//irregularesAnt)-100)*-1
                    except ZeroDivisionError:
                         resultI=((((irregulares+1)*100)//(irregularesAnt+1))-100)*-1
               if inactivos==0:
                    resultInac=inactivosAnt*100
               else:
                    try:
                         resultInac=(((inactivos*100)//inactivosAnt)-100)*-1
                    except ZeroDivisionError:
                         resultInac=((((inactivos+1)*100)//(inactivosAnt+1))-100)*-1
               if precAux==0:
                    resultAux=auxAnt*-100
               else:
                    try:
                         resultAux=((precAux*100)//auxAnt)-100
                    except ZeroDivisionError:
                         resultAux=(((precAux+1)*100)//(auxAnt+1))-100
               if precReg==0:
                    resultReg=regAnt*-1
               else:
                    try:
                         resultReg=((precReg*100)//regAnt)-100
                    except ZeroDivisionError:
                         resultReg=(((precReg+1)*100)//(regAnt+1))-100
               suma = resultP+resultR+resultE+resultH+resultV+resultPubs+resultBau+resultI+resultInac+resultAux+resultReg
               total=suma//11
               sumaAbs = abs(resultP) + abs(resultR) + abs(resultE) + abs(resultH) + abs(resultV) + abs(resultPubs) + abs(resultBau) + abs(resultI) + abs(resultInac) + abs(resultAux) + abs(resultReg)
          else:
               total="No hubo informes en el mes pasado, no se puede comparar"
          if len(informes) > 0:
               data[cont] = {'publicaciones': publicaciones, 'revisitas': revisitas, 'estudios': estudios,
                             'horas': horas, 'videos': videos, 'mes':i[1], 'result':total, 'pubs':pubs, 'bau':bau, 'irreg':irregulares, 'inactivos':inactivos, 'aux':precAux, 'reg':precReg}
               if esp:
                    data[cont]['esp']=precEsp
               if len(informesAnt)>0:
                    data[cont]['torta']={
                              'publicaciones':resultP, 'revisitas':resultR, 'estudios':resultE, 'horas':resultH, 'videos':resultV, 'pubs':resultPubs, 'bau':resultBau, 'irreg':resultI, 'inactivos':resultInac, 'aux':resultAux, 'reg':resultReg
                         }
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
     return data

def calculo(nro, base):
     try:
          resultado=(nro*100)/base
          resultado=str(resultado)
          resultado=resultado[:resultado.find(".")+3]
     except ZeroDivisionError:
          resultado=nro*100
     return resultado


def infG(request):
     cont=0
     data={}
     meses=[]
     try:
          mes=int(request.POST['fecha'][0:2])
          year=int(request.POST['fecha'][3:])
     except:
          data={'msg':"No intente hacer trampa"}
     else:
          data=obtenerInf(mes,year)
     return HttpResponse(json.dumps(data))

def infPrec(request):
     return render(request, "estadisticasPrec.html", {})

def conInfPrec(request):
     cont = 0
     data = {}
     try:
          mes = int(request.POST['fecha'][0:2])
          year = int(request.POST['fecha'][3:])
     except:
          data = {'msg': "No intente hacer trampa"}
     else:
          meses = []
          meses.append([year, mes])
          for i in range(1, 6):
               mes -= 1
               if mes == 0:
                    mes = 12
                    year -= 1
               meses.append([year, mes])
          meses.sort(reverse=True)
          precurs = PubPrecursor.objects.all().order_by("-yearIni", "-mesIni")
          for i in meses:
               promH = []
               promE = []
               promR = []
               contP = 0
               data[cont]={'mes':i[1], 'year':i[0]}
               for p in precurs:
                    if getDiferenciaMes(p.mesIni, p.yearIni, i[1], i[0]) > -2:
                         if p.duracion == 0:
                              mesF = i[1]
                              yearF = i[0]
                         else:
                              fechaF = getFechaFin(p.mesIni, p.yearIni, p.duracion)
                              mesF = fechaF[0]
                              yearF = fechaF[1]
                         if getDiferenciaMes(i[1], i[0], mesF, yearF) > -2:
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
          meses = []
          meses.append([year, mes])
          for i in range(1, 6):
               mes -= 1
               if mes == 0:
                    mes = 12
                    year -= 1
               meses.append([year, mes])
          meses.sort(reverse=True)
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
                              if getDiferenciaMes(p.mesIni, p.yearIni, i[1], i[0]) > -2:
                                   if p.duracion == 0:
                                        mesF = i[1]
                                        yearF = i[0]
                                   else:
                                        fechaF = getFechaFin(p.mesIni, p.yearIni, p.duracion)
                                        mesF = fechaF[0]
                                        yearF = fechaF[1]
                                   if getDiferenciaMes(i[1], i[0], mesF, yearF) > -2:
                                        add=False
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

def estPub(request):
     return render(request, "estPub.html", {})

def estGlobal(request):
     return render(request, "estCong.html", {})
