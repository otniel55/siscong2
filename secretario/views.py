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

def obtenerStatus(mes, year):
     hoy=datetime.date.today()
     if hoy.year==year:
          meses=(hoy.month-1)-mes
     else:
          mesYear=(hoy.year-year)*12
          mesYear=mesYear-mes
          meses=mesYear+(hoy.month-1)
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
          datos={'pub':inf, 'p':p}
     else:
          datos={'vacio':1}

     if vista == '1':
          pagina = 'conTarjetaGrupoPub.html'
     else:
          pagina = 'tarjetaPub.html'

     return render(request, pagina , datos)

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
               verificar = PubPrecursor.objects.filter(FKpub=x['id'], status=True)
               if len(verificar) > 0:
                    msg[cont] = {'msg': 'el publicador' + x['id'] + 'ya es precursor'}
                    validaciones = False
               else:
                    try:
                         prec=Precursor.objects.get(pk=x['precur'])
                    except(KeyError, Precursor.DoesNotExist):
                         msg[cont]={'msg':'El precursorado'+ x['precur'] + ' no existe'}
                         validaciones=False
                    else:
                         pubP = PubPrecursor(FKpub=pub, FKprecursor=prec, duracion=x['duracion'], mesIni=mes, yearIni=year, status=True)
                         pubP.save()
                         msg[cont] = {'msg': 'el publicador' + x['id'] + 'fue nombrado con exito'}
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
          if status==3:
               p=Publicador.objects.filter(pubprecursor__FKprecursor=prec)
          else:
               p=Publicador.objects.filter(pubprecursor__FKprecursor=prec, pubprecursor__status=status)
          if len(p)>0:
               for i in p:
                    if prec==3 or prec==4:
                         pubprec=PubPrecursor.objects.filter(FKpub=i.pk)
                         for x in pubprec:
                              cont+=1
                              years.append(x.yearIni)
                    precs[cont]={'pk':i.pk, 'nombre':i.nombre+" "+i.apellido}
                    cont+=1

               data = {'p':precs}
          else:
               data={'msg':'No hay ningun registro de este tipo de precursor'}
     return HttpResponse(json.dumps(data))

def historiaPrec(request, pub, year, tipo):
     cont=0
     datosp={}
     try:
          p=Publicador.objects.get(pk=pub)
     except(KeyError, Publicador.DoesNotExist):
          datosp={'msg':'Publicador no existe'}
     else:
          try:
               Precursor.objects.get(pk=tipo)
          except(KeyError, Precursor.DoesNotExist):
               datosp={'msg':"tipo de precursorado no existe"}
          else:
               if tipo==1 or tipo==2:
                    precur=PubPrecursor.obejects.filter(FKpub=pub, FKprecursor=tipo).order_by('-yearIni', '-mesIni')
               else:
                    precur=PubPrecursor.obejects.filter(FKpub=pub, FKprecursor=tipo, yearIni=year).order_by('-mesIni')
               if len(precur)>0:
                    for i in precur:
                         mes=i.mesIni
                         year=i.yearIni
                         duracion=i.duracion
                         while duracion>0:
                              status=2
                              try:
                                   inf=Informe.objects.get(FKpub=pub, mes=mes, year=year)
                              except(KeyError, Informe.DoesNotExist):
                                   h="No informo"
                              else:
                                   h=inf.horas
                                   if h>=i.FKprecursor.horas:
                                        status=1
                              mes+=1
                              if mes==13:
                                   mes=1
                                   year+=1
                              duracion-=1
                              if tipo==1 or tipo==2:
                                   datosp[cont]={'tipoPrecur':i.FKprecursor.nombre, 'horasExigidas': i.FKprecursor.horas, 'horasHechas':h}
                              else:
                                   if h!="No informo":
                                        datosp[cont]={'mes':inf.mes, 'horas':inf.horas, 'publicaciones':inf.publicaciones, 'videos':inf.videos, 'revisitas':inf.revisitas, 'estudios': inf.estudios}
                                   else:
                                        datosp[cont]={'msg':h}
                              cont+=1
                              datosp=datosp.values()
               else:
                    datosp={'msg':"Esta persona no ha realizado el precursorado en ese lapso de tiempo o nunca ha sido precursor."}
     return render(request, "tarjetaPrec.html", datosp)


#
