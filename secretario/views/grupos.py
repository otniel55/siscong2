#libs propios de python
import json
import datetime
#modulos de django
from django.http import HttpResponse
from django.shortcuts import render
#modulos propios del proyecto
from ..forms import traerGrupo, modalPub, regInforme, regPub, CrearGrupo
from .siscong import *
#modelos
from secretario.models import GruposPred, Publicador

def Vista_registrar(request):
     hoy=datetime.date.today()
     pub = regPub()
     idGrupos=[]
     pubAux=[]
     for i in GruposPred.objects.all():
          idGrupos.append(i.pk)
     pubSinGrupo=Publicador.objects.exclude(grupo__IDgrupo__in=idGrupos)
     for i in pubSinGrupo:
          if getEdad(i.fechaNa, hoy)>17:
               pubAux.append(i)
     pubsEncargado=pubSinGrupo.filter(privilegiopub__status=True)
     return render(request, 'Grupo/regGrupo.html', { 'url':1, 'regPub': pub, 'all':pubSinGrupo, 'encargados':pubsEncargado, 'aux':pubAux})

def registrar(request):
     msg={}
     validar=gestion(request.POST)
     validar.validar()
     if not validar.error:
          datosG=validar.trimUpper()
          _encargado=datosG['encargado']
          _auxiliar=datosG['auxiliar']
          try:
               verificar = GruposPred.objects.get(encargado=_encargado)
          except(KeyError, GruposPred.DoesNotExist):
               grupo=GruposPred(encargado=_encargado, auxiliar=_auxiliar)
               grupo.save()
               msg={'msg':"Grupo Registrado con exito", 'on':1}
          else:
               msg = {'msg': "Este encargado se encuentra en otro grupo"}
     else:
          msg=validar.mensaje
     return  HttpResponse(json.dumps(msg))

def vistaConsultar(request):
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
     return render(request, 'Grupo/conGrupo.html', {'form': cGrupo, 'onPub': on, 'url':1 })

def conGrupoofPubs(request, idGrupo):
     cGrupo = traerGrupo(initial={'Encargado': idGrupo})
     return render(request, 'Grupo/conGrupo.html', {'form': cGrupo, 'onPub': 1, 'url':1 })

def consultar(request,idGrupo):
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
     return render(request, 'Grupo/datGrupo.html',datos)

def modificar(request):
     validar=gestion(request.POST)
     validar.validar()
     if not validar.error:
          datosG=validar.trimUpper()
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
          msg=validar.mensaje
     return HttpResponse(json.dumps(msg))
