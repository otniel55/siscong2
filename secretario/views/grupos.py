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
          if getEdad(i.fechaNa, hoy)>17 and i.fechaBau[0]!="N" and i.sexo=="M":
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
               inf=Informe.objects.filter(FKpub=i.pk).order_by("-year", "-mes")
               if len(inf)>0:
                    status=obtenerStatus(inf[0].mes, inf[0].year, i.pk)[0]
               else:
                    status=3
               pubs[cont]={'id':i.pk, 'nombre':i.nombre, 'apellido':i.apellido,'status': status,
                           'telefono':i.telefono, 'email':i.email, 'direccion':i.direccion}
               cont+=1
          pubs=pubs.values()
          y=str(datetime.date.today().year-1)+""+str(datetime.date.today().year)
          datos = {'pubs': pubs, 'num': g.pk, 'y':y, 'url':1, 'enc':enc, 'aux':aux}
     return render(request, 'Grupo/datGrupo.html',datos)


def vistaModificar(request, id):
     try:
          g=GruposPred.objects.get(pk=int(id))
     except(KeyError, GruposPred.DoesNotExist):
          return render(request, "page404.html")
     else:
          hoy=datetime.date.today()
          encs={}
          data={}
          id=g.pk
          enc=g.encargado.pk
          aux=g.auxiliar.pk
          grupos=GruposPred.objects.exclude(pk=id)
          groups={}
          cont=0
          for i in grupos:
               groups[cont]={'value':i.pk, 'text':str(i)}
               cont+=1
          groups=groups.values()
          encargados=Publicador.objects.filter(privilegiopub__status=True)
          cont=0
          for i in encargados:
               if not verificarAsignacion(i.pk, True, id) and i.pk!=aux:
                    encs[cont]={'value':i.pk, 'text':i.nombre+" "+i.apellido}
                    if i.pk==enc:
                         encs[cont]['selected']=1
                         encs[cont]['direccion']=i.direccion
                    cont+=1
          encs=encs.values()
          auxiliares=Publicador.objects.filter(sexo="M")
          auxs={}
          cont=0
          for i in auxiliares:
               if i.fechaBau[0]!="N" and getEdad(i.fechaNa, hoy)>17 and not verificarAsignacion(i.pk, True, id) and i.pk!=enc:
                    auxs[cont]={'value':i.pk, 'text':i.nombre+" "+i.apellido}
                    if verificarPriv(i.pk):
                         auxs[cont]['priv']=1
                    if i.pk==aux:
                         auxs[cont]['selected']=1
                         auxs[cont]['direccion']=i.direccion
                    cont+=1
          auxs=auxs.values()
          publicadores=Publicador.objects.filter(grupo__IDgrupo=g.pk).exclude(pk__in=[enc, aux])
          sinGrupo=Publicador.objects.exclude(grupo__IDgrupo__in=arrayIdGrup())
          data={'id':id, 'cmbEnc':encs, 'cmbAux':auxs, 'pubs':publicadores, 'cmbGrupo':groups, 'sinG':sinGrupo}
          return render(request, "Grupo/editGrupo.html", data)

