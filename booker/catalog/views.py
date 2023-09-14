import os
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest
from django.utils.deconstruct import deconstructible
from PIL import Image

from .configuration import storage_directory
from .models import Book, UploadBook
from .ebook_info import EbookInfoFetcher, MetadataExplorer, GoogleApiCaller
from .forms import BookUploader


def index(request):
    return HttpResponse("Hello, world. You're at the catalog index.")


def home(request):
    books_list = Book.objects.all().order_by('title')
    paginator = Paginator(books_list, 4)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    return render(request, 'home.html', {'books': books})


def upload_book(request):
    if request.method == 'POST':
        form = BookUploader(request.POST, request.FILES)
        files = request.FILES.getlist('book_file')
        invalid_file = []
        if form.is_valid():
            for f in files:
                extension_check = AllowedExtensions(filename=f.name)

                # do not remove == True !!
                if extension_check == True:
                    file_instance = UploadBook(book_file=f)
                    file_instance.save()
                    path = file_instance.book_file.file.name
                    insert_book_info_in_database(path)
                    file_instance.delete()
                else:
                    invalid_file.append(f.name)
            if invalid_file:
                invalid_file_names = ", ".join(invalid_file)
                return HttpResponseBadRequest(f'Invalid file type for '
                                              f'{invalid_file_names}')

    else:
        form = BookUploader()
    return render(request, 'upload.html', {'form': form})


def init_database(request):
    resize_default_cover()

    files = os.listdir(storage_directory)
    filtered_files = [file for file in files if os.path.isfile(
        os.path.join(storage_directory, file)) and not file.startswith('.')]

    for file in filtered_files:
        path = f'{storage_directory}/{file}'
        print(path)
        insert_book_info_in_database(path)

    books = Book.objects.all()
    return render(request, 'home.html', {'books': books})


def insert_book_info_in_database(path):
    metadata_from_file = MetadataExplorer(path).run()
    metadata_from_google = GoogleApiCaller(
        metadata_from_file).run()

    ebook_info = EbookInfoFetcher(metadata_from_file,
                                  metadata_from_google)

    ebook_info.run()

    Book.objects.create(
        image_path=ebook_info.absolute_local_path_cover,
        image=ebook_info.relative_local_path_cover,
        title=ebook_info.title[:198],
        author=ebook_info.author,
        publication_date=ebook_info.published_date,
        language=ebook_info.language,
        rating=None,
        file_type=ebook_info.file_extension,
        summary=ebook_info.description,
        genre=ebook_info.categories,
        file_path=ebook_info.relative_path_to_book)


def resize_default_cover():
    image = Image.open(
        f'{storage_directory}/cover/default_cover.jpeg')
    standard_size = (250, 400)
    image = image.resize(standard_size)
    image = image.convert("RGB")
    image.save(f'{storage_directory}/cover/default_cover.jpeg')


@deconstructible
class AllowedExtensions:
    allowed_extensions = ['epub', 'pdf', 'obi']

    def __init__(self, *args, **kwargs):
        self.file_extension = kwargs['filename'].split('.')[-1]

    def __eq__(self, other):
        return self.file_extension in self.allowed_extensions

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, frozenset(self.allowed_extensions)))
