from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from master_data . models import *


from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login_view(request):
    heading = "Login"
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            profile=UserProfile.objects.filter(user__username = username, role__role_type__in=[0,2])
            if profile.exists():
                if profile.filter(status=2).exists():
                    apl_linakage = ApplicationUserStateLinkage.objects.filter(user=user)
                    if not apl_linakage.exists() and profile.first().role.id in [8,9,10]:
                        error_message = "Your zone are not yet configuration. Contact Super admin"
                        logout(request)
                    else:
                        role_id = profile.values_list('role__id', flat=True)
                        request.session["role_id"]=list(role_id )[0]
                        login(request, user)
                        if request.session.get('role_id') == 7:
                            return redirect('/spectacle-list/')
                        elif request.session.get('role_id') == 6:
                            return redirect('/orders/')
                        else:
                            return redirect('/dashboard/')
                else:
                    error_message = "Your account has been deactivated. Contact Super admin"
                    logout(request)
            else:
                error_message = "User does not have the required role. Contact Super admin."
                logout(request)
        else:
            error_message = "Invalid Username or Password"
            logout(request)
    else:
        logout(request)
    return render(request, 'dashboard/login.html', locals())

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/')

@login_required(login_url='/login/')
def sidebar_view(request):
    s="hello write any thing here"
    return render(request,'local.html')

@login_required(login_url='/login/')
def dashboard(request):
    greeting = {}
    greeting['heading'] = "Dashboard"
    return render (request,'partials/dashboard.html',greeting) 

@login_required(login_url='/login/')
def form_validate(request):
    greeting = {}
    greeting['heading'] = "Form Validation"
    return render (request,'forms/formvalidate.html',greeting)        


@login_required(login_url='/login/')
def send_login_email(request):
    user = request.user
    current_site = get_current_site(request)
    mail_subject = 'Your Login Details'
    username = request.user
    password = request.user.password
    context = {
        'user': user,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        'domain': current_site.domain,
    }
    message = render_to_string('login_email.html', locals())
    send_mail(mail_subject, message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email])

    return HttpResponse(message,'Email sent successfully')