#libs propios de python
import json
import datetime
#modulos de django
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Q
#modulos propios del proyecto
from ..forms import traerGrupo, modalPub, regInforme, regPub
from .siscong import *
#modelos
from secretario.models import GruposPred, Publicador

def Vista_registrar(request):
     hoy=datetime.date.today()
     pub = regPub()
     idGrupos=arrayIdGrup()
     pubAux=[]
     pubSinGrupo=Publicador.objects.exclude(grupo__IDgrupo__in=idGrupos)
     for i in pubSinGrupo:
          if getEdad(i.fechaNa, hoy)>17 and i.fechaBau[0]!="N":
               pubAux.append(i)
     pubsEncargado=pubSinGrupo.filter(privilegiopub__status=True)
     return render(request, 'Grupo/regGrupo.html', { 'url':1, 'regPub': pub, 'all':pubSinGrupo, 'encargados':pubsEncargado, 'aux':pubAux})

def registrar(request):
     validaciones=True
     cont=0
     hoy=datetime.date.today()
     msg={}
     nums=['IDgrupo', 'encargado', 'auxiliar']
     validar=gestion(request.POST, nums, ignorar=['pubs'])
     validar.validar()
     if not validar.error:
          idGrupo=int(request.POST['IDgrupo'])
          enc=int(request.POST['encargado'])
          aux=int(request.POST['auxiliar'])
          pubs=json.loads(request.POST['pubs'])
          try:
               GruposPred.objects.get(pk=idGrupo)
          except(KeyError, GruposPred.DoesNotExist):
               try:
                    encargado=Publicador.objects.get(pk=enc)
               except(KeyError, Publicador.DoesNotExist):
                    msg={'msg':'El Encargado no existe'}
                    validaciones=False
               else:
                    try:
                         Publicador.objects.get(pk=enc, privilegiopub__status=True)
                    except:
                         msg={'msg':'Error, El encargado no tiene privilegios'}
                         validaciones=False
                    else:
                         if not verificarExist(enc):
                              if not verificarAsignacion(enc):
                                   try:
                                        auxiliar=Publicador.objects.get(pk=aux)
                                   except(KeyError, Publicador.DoesNotExist):
                                        msg={'msg':"Error el auxiliar no existe"}
                                        validaciones=False
                                   else:
                                        if aux!=enc:
                                             if getEdad(auxiliar.fechaNa, hoy)>17 and auxiliar.sexo=="M" and auxiliar.fechaBau[0]!="N":
                                                  if not verificarExist(aux):
                                                       if not verificarAsignacion(aux):
                                                            g=GruposPred(IDgrupo=idGrupo, encargado=encargado, auxiliar=auxiliar)
                                                            g.save()
                                                            encargado.grupo.add(g)
                                                            auxiliar.grupo.add(g)
                                                            for i in pubs:
                                                                 try:
                                                                      p=Publicador.objects.get(pk=int(i['id']))
                                                                 except (KeyError, Publicador.DoesNotExist):
                                                                      msg[cont]={'id': i['id'], 'bien':0}
                                                                      validaciones=False
                                                                 else:
                                                                      if not p.pk in [enc, aux]:
                                                                           if not verificarExist(p.pk):
                                                                                p.grupo.add(g)
                                                                                msg[cont]={'id': i['id'], 'bien':1}
                                                                           else:
                                                                                msg[cont]={'id': i['id'], 'bien':0}
                                                                                validaciones=False
                                                                      else:
                                                                            msg[cont]={'id': i['id'], 'bien':1}
                                                                 cont+=1
                                                       else:
                                                            msg={'msg':"Error el auxiliar tiene responsabilidades en otro grupo"}
                                                            validaciones=False
                                                  else:
                                                       msg={'msg':"Error, el auxiliar esta en otro grupo"}
                                                       validaciones=False
                                             else:
                                                  msg={'msg':"Error el auxiliar debe ser varon, mayor de edad y estar bautizado"}
                                                  validaciones=False
                                        else:
                                             msg={'msg':"Error el encargado no puede ser el auxiliar"}
                                             validaciones=False
                              else:
                                   msg={'msg':'Error, el encargado ya tiene responsabilidades en otro grupo'}
                                   validaciones=False
                         else:
                              msg={'msg':'Error, Este encargado está en otro grupo'}
                              validaciones=False
          else:
               msg={'msg':'Hay otro grupo con ese numero, por favor intente con otro'}
               validaciones=False
     else:
          msg=validar.mensaje
     if validaciones:
          msg={'msg':"Grupo creado con exito"}
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
     pubs={}
     cont=0
     try:
          g = GruposPred.objects.get(pk=idGrupo)
     except(KeyError, GruposPred.DoesNotExist):
          datos={"msg":"Este grupo no esta registrado"}
     else:
          request.session['conGrupoId']=idGrupo
          p = Publicador.objects.filter(grupo__IDgrupo=g.pk)
          enc=str(g.encargado.nombre)+" "+str(g.encargado.apellido)
          aux=str(g.auxiliar.nombre)+" "+str(g.auxiliar.apellido)
          for i in p:
               pubs[cont]={'id':i.pk, 'nombre':i.nombre, 'apellido':i.apellido, 'status': 1,
                           'telefono':i.telefono, 'email':i.email, 'direccion':i.direccion}
               cont+=1
          pubs=pubs.values()
          modalInfo = regInforme()
          y=str(datetime.date.today().year-1)+""+str(datetime.date.today().year)
          datos = {'pubs': pubs, 'num': g.pk, 'modalInfo': modalInfo, 'y':y, 'url':1, 'enc':enc, 'aux':aux}
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

#metodos reutilizables
def arrayIdGrup():
     id=[]
     for i in GruposPred.objects.all():
          id.append(i.pk)
     return id

def verificarExist(id):
     p=Publicador.objects.filter(pk=id, grupo__IDgrupo__in=arrayIdGrup())
     if len(p)>0:
          exist=True
     else:
          exist=False
     return exist

def verificarAsignacion(id):
     grupos=GruposPred.objects.filter(Q(encargado=id)|Q(auxiliar=id))
     if len(grupos)>0:
          exist=True
     else:
          exist=False
     return exist

def grupoExist(request):
     g=request.POST['id']
     try:
          GruposPred.objects.get(pk=int(g))
     except(KeyError, GruposPred.DoesNotExist):
          return HttpResponse(json.dumps({'on':1}))
     else:
          return HttpResponse(json.dumps({'on':0}))
