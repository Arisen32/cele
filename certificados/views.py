from django.shortcuts import render
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib import messages
from .forms import LoginForm
 
# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect('certificados:dashboard')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            auth_login(request, usuario)
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return redirect("certificados:dashboard")
        else:
            messages.error(request, """Por favor introduzca un nombre de usuario y
                        contraseña correctos.""")
            return redirect('certificados:login')
    context = {
        'form': form,
    }
    return render(request, 'registration/login.html', context)

 

def logout_view(request):
    auth_logout(request)
    # Redirigir a la página de inicio o cualquier otra página deseada después del logout
    return redirect('certificados:login')


@login_required
def dash_view(request):
    return render(request,"certificados/dashboard.html")










