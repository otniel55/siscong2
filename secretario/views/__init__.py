#libs propias de python
import json
import datetime
#modulos de django
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.core.urlresolvers import reverse
from secretario.models import *
from django.views import generic
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
#modulos propios del proyexto
from ..forms import *
from .views1 import *
from .grupos_registrar import *

def index(request):
     return render(request, 'layout.html', {'url':0})

def registrarGrupo(request):
     form = CrearGrupo()
     return render(request, 'regGrupo.html', {'form': form, 'url':1})