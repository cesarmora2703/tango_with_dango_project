from django.shortcuts import render
from django.http import HttpResponseGone

# Create your views here.
def index(request):
    # Context includes aboldmessage variable
    context_dict={
        'aboldmessage': 'Crunchy, creamy, cookie, candy, Cupcake!'
    }
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    #return HttpResponseGone("Rango says here is the about page. <a href='/rango/'>Index</a>")
    return render(request, 'rango/about.html', context={})
