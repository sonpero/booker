import os
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from PIL import Image

from .models import Book
from .ebook_info import EbookInfoFetcher


def index(request):
    return HttpResponse("Hello, world. You're at the catalog index.")


def home(request):
    books_list = Book.objects.all()
    paginator = Paginator(books_list, 4)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    return render(request, 'home.html', {'books': books})


def add_book(request):
    # book = Book.objects.get()
    return render(request, 'add_book.html')#, {'book': book})


def resize_default_cover():
    image = Image.open(
        f'/volumes/homes/Alex/ebook/test/cover/default_cover.jpeg')
    standard_size = (250, 400)
    image = image.resize(standard_size)
    image = image.convert("RGB")
    image.save(f'/volumes/homes/Alex/ebook/test/cover/default_cover.jpeg')


def init_database(request):
    directory = '/volumes/homes/Alex/ebook/test'
    resize_default_cover()
    files = os.listdir(directory)
    filtered_files = [file for file in files if os.path.isfile(
        os.path.join(directory, file)) and not file.startswith('.')]

    for file in filtered_files:
        path = f'{directory}/{file}'
        print(path)
        ebook_info = EbookInfoFetcher(path)
        Book.objects.create(image_path=ebook_info.absolute_local_path_cover,
                            image=ebook_info.relative_local_path_cover,
                            title=ebook_info.title,
                            author=ebook_info.author,
                            publication_date=ebook_info.published_date,
                            language=ebook_info.language,
                            rating=None,
                            file_type=ebook_info.file_extension,
                            summary=ebook_info.description,
                            genre=ebook_info.categories,
                            file_path=ebook_info.relative_path_to_book)

    books = Book.objects.all()
    return render(request, 'home.html', {'books': books})
