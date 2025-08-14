from django.db import models
from quiz.models import Category

class EducationContent(models.Model):
    CONTENT_TYPES = [
        ('video', 'Video'),
        ('text', 'Matn'),
        ('image', 'Rasm'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='education_materials')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    text_content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='education/', blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.title
