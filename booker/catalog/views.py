from django.shortcuts import render
from django.http import HttpResponse
from .models import Book


def index(request):
    return HttpResponse("Hello, world. You're at the catalog index.")


def home(request):
    books = Book.objects.all()
    return render(request, 'home.html', {'books': books})


def add_book(request):
    # book = Book.objects.get()
    return render(request, 'add_book.html')#, {'book': book})
