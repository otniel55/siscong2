def modInf(request):
     msg={}
     try:
          y=request.session['tarjetaY']
     except(KeyError):
          msg={'msg':'Seleccione un informe'}
     else:
          try:
               p=request.session['tarjetaPub']
          except(KeyError):
               msg={'msg':'Seleccione un informe'}
     mes=request.POST['mes']
     horas=request.POST['horas']
     revisitas=request.POST['revisitas']
     estudios=request.POST['estudios']
     publicaciones=request.POST['publicaciones']
     videos=request.POST['videos']
     try:
          inf=Informe.objects.get(FKpub=p, year=y, mes=mes)
     except(KeyError):
          msg={"msg":"no existe un informe que haya sido registrado en esa fecha"}
     else:
          if inf.horas==horas and inf.revisitas==revisitas and inf.estudios==estudios and inf.publicaciones==publicaciones and inf.videos==videos:
               msg={"msg":"Usted no ha realizado ningun cambio"}
          else:
               inf.horas=horas
               inf.revisitas=revisitas
               inf.estudios=estudios
               inf.publicaciones=publicaciones
               inf.videos=videos
               inf.save()
               msg={"msg":"Datos del informe modificados con exito"}
     HttpResponse(json.dumps(msg))

def usuReg(request):
     return render(request, 'usuReg.html')

def Regusu(request):
     validar=validarVacio(request.POST)
     if validar[0]:
          nombre=request.POST['nombre']
          clave=request.POST['pass']
          try:
               newUser=User.objects.create_user(username=nombre, password=clave)
          except:
               msg={'msg':'Usuario ya existe'}
          else:
               newUser.is_staff=True
               newUser.save()
               msg={'msg':'Usuario registrado con exito', 'on':1}
     else:
          msg={'msg':'Por favor no intente hacer trampa'}
     return HttpResponse(json.dumps(msg))