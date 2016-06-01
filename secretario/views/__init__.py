#modulos de django
from django.shortcuts import render
#modulos propios del proyecto
from .grupos import *
from .publicador import *
from .informe import *
from .estadisticas import *
from .pdfs import *
from .precursor import *
from .usuario import *
from .privilegios import *

def index(request):
     return render(request, 'layout.html', {'url':0})

def error404(request):
     return render(request, 'page404.html')
