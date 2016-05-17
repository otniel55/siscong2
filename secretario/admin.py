from django.contrib import admin
from django.contrib.admin import AdminSite

# Register your models here.
from .models import GruposPred, Publicador, Informe, Precursor, PubPrecursor, nroPrec, horasCon

admin.site.register(GruposPred)
admin.site.register(Publicador)

admin.site.register(Precursor)
admin.site.register(PubPrecursor)

admin.site.register(Informe)
admin.site.register(nroPrec)
admin.site.register(horasCon)