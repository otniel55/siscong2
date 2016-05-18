#libs propias de python
import datetime
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