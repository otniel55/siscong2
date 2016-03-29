from django.conf.urls import url

from . import views

app_name="secretario"
urlpatterns = [
    url(r'^$', views.index, name='index'),
	url(r'^grupos/registrar/$', views.registrarGrupo, name='registrarGrupo'),
    url(r'^registrar/grupos/$', views.grupos_registrar, name='grupos_registrar'),
    url(r'^consultar/grupos/$', views.conGrupo, name='conGrupo'),
    url(r'^(?P<idGrupo>[0-9]+)/datos_grupo/$', views.datGrupo, name='datGrupo'),
    url(r'^regPubli/$', views.regPubli, name='regPubli'),
    url(r'^conPub/$', views.conPub, name='conPub'),
    url(r'^publicreg/$', views.publicReg, name='publicReg'),
    url(r'^cambiarpub/$', views.cambiarPub, name='cambiarPub'),
    url(r'^consultar/Publicadores/$', views.conPubs, name='conPubs'),
    url(r'^(?P<idpub>[0-9]+)/Publicador/$', views.traerPub, name='traerPub'),
	url(r'^modGrup/$', views.modGrup, name='modGrup'),
    url(r'^informe/registrar/$', views.viewInfo, name='viewInfo'),
	url(r'^regInf/$', views.regInf, name='regInf'),
	url(r'^(?P<vista>[1-2]+)/(?P<idPub>[0-9]+)/Tarjeta/(?P<y>[0-9]+)/$', views.tarjeta, name='tarjeta'),
    url(r'^(?P<idGrupo>[0-9]+)/grupoPublicador/$', views.conGrupoofPubs, name='conGrupoofPubs'),
	url(r'^conPubG/$', views.conPubG, name='conPubG'),
	url(r'^Publicador/verTarjeta$', views.verTarjetaPub, name='verTarjetaPub'),
    url(r'^Precursores/horas/$', views.editPrecur, name='editPrecur'),
]