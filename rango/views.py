from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm
from rango.forms import UserProfileForm
from django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass
    # to the template rendering engine.
    context_dict = {}
    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # Note that filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages

        # We also add the category object from
        # the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything -
        # the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None
    # Go render the response and return it to the client.
    return render(request,'rango/category.html', context_dict)

def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary
    # that will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    # Render the response and send it back!
    return render(request,'rango/index.html', context=context_dict)

def about(request):
    context_dict = {'boldmessage': "This tutorial has been put together by Peter IP!"}
    return render(request, 'rango/about.html', {})


@login_required
def add_category(request):
    form = CategoryForm()
    if request.method =='POST':
        form = CategoryForm(request.POST)
        #have we been provided with a valid form
        if form.is_valid():
            #Save the new category to the database
            cat = form.save(commit=True)
            print(cat, cat.slug)
            #redircet back to index view
            return redirect(reverse('rango:index'))
        else:
            #the form contained errors
            print(form.errors)
    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html',{'form':form})

@login_required
def add_page(request,category_name_slug):
    try:
        category=Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category=None
    if category is None:
        return redirect(reverse('rango:index'))
    form=PageForm()
    if request.method =='POST':
        form=PageForm(request.POST)
        if form.is_valid():
            if category:
                page =form.save(commit=False)
                page.category = category
                page.views =0
                page.save()
                return redirect(reverse('rango:show_category',kwargs={'category_name_slug':category_name_slug}))
        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    registered = False
    if request.method =='POST':
        user_form=UserForm(request.POST)
        profile_form=UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user =user
            if 'picture' in request.FILES:
                profile.pictures = request.FILES['picture']
            profile.save()
            registered=True
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form=UserForm()
        profile_form=UserProfileForm()
    return render(request,'rango/register.html',context ={'user_form':user_form,'profile_form':profile_form,'registered':registered})

def user_login(request):
    if request.method =='POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while request.POST['<variable>']
        # will raise a KeyError exception.
        username= request.POST.get('username')
        password = request.POST.get('password')
        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username,password=password)
        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage. 
                login(request,user)
                return redirect(reverse('rango:index'))
            else:
                #An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied")
            # The request is not a HTTP POST, so display the login form
            # This scenario would most likely be a HTTP GET
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request,'rango/login.html')

@login_required
def restricted(request):
    return render(request,'rango/restricted.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))