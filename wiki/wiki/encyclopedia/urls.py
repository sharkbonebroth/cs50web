from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.reqSearch, name="reqSearch"),
    path("<str:entryName>", views.reqEntry, name="reqEntry"),
]
