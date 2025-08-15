from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from quiz.models import Category, EducationContent

@login_required
def education_view(request, category_id=None):
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        contents = EducationContent.objects.filter(category=category)
        return render(request, 'education/category.html', {
            'category': category,
            'contents': contents
        })
    else:
        categories = Category.objects.all()
        return render(request, 'education/index.html', {
            'categories': categories
        })

@login_required
def education_content_view(request, content_id):
    content = get_object_or_404(EducationContent, id=content_id)
    related_content = EducationContent.objects.filter(
        category=content.category
    ).exclude(id=content_id)[:3]
    
    return render(request, 'education/content_clean.html', {
        'content': content,
        'related_content': related_content
    })
