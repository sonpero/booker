from django.db import models


class Book(models.Model):
    image_path = models.TextField(default=None, null=True, blank=True)
    image = models.ImageField(upload_to='cover/', default=None, null=True, blank=True)
    title = models.CharField(max_length=200, default=None)
    author = models.CharField(max_length=100, default=None, null=True, blank=True)
    publication_date = models.DateField(default=None, null=True, blank=True)
    language = models.CharField(max_length=10, default=None, null=True, blank=True)
    rating = models.FloatField(default=None, null=True, blank=True)
    file_type = models.CharField(max_length=8, default=None)
    summary = models.TextField(default=None, null=True, blank=True)
    genre = models.CharField(max_length=50, default=None, null=True, blank=True)
    file_path = models.TextField(default=None)

    def summary_first_chars(self):
        if self.summary is not None:
            return f'\n{self.summary[:500]} ...'

    def __str__(self):
        return self.title

