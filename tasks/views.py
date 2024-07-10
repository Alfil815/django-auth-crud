from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required  
#from django.http import HttpResponse


# Create your views here.
def home(request):
    return render(request, 'home.html')

def singup(request):
    
    if request.method == 'GET':
        return render(request, 'signup.html', {
        'form': UserCreationForm
    })
    else:
        if request.POST['password1'] == request.POST['password2']:
            
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('task')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'El Usuario ya Existe'
                })
                
        return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'La Copntraseña No Coincide'
                })

@login_required
def task(request):
    tasks = Task.objects.filter(user=request.user, dateclompleted__isnull=True)
    return render(request, 'task.html', {
        'tasks': tasks
    })
 
@login_required    
def task_completed(request):
    tasks = Task.objects.filter(user=request.user, dateclompleted__isnull=False).order_by('-dateclompleted')
    return render(request, 'task.html', {
        'tasks': tasks
    })    

@login_required
def create_task(request):
    
    if request == 'GET':
        return render(request, 'create_task.html', {
        'form': TaskForm
    })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('task')
        except ValueError:
            return render(request, 'create_task.html', {
        'form': TaskForm,
        'error': 'Introduce un Dato Valido'
    })

@login_required            
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('task')
        except ValueError:
            return render(request, 'task_detail.html', {
            'task': task,
            'form': form,
            'error': 'Error Al Actualizar La Tarea'
        })

@login_required
def task_complete(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.dateclompleted = timezone.now()
        task.save()
        return redirect('task')

@login_required   
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task')                                        

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
        'form': AuthenticationForm
    })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'El Usuario o La Contraseña Son Incorrectos'
            })
        else:
            login(request, user)
            return redirect('task')
           
   