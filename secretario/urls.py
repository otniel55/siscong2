from django.conf.urls import url

from . import views

app_name="secretario"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    #urls relacionada con grupos
	url(r'^grupos/registrar/$', views.grupos.Vista_registrar, name='registrarGrupo'),
    url(r'^registrar/grupos/$', views.grupos.registrar, name='grupos_registrar'),
    url(r'^consultar/grupos/$', views.grupos.vistaConsultar, name='conGrupo'),
    url(r'^(?P<idGrupo>[0-9]+)/grupoPublicador/$', views.grupos.conGrupoofPubs, name='conGrupoofPubs'),
    url(r'^(?P<idGrupo>[0-9]+)/datos_grupo/$', views.grupos.consultar, name='datGrupo'),
    url(r'^modGrup/$', views.grupos.modificar, name='modGrup'),
    #url relacionadas con publicadores
    url(r'^regPubli/$', views.publicador.vistaRegistrar, name='regPubli'),
    url(r'^publicreg/$', views.publicador.registrar, name='publicReg'),
    url(r'^conPub/$', views.publicador.consultarNameGroup, name='conPub'),
    url(r'^cambiarpub/$', views.publicador.cambiarPub, name='cambiarPub'),
    url(r'^consultar/Publicadores/$', views.publicador.consultarTodos, name='conPubs'),
    url(r'^(?P<idpub>[0-9]+)/Publicador/$', views.traerPub, name='traerPub'),
    url(r'^informe/registrar/$', views.viewInfo, name='viewInfo'),
	url(r'^regInf/$', views.regInf, name='regInf'),
	url(r'^(?P<vista>[1-2]+)/(?P<idPub>[0-9]+)/Tarjeta/(?P<y>[0-9]+)/$', views.tarjeta, name='tarjeta'),
	url(r'^conPubG/$', views.conPubG, name='conPubG'),
	url(r'^Publicador/verTarjeta$', views.verTarjetaPub, name='verTarjetaPub'),
    url(r'^Precursores/horas/$', views.editPrecur, name='editPrecur'),
    url(r'^Precursores/nombrar/$', views.vistaNombrar, name='vistaNombrar'),
    url(r'^nombrar/$', views.NombrarPrecur, name='NombrarPrecur'),
    url(r'^modPub/$', views.modPub, name='modPub'),
    url(r'^consultar/Precursor/$', views.conPrec, name='conPrec'),
    url(r'^conPrecs/$', views.conPrecs, name='conPrecs'),
    url(r'^historia/precursor/(?P<year>[a-zA-Z0-9]+)/$', views.historiaPrec, name='historiaPrec'),
    url(r'^conYear/$', views.yearServicio, name='yearServicio'),
    url(r'^darBaja/$', views.darBaja, name='darBaja'),
    url(r'^registrar/usuario/$', views.usuReg, name='usuReg'),
    url(r'^regusu/$', views.Regusu, name='Regusu'),
    url(r'^estadisticas/$', views.estadisticas, name='estadisticas'),
    url(r'^estadisticas/informeGeneral', views.infG, name='infG'),
    url(r'^estadisticas/Precurs', views.infPrec, name='infPrec'),
    url(r'^PrecursInf', views.conInfPrec, name='conInfPrec'),
    url(r'^estadisticas/Publicador', views.estPub, name='estPub'),
    url(r'^pubEst', views.conEstPub, name='conEstPub'),
    url(r'^estadisticas/global', views.estGlobal, name='estGlobal'),
    url(r'^pdf/tarjeta/publicador', views.vistaPdfPub, name='vistaPdfPub'),
    url(r'^pdfTarPub', views.datosPdfPub, name='datosPdfPub'),
]