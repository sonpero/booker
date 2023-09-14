from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('init', views.init_database, name='init'),
    path('upload_book', views.upload_book, name='upload_book'),
    path('index', views.index, name='add_book'),
]
