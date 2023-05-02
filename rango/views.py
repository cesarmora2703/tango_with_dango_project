from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

# Import the models
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
# Import the forms
from rango.forms import UserForm, UserProfileForm

# Create your views here.


def index(request):
    # Context includes aboldmessage variable
    context_dict = {
        'aboldmessage': 'Crunchy, creamy, cookie, candy, Cupcake!'
    }
    # From database obtain five most liked categories in descendent order
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict['categories'] = category_list
    # Five most viewed page
    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list
    context_dict['extra'] = 'Fom the model soluctio on github'

    # Server side cookies
    context_dict['visits'] = get_server_side_cookie(request, 'visits', 1)
    # Side server side cookie funtion
    visitor_cookie_handler(request)
    # Return response back to the user, updating any cookies that need changed.
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    # return HttpResponseGone("Rango says here is the about page. <a href='/rango/'>Index</a>")
    return render(request, 'rango/about.html', context={})


def show_category(request, category_name_slug):
    # Create the contex dictionary which we can pass
    # to the template rendering engine.
    context_dict = {}

    try:
        # Check if a category with a slug given name exists.
        # If no exists raise an exception
        category = Category.objects.get(slug=category_name_slug)
        # Retrieve the assciated pages
        pages = Page.objects.filter(category=category)
        # Add results to the context dictionary
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    # Go render the response an return it to the client
    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # Have we been provided with a valid data
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

    context_dict = {'form': form, }
    return render(request, 'rango/add_category.html', context=context_dict)


def add_page(request, category_name_slug):
    # Check if category exists
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    # If category is  not found cannot add a page
    if category is None:
        return redirect(reverse('rango:index'))

    form = PageForm()
    # A HTTP POST?
    if request.method == 'POST':
        form = PageForm(request.POST)
        # Have we been provided with a valid data
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
    context_dict = {'form': form, 'category': category}

    return render(request, 'rango/add_page.html', context=context_dict)


def register(request):
    '''
    A boolean value for telling the template whether the 
    registration was successful.
    Set to false initially. Code changes value to True when
    registrarion succeeds.
    '''
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attemp to grab information from the raw form information.
        # Note thet we make use of both UserForm and UserProfileForm.
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()
            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves,
            # we set commit=False. This delays saving the model
            # until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and
            # put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to indicate that the template
            # registration was successful.
            registered = True
        else:
            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal.
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances.
        # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,
                  'rango/register.html',
                  context={'user_form': user_form,
                           'profile_form': profile_form,
                           'registered': registered})


def user_login(request):
    # If the request is a HTTP pOST, try to pull out the reelvant information
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # Fron login form using request.POST.get()
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if a user/password combination is valid
        user = authenticate(username=username, password=password)

        # Act acordingly depending on what found
        if user:
            # Is the account active?
            if user.is_active:
                # Account valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse(reverse('rango:index'))
        else:
            # Bad login details were provided. Can't log in user
            print(f'Invalid login details: {username}, {password}')
            return HttpResponse('Invalid login details supplied')

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be HTTP GET
    else:
        # No context variable to pass to the template system
        return render(request, 'rango/login.html')


def some_view(request):
    if not request.user.is_authenticated():
        return HttpResponse("You are logged in.")
    else:
        return HttpResponse("You are not logged in.")


@login_required
def restricted(request):
    context_dict = {'message': "Since you're logged in, you can see this text!"}
    return render(request, 'rango/restricted.html', context=context_dict)


@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('rango:index'))


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

# Updated the function for cookies server side


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(
        request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(
        last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # Update/set the visits cookie
    request.session['visits'] = visits
