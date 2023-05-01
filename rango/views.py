from django.shortcuts import render
from django.http import HttpResponseGone
from django.shortcuts import redirect
from django.urls import reverse

# Import the categorry model
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

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


def add_category(request):
    form = CategoryForm()
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        #Have we been provided with a valid data
        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)

            return redirect('/rango/')
        else:
            # The supplied form contained errors
            # Just print them to the terminal.
            print(form.errors)

    # Will handle the bad form, new form, or no form suppied cases.
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    # Check if category exists
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category=None

    # If category is  not found cannot add a page
    if category is None:
        return redirect(reverse('rango:index'))

    form = PageForm()
    # A HTTP POST?
    if request.method == 'POST':
        form = PageForm(request.POST)
        #Have we been provided with a valid data
        if form.is_valid():
            # Save the new category to the database
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug': category_name_slug}))
        else:
            # The supplied form contained errors
            # Just print them to the terminal.
            print(form.errors)

    # Will handle the bad form, new form, or no form suppied cases.
    # Render the form with error messages (if any).
    context_dict={'form': form, 'category':category}
    return render(request, 'rango/add_page.html', context = context_dict)