from django.shortcuts import render

def consultar(request):
    return render(request, "Privilegio/consultar.html")

def nombrar(request):
    return render(request, "Privilegio/nombrar.html")

def consultarNombrados(request):
    return render(request, "Privilegio/consNombrados.html")