def modificar(request):
     pasar=False
     msg={}
     nums=['IDgrupo', 'enc', 'aux']
     validar=gestion(request.POST, nums, ignorar=['pubs'])
     validar.validar()
     if not validar.error:
          idG=int(request.POST['IDgrupo'])
          enc=int(request.POST['enc'])
          aux=int(request.POST['aux'])
          try:
               g=GruposPred.objects.get(pk=idG)
          except(KeyError, GruposPred.DoesNotExist):
               msg={'msg':"Este grupo no existe"}
          else:
               try:
                    encargado=Publicador.objects.get(pk=enc)
               except(KeyError, Publicador.DoesNotExist):
                    msg={'msg':"Error, Encargado no existe"}
               else:
                    if enc!=g.encargado.pk:
                         try:
                              Publicador.objects.get(pk=enc, privilegiopub__status=True)
                         except(KeyError, Publicador.DoesNotExist):
                              msg={'msg':"Error, el encargao no tiene privilegios"}
                              pasar=False
                         else:
                              resp=addToGroup(enc, idG, False, True)
                              if resp[0]:
                                   pasar=True
                              else:
                                   pasar=False
                                   msg=resp[1]
                    else:
                         pasar=True
                    if pasar:
                         pasar=False
                         try:
                              auxiliar=Publicador.objects.get(pk=aux)
                         except:
                              msg={'msg':"Error, el auxiliar no existe"}
                         else:
                              if aux!=g.auxiliar.pk:
                                   hoy=datetime.date.today()
                                   if getEdad(auxiliar.fechaNa, hoy)>17 and auxiliar.sexo=="M" and auxiliar.fechaBau[0]!="N":
                                        resp=addToGroup(aux, idG, True)
                                        if resp[0]:
                                             pasar=True
                                        else:
                                             pasar=False
                                             msg=resp[1]
                                   else:
                                        pasar=False
                                        msg={'msg':"Error, el auxiliar debe ser mayor de edad, estar bautizado y ser de sexo masculino"}
                              else:
                                   pasar=True
                              if pasar:
                                   cont=0
                                   pubs=json.loads(request.POST['pubs'])
                                   for i in pubs:
                                        if not int(i['id']) in [enc, aux]:
                                             resp=addToGroup(int(i['id']), int(i['idG']))
                                             if resp[0]:
                                                  msg[cont]={'id': i['id'], 'bien':1}
                                             else:
                                                  msg[cont]={'id': i['id'], 'bien':0}
                                                  pasar=False
                                        else:
                                             msg[cont]={'id': i['id'], 'bien':1}
                                        cont+=1
     else:
          msg=validar.mensaje
     if pasar:
          msg={'msg':"Datos modificados exitosamente"}
     return HttpResponse(json.dumps(msg))

def verificarPriv(id):
     try:
          Publicador.objects.get(pk=id, privilegiopub__status=True)
     except(KeyError, Publicador.DoesNotExist):
          return False
     else:
          return True

def addToGroup(pub, grupo, nombrarA=False, nombrarE=False):
     resp=[True, {}]
     try:
          p=Publicador.objects.get(pk=pub)
     except(KeyError, Publicador.DoesNotExist):
          resp=[False, {'msg':"Error, Publicador no existe"}]
     else:
          if grupo!=0:
               try:
                    g=GruposPred.objects.get(pk=grupo)
               except(KeyError, GruposPred.DoesNotExist):
                    resp=[False, {'msg':"Error, Grupo no existe"}]
               else:
                    if not verificarAsignacion(pub):
                         if len(p.grupo.values())==1 and p.grupo.values()[0]['IDgrupo']==grupo and (nombrarA or nombrarE):
                              if nombrarA:
                                   g.auxiliar=p
                              else:
                                   g.encargado=p
                              g.save()
                         elif not verificarExist(pub):
                              p.grupo.add(g)
                              if nombrarA:
                                   g.auxiliar=p
                                   g.save()
                              elif nombrarE:
                                   g.encargado=p
                                   g.save()
                         else:
                              grupoP=p.grupo.values()
                              if len(Publicador.objects.filter(grupo__IDgrupo=grupoP[0]['IDgrupo']).exclude(pk__in=[grupoP[0]['encargado_id'] , grupoP[0]['auxiliar_id']]))>1:
                                   p.grupo.clear()
                                   p.grupo.add(g)
                                   if nombrarA:
                                        g.auxiliar=p
                                        g.save()
                                   elif nombrarE:
                                        g.encargado=p
                                        g.save()
                              else:
                                   resp=[False, {'msg':"Error, El grupo no puede quedar vacio"}]
                    else:
                         resp=[False, {'msg':"Error, Este publicador tiene responsabilidades en otro grupo"}]
          else:
               p.grupo.clear()
     return resp
     
def eliminar(request):
     datos={}
     id=int(request.POST['id'])
     try:
          g=GruposPred.objects.get(pk=id)
     except(KeyError, GruposPred.DoesNotExist):
          datos={'msg':"Error, este grupo existe", 'on':1}
     else:
          g.delete()
          datos={'msg':"Grupo eliminado con exito", 'on':1}
     return HttpResponse(json.dumps(datos))

#metodos reutilizables
def verificarExist(id):
     p=Publicador.objects.filter(pk=id, grupo__IDgrupo__in=arrayIdGrup())
     if len(p)>0:
          exist=True
     else:
          exist=False
     return exist

def verificarAsignacion(id, excluir=False, gPk=0):
     grupos=GruposPred.objects.filter(Q(encargado=id)|Q(auxiliar=id))
     if excluir:
          grupos=grupos.exclude(IDgrupo=gPk)
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
