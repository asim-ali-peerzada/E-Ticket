from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login 
from django.http import HttpResponseRedirect,HttpResponse
from .models import *
from django.urls import reverse
from django.core.mail import send_mail
from datetime import datetime
from .forms import *
from django.contrib.auth.decorators import login_required




def login_page(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)


        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'Your account is not verified.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email , password= password)
        if user_obj:
            login(request , user_obj)
            return redirect(reverse('bookings'))

        

        messages.warning(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/login.html')


def register_page(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        user_obj = User.objects.filter(username = email)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        user_obj = User.objects.create(first_name = first_name , last_name= last_name , email = email , username = email)
        user_obj.set_password(password)
        user_obj.save()
        
        user_profile = user_obj.profile
        user_profile.phone_number = phone_number
        user_profile.save()
        
        messages.success(request, 'An email has been sent on your mail.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/register.html')




def activate_email(request , email_token):
    try:
        user = Profile.objects.get(email_token= email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Invalid Email token')
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}')
    

from django.http import JsonResponse

def home(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})  # Return success response
    else:
        form = ContactForm()
    return render(request, 'base/home.html', {'form': form})



@login_required
def bookings(request):
    is_authenticated = request.user.is_authenticated
    is_employee = request.user.profile.is_employee if is_authenticated else False
    first_name = request.user.first_name if is_authenticated else ""

    return render(
        request, 'bookings/bookings.html',
        {
            'is_authenticated': is_authenticated,
            'is_employee': is_employee,
            'first_name': first_name
        }
    )

