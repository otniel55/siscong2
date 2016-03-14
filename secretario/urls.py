from django.conf.urls import url

from . import views

app_name="secretario"
urlpatterns = [
    url(r'^$', views.index, name='index'),
	url(r'^grupos/registrar/$', views.registrarGrupo, name='registrarGrupo'),
    url(r'^registrar/grupos/$', views.grupos_registrar, name='grupos_registrar'),
    url(r'^consultar/grupos/$', views.conGrupo, name='conGrupo'),
    url(r'^datos_grupo/$', views.datGrupo, name='datGrupo'),
    url(r'^regPubli/$', views.regPubli, name='regPubli'),
    url(r'^conPub/$', views.conPub, name='conPub'),
    url(r'^publicreg/$', views.publicReg, name='publicReg'),
    url(r'^cambiarpub/$', views.cambiarPub, name='cambiarPub'),
    url(r'^consultar/Publicadores/$', views.conPubs, name='conPubs'),
    url(r'^(?P<idpub>[0-9]+)/Publicador/$', views.traerPub, name='traerPub'),
]