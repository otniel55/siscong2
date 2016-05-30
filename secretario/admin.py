from django.contrib import admin
from django.contrib.admin import AdminSite

# Register your models here.
from .models import *

admin.site.register(GruposPred)
admin.site.register(Publicador)
admin.site.register(Informe)

admin.site.register(Precursor)
admin.site.register(PubPrecursor)
admin.site.register(nroPrec)
admin.site.register(horasCon)

admin.site.register(privilegioPub)
admin.site.register(privilegio)
