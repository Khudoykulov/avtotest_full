from django.urls import path
from . import views

app_name = 'education'

urlpatterns = [
    path('', views.education_view, name='index'),
    path('category/<int:category_id>/', views.education_view, name='category'),
    path('content/<int:content_id>/', views.education_content_view, name='content'),
]