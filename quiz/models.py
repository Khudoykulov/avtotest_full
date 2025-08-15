from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    """Quiz categories like traffic rules, road signs, etc."""
    name = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name_uz

class Question(models.Model):
    """Individual quiz questions"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    image = models.ImageField(upload_to='questions/', blank=True, null=True)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.question_text[:50]

class Answer(models.Model):
    """Answer choices for questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.question.question_text[:30]} - {self.answer_text[:30]}"

class TestTicket(models.Model):
    """Test tickets containing 20 questions each"""
    ticket_number = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    questions = models.ManyToManyField(Question, related_name='tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Bilet {self.ticket_number}"

class TestResult(models.Model):
    """User test results"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    ticket = models.ForeignKey(TestTicket, on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    time_taken = models.DurationField()
    passed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.score}/{self.total_questions}"

class UserAnswer(models.Model):
    """Track user answers for analysis"""
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    
    def __str__(self):
        return f"{self.test_result.user.username} - Q{self.question.id}"

class EducationContent(models.Model):
    """Educational materials for learning"""
    CONTENT_TYPES = [
        ('video', 'Video'),
        ('text', 'Matn'),
        ('image', 'Rasm'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='education_content')
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
