from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.core.mail import send_mail
from cuser.forms import AuthenticationForm
from . forms import UserCreateForm
User = get_user_model()


def signin(request):
    if request.user.is_authenticated:
        valnext = request.GET.get('next', 'index')
        if valnext == '':
            valnext = 'index'
        return redirect(valnext)
    if request.method == 'POST':
        valnext = request.POST.get('next', 'index')
        if valnext == '':
            valnext = 'index'
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect(valnext)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            # user.first_name = form.cleaned_data.get('first_name')
            # user.last_name = form.cleaned_data.get('last_name')
            user.save()
            email_msg = 'Hey {}, thanks for signing up. Have a look around at our store because we sell slick clothing that make YOU Slick!'.format(user.first_name)
            send_mail(
                subject='Welcome to Slicks Store!',
                message=email_msg,
                from_email=None,
                recipient_list=[user.email],
                fail_silently=True,
            )
            login(request, user)
            return redirect('index')
    else:
        form = UserCreateForm()
    return render(request, 'signup.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('index')
