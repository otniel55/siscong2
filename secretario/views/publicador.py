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
     sesionGrupo(request)
     formPub = regPub()
     cmbGrupo = traerGrupo()
     return render(request, 'Publicador/regPubli.html', {'form': formPub, 'form2': cmbGrupo, 'url':2})

def registrar(request):
     hoy=datetime.date.today()
     vFechas=['fechaNa']
     validar=gestion(request.POST,[],vFechas)
     validar.ignore=['active']
     validar.validar()
     if not validar.error:
          validar.ignore.append('email')
          validar.ignore.append('fechaBau')
          datosP=validar.trimUpper()
          _nombre=datosP['nombre']
          _apellido=datosP['apellido']
          _telefono=datosP['telefono']
          _direccion =datosP['direccion']
          _email=datosP['email']
          _fechaBau=datosP['fechaBau']
          _fechaNa=datosP['fechaNa']
          _sexo=datosP['sexo']
          if _sexo in ["F", "M"]:
               edad=getEdad(datetime.date(int(_fechaNa[0:4]),int(_fechaNa[5:7]), int(_fechaNa[8:])), hoy)
               if edad>3:
                    try:
                         pub=Publicador.objects.get(nombre=_nombre, apellido=_apellido, fechaNa=_fechaNa)
                    except(KeyError, Publicador.DoesNotExist):
                         p=Publicador(nombre=_nombre, apellido=_apellido, telefono=_telefono, direccion=_direccion,email=_email, fechaBau=_fechaBau, fechaNa=_fechaNa, sexo=_sexo)
                         p.save()
                         msg={'msg':"Publicador Registrado con exito", 'on':1, 'id':p.pk}
                    else:
                         msg={ 'msg': "Error! Este publicador ya esta registrado."}
               else:
                    msg={'msg':"Error! Para ser registrado debe tener como minimo 4 anios"}
          else:
               msg=validar.mensaje
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
     sesionGrupo(request)
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
               status=obtenerStatus(inf[0].mes, inf[0].year, i.pk)[0]
               intervalo=obtenerStatus(inf[0].mes, inf[0].year, i.pk)[1]
               fecha=str(inf[0].mes)+"-"+str(inf[0].year)
          else:
               status=3
               intervalo="Este publicador nunca ha informado"
               fecha="Nulo"
          pubs[cont]={'nombre':i.nombre, 'apellido':i.apellido, 'fechaBau':i.fechaBau, 'edad':getEdad(i.fechaNa, hoy), 'id':i.pk, 'status': status, 'intervalo': intervalo, 'fecha':fecha}
          if len(i.grupo.values())>0:
               pubs[cont]['FKgrupo']=GruposPred.objects.get(pk=i.grupo.values()[0]['IDgrupo'])
          else:
               pubs[cont]['FKgrupo']=0
          cont=cont+1
     pubs=pubs.values()
     return render(request, 'Publicador/conPubs.html',{'pub':pubs,'msg':msg, 'url':2})

def consultar(request, idpub):
     sesionGrupo(request)
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
          mes=p.fechaNa.month
          day=p.fechaNa.day
          fechaNa=str(p.fechaNa.year)+"-"+addZero(p.fechaNa.month)+"-"+addZero(p.fechaNa.day)
          data={'form': formPub, 'on': 1, 'url':2, 'fechaNa':fechaNa, 'fechaBau':p.fechaBau, 'sexo':p.sexo}
     return render(request, pg, data)

def modificar(request):
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
          edad=getEdad(datetime.date(int(_fechaNa[0:4]),int(_fechaNa[5:7]), int(_fechaNa[8:])), hoy)
          if edad>3:
               try:
                    _id=request.session['pub']
               except KeyError:
                    msg="Error! Antes de modificar seleccione un publicador"
               else:
                    p=Publicador.objects.get(pk=_id)
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

def verTarjetaPub(request):
     sesionGrupo(request)
     years=[]
     cont=0
     yearHoy=datetime.date.today().year
     while cont<5:
          years.append([yearHoy-1, yearHoy])
          yearHoy=yearHoy-1
          cont+=1
     cGrupo = traerGrupo()
     p=Publicador.objects.all()
     pubs={}
     cont=0
     for i in p:
          pubs[cont]=i.__dict__
          del pubs[cont]['_state']
          pubs[cont]['fechaNa']=str(i.fechaNa)
          cont+=1
     return render(request, 'Publicador/verTarjetaPub.html', {'form': cGrupo, 'years':years, 'url':2, 'pubs':json.dumps(pubs)})

def conPubG(request):
     datos={}
     cont=0
     grupo=int(request.POST['id'])
     if grupo==0:
          p=Publicador.objects.exclude(grupo__IDgrupo__in=arrayIdGrup())
          if len(p)>0:
               for i in p:
                    datos[cont]={'pk':i.pk, 'nombre':i.nombre, 'apellido':i.apellido, 'direccion':i.direccion}
                    cont+=1
          else:
               datos={'on':1, 'msg':'No hay publicadores sin grupo'}
     else:
          try:
               g=GruposPred.objects.get(pk=grupo)
          except:
               datos={'on':1, 'msg':"Error grupo no existe"}
          else:
               try:
                    request.POST['all']
               except KeyError:
                    p=Publicador.objects.filter(grupo__IDgrupo=grupo).exclude(IDpub__in=[g.encargado.pk, g.auxiliar.pk])
               else:
                    p=Publicador.objects.filter(grupo__IDgrupo=grupo)
               if len(p)>0:
                    for i in p:
                         datos[cont]={'pk':i.pk, 'nombre':i.nombre, 'apellido':i.apellido, 'direccion':i.direccion}
                         cont+=1
               else:
                    datos={'on':1, 'msg':'Este grupo no tiene ningun publcador'}
     return HttpResponse(json.dumps(datos))
