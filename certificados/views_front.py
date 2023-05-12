from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .forms import LoginForm
from gestion_escolar.models import Alumno, CursoAlumno, Periodo
from usuarios.models import Usuario
from django.http import FileResponse
import io
from pathlib import Path
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.colors import blue

from .forms import ProfileForm





# Create your views here.


def add_background(canvas, image_path):
    canvas.drawImage(image_path, 0, 0, width=letter[0], height=letter[1], preserveAspectRatio=True, mask='auto')

# Generar PDF
@login_required
def pdfgen(request, curso_id, firma):
    # Crea un objeto BytesIO para almacenar el PDF generado.
    buffer = BytesIO()

    # Crea un objeto canvas de ReportLab para generar el PDF.
    c = canvas.Canvas(buffer, pagesize=letter)

    # Agrega la imagen de fondo al PDF.

    if firma == 'True':
        BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
        STATIC_ROOT = os.path.join(BASE_DIR, "media/")
        bg_path = STATIC_ROOT + "certificados/plantilla-certificado-uts.png"
        add_background(c, bg_path)
    else:
        BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
        STATIC_ROOT = os.path.join(BASE_DIR, "media/")
        bg_path = STATIC_ROOT + "certificados/plantilla-certificado-uts_nofirma.png"
        add_background(c, bg_path)
    # Obtención de datos

    ## Nombre del Curso
    curso = CursoAlumno.objects.get(pk=curso_id)

    ## Fecha de Inicio y de Término
    meses = {
        "January": "enero",
        "February": "febrero",
        "March": "marzo",
        "April": "abril",
        "May": "mayo",
        "June": "junio",
        "July": "julio",
        "August": "agosto",
        "September": "septiembre",
        "October": "octubre",
        "November": "noviembre",
        "December": "diciembre",
    }

    fecha = curso.periodo.fecha_inicio.strftime("%d")
    fecha += " de " + meses[curso.periodo.fecha_inicio.strftime("%B")]
    fecha += " del " + curso.periodo.fecha_inicio.strftime("%Y")
    fecha += " al " + curso.periodo.fecha_fin.strftime("%d")
    fecha += " de " + meses[curso.periodo.fecha_fin.strftime("%B")]
    fecha += " del " + curso.periodo.fecha_fin.strftime("%Y")


    # Agrega contenido al PDF.
    text_nombre = str(request.user)
    text_subtitulo =  str(curso)
    text_fecha = "Salamanca, Gto., del " + str(fecha)
    text_width = c.stringWidth(text_nombre, "Helvetica-Bold", 16)
    x = (letter[0] - text_width) / 2
    y = letter[1] / 2.25

    # Pasada 1: Nombre del Alumno
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(HexColor('#204089'))
    c.drawString(x, y, text_nombre)

    # Pasada 2: Motivo de la constancia
    lines = [
        "Por haber concluido satisfactoriamente el curso \"" + text_subtitulo +"\"",
        "impartido en las instalaciones de la Universidad Tecnológica de Salamanca."
    ]
    
    textob = c.beginText()

    text_width = c.stringWidth(lines[0], "Helvetica", 14)
    x = (letter[0] - text_width) / 2

    textob.setTextOrigin(x, (letter[1] / 2.5))
    textob.setFont("Helvetica", 14)
    textob.setFillColor(HexColor('#8d8989'))
    for line in lines:
        textob.textLine(line)
        c.drawText(textob)
        text_width = c.stringWidth(lines[1], "Helvetica", 14)
        x = (letter[0] - text_width) / 2
        textob.setTextOrigin(x, (letter[1] / 2.65))

    # Pasada 3: Fecha de Término 
    text_width = c.stringWidth(text_fecha, "Helvetica", 10)
    x = (letter[0] - text_width) / 2
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor('#9f9b9b'))
    c.drawString(x, (letter[1] / 3.04), text_fecha)

    # Finaliza el PDF.
    c.showPage()
    c.save()

    # Lee los contenidos del BytesIO y devuelve una respuesta HTTP con el PDF generado.
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="prueba.pdf"'
    return response


@login_required
def listar_cursos(request):
    usuario = request.user
    curso_list = CursoAlumno.objects.filter(alumno=usuario)
   

    return render(request, 'certificados/m.html',
                  {'curso_list': curso_list}) 

@login_required
def mostrar_curso(request, curso_id):
    selcurso = CursoAlumno.objects.get(pk=curso_id)

    return render(request, 'certificados/mis_cursos_detail.html',
                  {'selcurso': selcurso})



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



def profile_user(request):
    usuario = request.user
    alumno = Alumno.objects.get(username=usuario.username)

    print(alumno.nombre)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=alumno)
        if form.is_valid():
            form.save()
            return redirect('certificados:profile')  # Redirige a la página de perfil actualizada
    else:
        form = ProfileForm(instance=alumno)

    return render(request, "certificados/profile.html", {'form': form, 'alumno': alumno})

def curso_info(request):
    usuario = request.user
    curso_list = CursoAlumno.objects.filter(alumno=usuario) 
    return render(request, "certificados/info.html", {'curso_list': curso_list})




@login_required
def dash_view(request):
    usuario = request.user
    curso_list = CursoAlumno.objects.filter(alumno=usuario)
   
    return render(request,"certificados/dashboard.html", {'curso_list': curso_list})








  

 



  













