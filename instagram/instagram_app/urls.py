from django.urls import path
from instagram_app import views

urlpatterns = [
    path('', views.get_media, name = "get_media"),
]