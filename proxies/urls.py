from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.proxy_create, name='proxy_create'),
    path('<int:pk>/edit/', views.proxy_edit, name='proxy_edit'),
    path('<int:pk>/delete/', views.proxy_delete, name='proxy_delete'),
]
