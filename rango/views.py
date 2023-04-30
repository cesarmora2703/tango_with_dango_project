from django.shortcuts import render
from django.http import HttpResponseGone

# Import the categorry model
from rango.models import Category, Page

# Create your views here.
def index(request):
    # Context includes aboldmessage variable
    context_dict={
        'aboldmessage': 'Crunchy, creamy, cookie, candy, Cupcake!'
    }
    # From database obtain five most liked categories in descendent order
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict['categories'] = category_list
    # Five most viewed page
    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages']=page_list

    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    #return HttpResponseGone("Rango says here is the about page. <a href='/rango/'>Index</a>")
    return render(request, 'rango/about.html', context={})


def show_category(request, category_name_slug):
    # Create the contex dictionary which we can pass
    #to the template rendering engine.
    context_dict = {}

    try:
        #Check if a category with a slug given name exists.
        #If no exists raise an exception
        category = Category.objects.get(slug=category_name_slug)
        #Retrieve the assciated pages
        pages = Page.objects.filter(category=category)
        #Add results to the context dictionary
        context_dict['pages']=pages
        context_dict['category']=category
    except Category.DoesNotExist:
        context_dict['category']=None
        context_dict['pages']=None

    #Go render the response an return it to the client
    return render(request, 'rango/category.html', context=context_dict)

