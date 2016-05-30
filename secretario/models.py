from __future__ import unicode_literals

from django.db import models

# Create your models here.

class GruposPred(models.Model):
	IDgrupo = models.AutoField(primary_key=True)
	encargado = models.ForeignKey(
        'Publicador',
        on_delete = models.CASCADE,
    )
	auxiliar = models.ForeignKey(
        'Publicador',
        on_delete = models.CASCADE,
		related_name='pubauxiliar'
    )
	def __str__(self):
		return self.encargado

class Precursor(models.Model):
	IDprecursor = models.AutoField(primary_key=True)
	horas = models.IntegerField()
	nombre = models.CharField(max_length=50)

	def __str__(self):
		return self.nombre

class privilegio(models.Model):
	nombre=models.CharField("Nombre", max_length=200)
	edadMin=models.IntegerField("Edad minima")
	tiempoBauMin=models.IntegerField("Tiempo minimo de bautizado")

class Publicador(models.Model):
	IDpub = models.AutoField(primary_key=True)
	nombre = models.CharField(max_length=50)
	apellido = models.CharField(max_length=50)
	telefono = models.CharField(max_length=15)
	direccion = models.CharField(max_length=150)
	email = models.CharField(max_length=200)
	fechaBau = models.CharField('Fecha de Bautismo',max_length=20)
	fechaNa = models.DateField('Fecha de Nacimiento')
	precursorado=models.ManyToManyField(Precursor, through='PubPrecursor')
	privilegio=models.ManyToManyField(privilegio, through='privilegioPub')
	grupo = models.ManyToManyField(GruposPred)
	
	def __str__(self):
		return self.nombre
	
class Informe(models.Model):
	Idinf = models.AutoField(primary_key=True)
	horas = models.IntegerField()
	publicaciones = models.IntegerField()
	videos = models.IntegerField()
	revisitas = models.IntegerField()
	estudios = models.IntegerField()
	mes=models.IntegerField()
	year=models.IntegerField()
	FKpub = models.ForeignKey(
        'Publicador',
        on_delete = models.CASCADE,
    )
	observacion=models.CharField(max_length=250)
	def __int__(self):
		return self.IDinf

class PubPrecursor(models.Model):
	FKpub = models.ForeignKey(
        'Publicador',
        on_delete = models.CASCADE,
    )
	FKprecursor = models.ForeignKey(
        'Precursor',
        on_delete = models.CASCADE,
    )
	duracion = models.IntegerField()
	mesIni = models.IntegerField()
	yearIni=models.IntegerField()
	status=models.BooleanField()

class nroPrec(models.Model):
	FKpub = models.ForeignKey(
        'Publicador',
        on_delete = models.CASCADE,
    )
	nroPrec=models.IntegerField()

class privilegioPub(models.Model):
	mes=models.IntegerField("mes de nombramiento")
	year=models.IntegerField("anio de nombramiento")
	FKpub = models.ForeignKey(
        'Publicador',
        on_delete = models.CASCADE,
    )
	FKpriv=models.ForeignKey(
		'privilegio',
		on_delete=models.CASCADE,
	)
	responsabilidad=models.CharField("Responsabilidad", max_length=200)

class horasCon(models.Model):
	FKinf=models.ForeignKey(
		'Informe',
		on_delete=models.CASCADE,
	)
	horas=models.IntegerField()
