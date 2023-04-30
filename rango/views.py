from django.shortcuts import render
from django.http import HttpResponseGone

# Import the categorry model
from rango.models import Category

# Create your views here.
def index(request):
    # Context includes aboldmessage variable
    context_dict={
        'aboldmessage': 'Crunchy, creamy, cookie, candy, Cupcake!'
    }
    # From database obtain five most liked categories in descendent order
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict['categories'] = category_list
    
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    #return HttpResponseGone("Rango says here is the about page. <a href='/rango/'>Index</a>")
    return render(request, 'rango/about.html', context={})
