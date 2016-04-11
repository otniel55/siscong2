from __future__ import unicode_literals

from django.db import models

# Create your models here.

class GruposPred(models.Model):
	IDgrupo = models.AutoField(primary_key=True)
	encargado = models.CharField(max_length=50)
	auxiliar = models.CharField(max_length=50)
	def __unicode__(self):
		return self.encargado

class Precursor(models.Model):
	IDprecursor = models.AutoField(primary_key=True)
	horas = models.IntegerField()
	nombre = models.CharField(max_length=50)

	def __unicode__(self):
		return self.nombre

class Publicador(models.Model):
	IDpub = models.AutoField(primary_key=True)
	nombre = models.CharField(max_length=50)
	apellido = models.CharField(max_length=50)
	telefono = models.CharField(max_length=15)
	direccion = models.CharField(max_length=150)
	email = models.EmailField()
	fechaBau = models.CharField('Fecha de Bautismo',max_length=20)
	fechaNa = models.DateField('Fecha de Nacimiento')
	precursorado=models.ManyToManyField(Precursor, through='PubPrecursor')
	FKgrupo = models.ForeignKey(
        'GruposPred',
        on_delete = models.CASCADE,
    )
	
	def __unicode__(self):
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