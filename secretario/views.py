from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from .forms import *
from django.core.urlresolvers import reverse
from secretario.models import *
from django.views import generic
import json
import datetime

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
          return render(request, 'regGrupo.html', {'msg':"Grupo Registrado con exito"})
     else:
          return render(request, 'regGrupo.html', {
          'msg': "Error! Este encargado se encuentra en otro grupo.",
          })
        
def conGrupo(request):
     cGrupo = traerGrupo()
     return render(request, 'conGrupo.html', {'form': cGrupo})

def datGrupo(request,idGrupo):
     g = GruposPred.objects.get(pk=idGrupo)
     p = Publicador.objects.filter(FKgrupo=g.pk)
     formDatGrupo = CrearGrupo(instance=g)
     datos = {'form': formDatGrupo, 'publicadores': p, 'num': g.pk}
     return render(request, 'datGrupo.html',datos)

def conPub(request):
     cont=0
     try:
        p=Publicador.objects.get(pk=request.POST['id'])
     except(KeyError, Publicador.DoesNotExist):
        return HttpResponse(json.dumps({'msg':'Error, Publicador no existe'}))
     else:
          fechaNa=str(p.fechaNa.day)+"-"+str(p.fechaNa.month)+"-"+str(p.fechaNa.year)
          p={'nombre':p.nombre, 'apellido':p.apellido, 'telefono':p.telefono, 'direccion':p.direccion, 'email':p.email,'fechaBau':p.fechaBau,'fechaNa':fechaNa, 'grupo':p.FKgrupo.pk}
          g=GruposPred.objects.all()
          grup={}
          for i in g:
            grup[cont]={'id':i.pk, 'encargado':i.encargado}
            cont=cont+1
          datos={'pub':p, 'grupos':grup}
          return HttpResponse(json.dumps(datos))

def conPubs(request):
    c=[]
    cont=0
    pubs={}
    p=Publicador.objects.all()
    for i in p:
        pubs[cont]={'nombre':i.nombre, 'apellido':i.apellido, 'fechaBau':i.fechaBau, 'edad':obteneredad(i), 'FKgrupo':i.FKgrupo, 'id':i.pk, 'g':i.FKgrupo.pk}
        cont=cont+1
    pubs=pubs.values()
    return render(request, 'conPubs.html',{'pub':pubs})

def obteneredad(persona):
    hoy=datetime.date.today()
    return hoy.year-persona.fechaNa.year-((hoy.month, hoy.day)<(persona.fechaNa.month, persona.fechaNa.day))

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
        g=GruposPred.objects.get(pk=_grupo)
        g.publicador_set.create(nombre=_nombre, apellido=_apellido, telefono=_telefono, direccion=_direccion,email=_email, fechaBau=_fechaBau, fechaNa=_fechaNa)
        return render(request, 'regPubli.html', {'msg':"Grupo Registrado con exito"})
    else:
        return render(request, 'regPubli.html', {
          'msg': "Error! Este encargado se encuentra en otro grupo.",
        })

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
    p=Publicador.objects.get(pk=idpub)
    formPub = regPub(instance=p)
    return render(request, 'regPubli.html', {'form': formPub})

def modPub(request):
    _nombre=request.POST['nombre'].upper()
    _apellido=request.POST['apellido'].upper()
    _telefono=request.POST['telefono']
    _direccion =request.POST['direccion'].upper()
    _email=request.POST['email'].upper()
    _fechaBau=request.POST['fechaBau']
    _fechaNa=request.POST['fechaNa']
    _grupo=request.POST['Encargado']
    _id=request.POST['id']
    try:
        p=Publicador.objects.get(pk=_id)
    except(KeyError, Publicador.DoesNotExist):
        msg={'msg':'Error, publicador no registrado'}
    else:
        try:
            g=GruposPred.objects.get(pk=_grupo)
        except(KeyError, GruposPred.DoesNotExist):
            msg={'msg':'Grupo no existe'}
        else:
            Publicador.objects.filter(pk=_id).update(FKgrupo=_grupo)
            p.nombre=_nombre
            p.apellido=_apellido
            p.telefono=_telefono
            p.direccion=_direccion
            p.email=_email
            p.fechaBau=_fechaBau
            p.fechaNa=_fechaNa
            p.save
            msg={'msg':'Publicador modificado con exito'}
    return HttpResponse(json.dumps(msg))

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
          try:
               Informe.objects.get(fecha=_fecha,FKpub=_pub)
          except(KeyError, Informe.DoesNotExist):
               p.informe_set.create(horas=_horas, publicaciones=_publicaciones, videos=_videos, revisitas=_revisitas, estudios=_estudios, fecha=_fecha)
               msg={'msg':'Informe Registrado con exito'}
          else:
               msg={'msg':'Informe ya Fue registrado'}
     return HttpResponse(json.dumps(msg))
