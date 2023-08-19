from django.db import models


class Book(models.Model):
    image_path = models.TextField(default=None)
    title = models.CharField(max_length=200, default=None)
    author = models.CharField(max_length=100, default=None)
    publication_date = models.DateField(default=None)
    language = models.CharField(max_length=10, default=None)
    rating = models.FloatField(default=None)
    file_type = models.CharField(max_length=8, default=None)
    summary = models.TextField(default=None)
    genre = models.CharField(max_length=50, default=None)
    file_path = models.TextField(default=None)

    def __str__(self):
        return self.title
