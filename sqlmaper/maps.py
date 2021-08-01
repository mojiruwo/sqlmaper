from django.shortcuts import render


def index(request):
    context = {}
    context['hello'] = 'Hello World!'
    return render(request, 'map.html', context)