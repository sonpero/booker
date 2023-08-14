from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_date = models.DateField()
    summary = models.TextField()
    image = models.ImageField(upload_to='books')
    genre = models.CharField(max_length=50)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.title
