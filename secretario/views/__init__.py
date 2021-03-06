#modulos de django
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
#modulos propios del proyecto
from .grupos import *
from .publicador import *
from .informe import *
from .estadisticas import *
from .pdfs import *
from .precursor import *
from .usuario import *
from .privilegios import *
from .siscong import *
from .sesion import *

@login_required(login_url='/login')
def index(request):
     sesionGrupo(request)
     return render(request, 'layout.html', {'url':0})

def error404(request):
     sesionGrupo(request)
     return render(request, 'page404.html')
