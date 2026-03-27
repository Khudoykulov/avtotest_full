from django.shortcuts import render
from django.http import HttpResponse
from quiz.models import Category, EducationContent

def test_view(request):
    categories = Category.objects.all()
    videos = EducationContent.objects.filter(content_type='video')
    
    return render(request, 'test_page.html', {
        'categories': categories,
        'videos': videos
    })