from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('init', views.init_database, name='init'),
    path('upload_book', views.upload_book, name='upload_book'),
    path('search', views.search_view, name='search_view'),
    path('index', views.index, name='index'),
]
