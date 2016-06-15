from django.conf.urls import url

from . import views

app_name="secretario"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^404/$', views.error404, name='404'),
    #urls relacionada con grupos
	url(r'^grupos/registrar/$', views.grupos.Vista_registrar, name='registrarGrupo'),
    url(r'^registrar/grupos/$', views.grupos.registrar, name='grupos_registrar'),
    url(r'^consultar/grupos/$', views.grupos.vistaConsultar, name='conGrupo'),
    url(r'^(?P<idGrupo>[0-9]+)/grupoPublicador/$', views.grupos.conGrupoofPubs, name='conGrupoofPubs'),
    url(r'^(?P<idGrupo>[0-9]+)/datos_grupo/$', views.grupos.consultar, name='datGrupo'),
    url(r'^modGrup/$', views.grupos.modificar, name='modGrup'),
    url(r'^validarGrupo/$', views.grupos.grupoExist, name='validarGrupo'),
    url(r'^grupo/modificar/(?P<id>[0-9]+)$', views.grupos.vistaModificar, name='editGrupo'),
    url(r'^deleteG/$', views.grupos.eliminar, name='deleteG'),
    #url relacionadas con publicadores
    url(r'^regPubli/$', views.publicador.vistaRegistrar, name='regPubli'),
    url(r'^publicreg/$', views.publicador.registrar, name='publicReg'),
    url(r'^conPub/$', views.publicador.consultarNameGroup, name='conPub'),
    url(r'^cambiarpub/$', views.publicador.cambiarPub, name='cambiarPub'),
    url(r'^consultar/Publicadores/$', views.publicador.consultarTodos, name='conPubs'),
    url(r'^(?P<idpub>[0-9]+)/Publicador/$', views.publicador.consultar, name='traerPub'),
    url(r'^modPub/$', views.publicador.modificar, name='modPub'),
	url(r'^Publicador/verTarjeta$', views.publicador.verTarjetaPub, name='verTarjetaPub'),
    url(r'^conPubG/$', views.publicador.conPubG, name='conPubG'),
    #urls relacionadas con informes
	url(r'^regInf/$', views.informe.registrar, name='regInf'),
	url(r'^(?P<vista>[1-2]+)/(?P<idPub>[0-9]+)/Tarjeta/(?P<y>[0-9]+)/$', views.informe.tarjeta, name='tarjeta'),
    url(r'^modInf/$', views.informe.modificar, name='modInf'),
    #urls relacionadas con estadisticas
    url(r'^estadisticas/$', views.estadisticas.verEstadisticas, name='estadisticas'),
    url(r'^estadisticas/global', views.estadisticas.estGlobal, name='estGlobal'),
    url(r'^estadisticas/Precurs', views.estadisticas.infPrec, name='infPrec'),
    url(r'^estadisticas/Publicador', views.estadisticas.estPub, name='estPub'),
    url(r'^estadisticas/informeGeneral', views.estadisticas.obtenerInf, name='infG'),
    url(r'^PrecursInf', views.estadisticas.conInfPrec, name='conInfPrec'),
    url(r'^pubEst', views.estadisticas.conEstPub, name='conEstPub'),
    #urls relacionadas con psdfs
    url(r'^pdf/tarjeta/publicador', views.pdfs.vistaPdfPub, name='vistaPdfPub'),
    url(r'^pdfTarPub', views.pdfs.datosPdfPub, name='datosPdfPub'),
    #urls relacionadas con precursores
    url(r'^Precursores/nombrar/$', views.precursor.vistaNombrar, name='vistaNombrar'),
    url(r'^consultar/Precursor/$', views.precursor.conPrec, name='conPrec'),
    url(r'^Precursores/horas/$', views.precursor.editPrecur, name='editPrecur'),
    url(r'^nombrar/$', views.precursor.nombrar, name='NombrarPrecur'),
    url(r'^conPrecs/$', views.precursor.conPrecs, name='conPrecs'),
    url(r'^conYear/$', views.precursor.yearServicio, name='yearServicio'),
    url(r'^historia/precursor/(?P<year>[a-zA-Z0-9]+)/$', views.precursor.historiaPrec, name='historiaPrec'),
    url(r'^darBaja/$', views.precursor.darBaja, name='darBaja'),
    #urls relacionadas con usuarios
    url(r'^registrar/usuario/$', views.usuario.vistaRegistro, name='usuReg'),
    url(r'^regusu/$', views.usuario.registrar, name='Regusu'),
    #urls relacionadas con privilegios
    url(r'^privilegio/modificar$', views.privilegios.modificar, name='privMod'),
    url(r'^privilegio/consultar$', views.privilegios.consultar, name='privCon'),
    url(r'^privilegio/nombrar$', views.privilegios.Vistanombrar, name='privnombrar'),
    url(r'^privilegio/consultarnombrados$', views.privilegios.consultarNombrados, name='privconsnombrados'),
    url(r'^privnombrar$', views.privilegios.nombrar, name='nombrarPriv'),
    url(r'^privilegio/baja$', views.privilegios.baja, name='privBaja'),
    #urls relacionadas con sesion de usuarios
    url(r'^login$', views.sesion.ingreso, name='login'),
    url(r'^autenticar$', views.sesion.autenticar, name='autenticar'),
    url(r'^cerrarsesion$', views.sesion.cerrar, name='cerrar'),
]
