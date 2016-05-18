class validacion:
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
