from django.contrib import admin
from django.contrib.admin import AdminSite

# Register your models here.
from .models import GruposPred, Publicador, Informe, Precursor, PubPrecursor

admin.site.register(GruposPred)
admin.site.register(Publicador)

admin.site.register(Precursor)
admin.site.register(PubPrecursor)

class infpub(admin.ModelAdmin):
	list_display = ('fecha','horas','FKpub')

admin.site.register(Informe,infpub)
