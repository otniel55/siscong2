#libs propias de python
import datetime
#modulos de django
from django.db.models import Q
#modulos propios del proyecto
from secretario.models import PubPrecursor, Informe, GruposPred
class gestion:
    elementos={}
    nroKeys=[]
    fechaKeys=[]
    ignore=[]
    error=False
    mensaje={}
    def __init__(self, elements={}, nro=[], fecha=[], ignorar=[],msg={'msg':"No intente hacer trampa"}):
        self.elementos=elements
        self.nroKeys=nro
        self.fechaKeys=fecha
        self.ignore=ignorar
        self.mensaje=msg
    def validar(self):
        for i in self.elementos.keys():
            if i not in self.ignore:
                if i in self.nroKeys:
                    try:
                        int(self.elementos[i])
                    except(ValueError, KeyError):
                        self.error=False
                        break
                elif i in self.fechaKeys:
                    try:
                        datetime.date(int(self.elementos[i][0:4]), int(self.elementos[i][5:7]), int(self.elementos[i][8:]))
                    except(ValueError, KeyError):
                        self.error=False
                        break
                else:
                    try:
                        if self.elementos[i].strip()=="":
                            self.error=False
                            break
                    except KeyError:
                        self.error=False
                        break

    def trimUpper(self):
         modElemets={}
         for i in self.elementos.keys():
              if i not in self.ignore:
                   try:
                        modElemets[i]=self.elementos[i].upper().strip()
                   except(AttributeError):
                        modElemets[i]=self.elementos[i]
              else:
                   modElemets[i]=self.elementos[i]
         return modElemets

def getEdad(fechaIni, fechaFin):
    return fechaFin.year-fechaIni.year-((fechaFin.month, fechaFin.day)<(fechaIni.month, fechaIni.day))

def getFechaFin(mesI, yearI, duracion):
     for i in range(1, duracion):
          mesI+=1
          if mesI==13:
               mesI=1
               yearI+=1
     fecha=[mesI, yearI]
     return fecha

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

def obtenerStatus(mes, year, pk):
     promInf=[]
     hoy=datetime.date.today()
     meses=getDiferenciaMes(mes,year,hoy.month,hoy.year)
     if meses<1:
          meses=0
          status=0
          inf=Informe.objects.filter(FKpub=pk).order_by("-year", "-mes")
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
                      promInf.append(infs.minutos)
              if len(promInf)>0:
                  if prom(promInf)>inf[0].minutos:
                      status=4
     elif meses>0 and meses<7:
          status=1
     else:
          status=2
     return (status, meses)

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

def arrayObjectToDict(arrayObject, ignore=[], add={}):
    cont=0
    dictionary={}
    for i in arrayObject:
        dictionary[cont]={}
        for j in i.__dict__.keys():
            if j not in ignore:
                dictionary[cont][j]=i.__dict__[j]
        if add:
            for j in add.keys():
                dictionary[cont][j]=add[j]['function']([i.__dict__[k] for k in add[j]['datos']])
        cont+=1
    return dictionary

def addZero(num):
     if num<10:
          num="0"+str(num)
     return str(num)

def precursorActivo(precursorado, mes, year):
     activo=False
     if getDiferenciaMes(precursorado.mesIni, precursorado.yearIni, mes, year) > -2:
          if precursorado.duracion == 0:
               mesF = mes
               yearF = year
          else:
               fechaF = getFechaFin(precursorado.mesIni, precursorado.yearIni, precursorado.duracion)
               mesF = fechaF[0]
               yearF = fechaF[1]
          if getDiferenciaMes(mes, year, mesF, yearF) > -2:
               activo=True
     return activo

def recorrerArrayMeses(array, idPub):
     stringMeses=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
     fin=False
     cont=0
     data={}
     ultimoInf=Informe.objects.filter(FKpub=idPub).order_by("-year", "-mes")[0]
     primerInf=Informe.objects.filter(FKpub=idPub).order_by("year", "mes")[0]
     for j in array:
          if getDiferenciaMes(j[1],j[0],ultimoInf.mes,ultimoInf.year)>-2:
               try:
                    inf=Informe.objects.get(FKpub=idPub, mes=j[1], year=j[0])
               except:
                    if not fin:
                         data[cont]={'mes':stringMeses[j[1]-1], 'horas':0, 'publicaciones':0,
                             'revisitas':0, 'estudios':0, 'videos':0, "obs":"no informo", 'pk':0
                             }
                    else:
                         data[cont]={'mes':stringMeses[j[1]-1], 'horas':"", 'publicaciones':"",
                             'revisitas':"", 'estudios':"", 'videos':"", "obs":"", 'pk':0
                             }
               else:
                    data[cont]={'horasC':convertMinutesToHours(inf.minutos),'mes':stringMeses[j[1]-1], 'horas':addZeroToFinal(convertMinutesToHours(inf.minutos)), 'publicaciones':inf.publicaciones,
                             'revisitas':inf.revisitas, 'estudios':inf.estudios, 'videos':inf.videos, 'obs':inf.observacion, 'pk':inf.pk
                             }
                    if primerInf.mes==j[1] and primerInf.year==j[0]:
                         fin=True
                         if inf.observacion=="n/t":
                              data[cont]['obs']="Primer Informe."
                         else:
                              data[cont]['obs']+="(Primer Informe)"
          else:
               data[cont]={'mes':stringMeses[j[1]-1], 'horas':"", 'publicaciones':"",
                             'revisitas':"", 'estudios':"", 'videos':"", "obs":"", 'pk':0
                             }
          cont+=1
     return [reverseDict(data), fin]

def reverseDict(dict):
     dictReverse={}
     keys=[]
     cont=0
     for i in dict.keys():
          keys.append(i)
     keys.reverse()
     for i in keys:
          dictReverse[cont]=dict[i]
          cont+=1
     return dictReverse

def arraymeses(year):
     meses=[]
     mes=8
     meses.append([year, mes])
     for i in range(1, 12):
          mes-=1
          if mes==0:
               mes=12
               year-=1
          meses.append([year,mes])
     return meses
    
def arrayIdGrup():
     id=[]
     for i in GruposPred.objects.all():
          id.append(i.pk)
     return id

def sesionGrupo(request):
    try:
        del request.session['idgrupo']
    except KeyError:
        pass

def convertMinutesToHours(minutos):
    result=""
    horas=0
    if minutos>0:
        while(minutos>59):
            horas+=1
            minutos-=60
        if horas>0:
            result=str(horas)
            if minutos>0:
                result+="."+str(minutos)
                result=float(addZeroToFinal(float(result)))
            else:
                result=int(result)
        else:
            result="0."+str(minutos)
            result=float(addZeroToFinal(float(result)))
        return result
    else:
        return "formato no valido para minutos"

def addZeroToFinal(num):
    try:
        if not num.is_integer():
            num=str(num)
            decimales=num[num.find(".")+1:]
            if len(decimales)==1:
                num+="0"
    except AttributeError:
        pass
    return num

def recortarDecimal(num):
    num=str(num)
    if num.find(".")>-1:
        return addZeroToFinal(float(num[:num.find(".")+3]))
    else:
        return num

    
