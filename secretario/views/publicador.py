#libs propios de python
import datetime
import json
#modulos de django
from django.http import HttpResponse
from django.shortcuts import render
#modulos propios del proyecto
from ..forms import traerGrupo, regPub
from .siscong import *
from secretario.models import GruposPred, Publicador, Informe

def vistaRegistrar(request):
     formPub = regPub()
     cmbGrupo = traerGrupo()
     return render(request, 'Publicador/regPubli.html', {'form': formPub, 'form2': cmbGrupo, 'url':2})

def registrar(request):
     hoy=datetime.date.today()
     nums=['Encargado']
     vFechas=['fechaNa']
     validar=gestion(request.POST,nums,vFechas)
     if not validar.error:
          validar.ignore=['email', 'fechaBau']
          datosP=validar.trimUpper()
          _nombre=datosP['nombre']
          _apellido=datosP['apellido']
          _telefono=datosP['telefono']
          _direccion =datosP['direccion']
          _email=datosP['email']
          _fechaBau=datosP['fechaBau']
          _fechaNa=datosP['fechaNa']
          _grupo=datosP['Encargado']
          edad=getEdad(datetime.date(int(_fechaNa[0:4]),int(_fechaNa[5:7]), int(_fechaNa[8:])), hoy)
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
          msg=validar.mensaje
     return HttpResponse(json.dumps(msg))

def consultarNameGroup(request):
     try:
        p=Publicador.objects.get(pk=request.POST['id'])
     except(KeyError, Publicador.DoesNotExist):
        return HttpResponse(json.dumps({'msg':'Error, Publicador no existe'}))
     else:
          p={'nombre':p.nombre, 'apellido':p.apellido,'grupo':p.FKgrupo.pk}
          datos={'pub':p}
          return HttpResponse(json.dumps(datos))

def cambiarPub(request):
     n=['id','grupo']
     validar=gestion(request.POST,n)
     if not validar.error:
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
          msg=validar.mensaje
     return HttpResponse(json.dumps(msg))

def consultarTodos(request):
     hoy=datetime.date.today()
     bajaAuto()
     promInf=[]
     try:
          request.session['msgpub']
     except KeyError:
          msg=""
     else:
          msg=request.session['msgpub']
          del request.session['msgpub']
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
          pubs[cont]={'nombre':i.nombre, 'apellido':i.apellido, 'fechaBau':i.fechaBau, 'edad':getEdad(i.fechaNa, hoy), 'FKgrupo':i.FKgrupo, 'id':i.pk, 'g':i.FKgrupo.pk, 'status': status, 'intervalo': intervalo, 'fecha':fecha}
          cont=cont+1
     pubs=pubs.values()
     return render(request, 'Publicador/conPubs.html',{'pub':pubs,'msg':msg, 'url':2})

def consultar(request, idpub):
     fechaNa=""
     data={}
     try:
          p=Publicador.objects.get(pk=idpub)
     except(KeyError, Publicador.DoesNotExist):
          pg="page404.html"
     else:
          pg='Publicador/regPubli.html'
          request.session['pub']=idpub
          formPub = regPub(instance=p)
          cmbGrupo = traerGrupo(initial={'Encargado': p.FKgrupo.pk})
          mes=p.fechaNa.month
          day=p.fechaNa.day
          fechaNa=str(p.fechaNa.year)+"-"+addZero(p.fechaNa.month)+"-"+addZero(p.fechaNa.day)
          data={'form': formPub, 'form2':cmbGrupo, 'on': 1, 'url':2, 'fechaNa':fechaNa, 'fechaBau':p.fechaBau}
     return render(request, pg, data)

def addZero(num):
     if num<10:
          num="0"+str(num)
     return str(num)

def modPub(request):
     hoy=datetime.date.today()
     nums=['Encargado']
     vFecha=['fechaNa']
     validar=gestion(request.POST,nums,vFecha, msg="Error introdujo algun campo incorrecto")
     if not validar.error:
          validar.ignore=['fechaBau', 'email']
          datosP=validar.trimUpper()
          _nombre=datosP['nombre']
          _apellido=datosP['apellido']
          _telefono=datosP['telefono']
          _direccion =datosP['direccion']
          _email=datosP['email']
          _fechaBau=datosP['fechaBau']
          _fechaNa=datosP['fechaNa']
          _grupo=datosP['Encargado']
          edad=getEdad(datetime.date(int(_fechaNa[0:4]),int(_fechaNa[5:7]), int(_fechaNa[8:])), hoy)
          if edad>3:
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
               msg="El minimo de edad aceptable es 4 anios en adelante"
     else:
          msg=validar.mensaje
     request.session['msgpub']=msg
     return HttpResponse(json.dumps({'msg':msg}))