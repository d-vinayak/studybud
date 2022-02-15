from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm

# rooms = [
#     {'id':1, 'name':"This is room 1"},
#     {'id':2, 'name':"This is room 2"},
#     {'id':3, 'name':"This is room 3"}
# ]

# Create your views here.
def login_page(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try: 
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'logged in successfully')
            return redirect('home')
        else:
            messages.error(request, 'username or passwrod is incorrect')


    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logout_user(request):
    logout(request)
    messages.success(request, 'logged out successfully')
    return redirect('home')

def register_user(request):

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            # form.save()
            login(request, user)
            messages.success(request, 'Account created successfully')
            return redirect('home')

    else:
        form = UserCreationForm()
    return render(request, 'base/login_register.html', {'form': form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__contains=q) |
        Q(description__icontains=q)
    ) 
    topics = Topic.objects.all()
    room_counts = rooms.count()
    context = {'rooms': rooms, 'topics': topics, 'room_counts': room_counts}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body'),
        )

        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not authorised')


    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
        return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj': room}
    return render(request, 'base/delete.html', {'obj':room})
