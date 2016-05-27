#libs propias de python
import datetime
#modulos de django
from django.db.models import Q
#modulos propios del proyecto
from secretario.models import PubPrecursor

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
                    except(ValueError):
                        self.error=False
                        break
                elif i in self.fechaKeys:
                    try:
                        datetime.date(int(self.elementos[i][0:4]), int(self.elementos[i][5:7]), int(self.elementos[i][8:]))
                    except(ValueError):
                        self.error=False
                        break
                else:
                    if self.elementos[i].strip()=="":
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