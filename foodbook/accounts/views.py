from django.shortcuts import render, redirect
from .forms import user_registration_form
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import bleach


def register_view(request):
    # # if the user is already logged in, they are redirected to the home page if they try to access this view
    # if request.user.is_authenticated:
    #     messages.warning(request, "You are already logged in.")
    #     return redirect('home')
    if request.method == 'POST':
        form = user_registration_form(request.POST)
        if form.is_valid():
            # use bleach to clean for XSS protection
            username = bleach.clean(request.POST.get('username') or "")
            email = bleach.clean(request.POST.get('email') or "")
            city = bleach.clean(request.POST.get('city') or "")
            bio = bleach.clean(request.POST.get('bio') or "")
            postal_code = bleach.clean(request.POST.get('postal_code') or "")

            # bleach cleaned input assigned to form instances 
            form.instance.username = username
            form.instance.email = email
            form.instance.city = city
            form.instance.bio = bio
            form.instance.postal_code = postal_code
            
            
            user = form.save()  # saves new user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)  
            messages.success(request, "You have successfully registered.")
            return redirect('home')  # logs new user in and redirects to the home page
    else:
        form = user_registration_form()  
    return render(request, 'register.html', {'form': form})



def login_view(request):
    # # if the user is already logged in, they are redirected to the home page if they try to access this view
    # if request.user.is_authenticated:
    #     messages.warning(request, "You are already logged in.")
    #     return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = bleach.clean(form.cleaned_data.get('username') or "")
            password = form.cleaned_data.get('password')
            
            user = authenticate(username=username, password=password)
            if user is not None:  # if the user exists
                login(request, user)
                # Redirect based on user role
                if user.is_staff or user.is_superuser:
                    messages.success(request, "You have been logged in successfully as an admin.")
                    return redirect('admin_home')
                else:
                    messages.success(request, "You have been logged in successfully.")
                    return redirect('home')
    
    else:
        form = AuthenticationForm()  

    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    # if the user is not authenticated, they are redirected to the home page if they try to access this view
    if not request.user.is_authenticated:
        messages.warning(request, "You are not logged in. Cannot logout.")
        return redirect('home')
    
    logout(request)  # recieves request to logout
    messages.success(request, "You have been logged out successfully.")
    # if request.user.is_authenticated:
    #     logout(request)
    #     return redirect('/login/?session_expired=1')
    
    return redirect('login')  # redirects to login page