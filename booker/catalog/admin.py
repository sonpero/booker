from django.contrib import admin
from .models import Book, UploadBook

# Register your models here.
admin.site.register(Book)
admin.site.register(UploadBook)

