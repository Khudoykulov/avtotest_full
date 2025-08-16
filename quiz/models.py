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
    
    # Umumiy test uchun qo'shimcha maydonlar
    variant_id = models.IntegerField(blank=True, null=True)  # Qaysi variant ishlatilgan
    test_type = models.CharField(max_length=20, choices=[
        ('ticket', 'Bilet'),
        ('category', 'Kategoriya'), 
        ('general', 'Umumiy Test'),
    ], default='general')
    
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


class AIAnalysis(models.Model):
    """AI analysis results for user tests"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_analyses')
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='ai_analyses', null=True, blank=True)
    
    # AI Analysis Content
    analysis_text = models.TextField()
    recommendations = models.JSONField(default=list)  # List of AI recommendations
    confidence_score = models.IntegerField(default=0)  # 0-100
    
    # Analysis metadata
    analysis_type = models.CharField(max_length=50, choices=[
        ('test_specific', 'Test-specific Analysis'),
        ('general', 'General Performance Analysis'),
        ('category_focused', 'Category-focused Analysis'),
    ], default='test_specific')
    
    # Performance insights
    weak_categories = models.JSONField(default=list)
    strong_categories = models.JSONField(default=list)
    improvement_suggestions = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "AI Analysis"
        verbose_name_plural = "AI Analyses"
    
    def __str__(self):
        return f"AI Analysis for {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"


class UserProgress(models.Model):
    """Advanced user progress tracking with gamification"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='progress')
    
    # XP and Level System
    total_xp = models.IntegerField(default=0)
    current_level = models.IntegerField(default=1)
    level_title = models.CharField(max_length=100, default='Yangi boshlovchi')
    
    # Streak tracking
    current_streak = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)
    last_test_date = models.DateField(null=True, blank=True)
    
    # Achievement tracking
    unlocked_achievements = models.JSONField(default=list)  # List of achievement IDs
    achievement_progress = models.JSONField(default=dict)  # Progress towards locked achievements
    
    # Learning analytics
    total_tests_completed = models.IntegerField(default=0)
    total_questions_answered = models.IntegerField(default=0)
    total_correct_answers = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    
    # Category mastery (JSON: {category_id: mastery_level})
    category_mastery = models.JSONField(default=dict)  # 0-100 mastery per category
    
    # Study habits
    preferred_study_time = models.CharField(max_length=20, choices=[
        ('morning', 'Ertalab'),
        ('afternoon', 'Tushdan keyin'),
        ('evening', 'Kechqurun'),
        ('night', 'Tunda'),
    ], blank=True)
    
    # Challenges
    active_challenges = models.JSONField(default=list)
    completed_challenges = models.JSONField(default=list)
    
    # Performance trends
    weekly_tests = models.IntegerField(default=0)
    monthly_tests = models.IntegerField(default=0)
    improvement_rate = models.FloatField(default=0.0)  # Weekly improvement percentage
    
    # Badges and rewards
    earned_badges = models.JSONField(default=list)
    current_title = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Progress"
        verbose_name_plural = "User Progress Records"
    
    def __str__(self):
        return f"{self.user.username} - Level {self.current_level} ({self.total_xp} XP)"
    
    def add_xp(self, points, reason=""):
        """Add XP and handle level ups"""
        self.total_xp += points
        old_level = self.current_level
        self.update_level()
        
        if self.current_level > old_level:
            # Level up achieved!
            return {'level_up': True, 'new_level': self.current_level, 'old_level': old_level}
        return {'level_up': False}
    
    def update_level(self):
        """Update level based on XP"""
        if self.total_xp >= 1000:
            self.current_level = 5
            self.level_title = 'Ekspert haydovchi'
        elif self.total_xp >= 500:
            self.current_level = 4
            self.level_title = 'Malakali haydovchi'
        elif self.total_xp >= 200:
            self.current_level = 3
            self.level_title = 'Tajribali o\'quvchi'
        elif self.total_xp >= 50:
            self.current_level = 2
            self.level_title = 'Faol o\'quvchi'
        else:
            self.current_level = 1
            self.level_title = 'Yangi boshlovchi'
    
    def update_streak(self):
        """Update test streak"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.last_test_date:
            if self.last_test_date == today:
                # Same day, don't update
                return
            elif self.last_test_date == today - timezone.timedelta(days=1):
                # Yesterday, continue streak
                self.current_streak += 1
            else:
                # Streak broken
                self.current_streak = 1
        else:
            # First test
            self.current_streak = 1
        
        self.last_test_date = today
        if self.current_streak > self.best_streak:
            self.best_streak = self.current_streak
    
    def get_next_level_xp(self):
        """Get XP needed for next level"""
        xp_requirements = {1: 50, 2: 200, 3: 500, 4: 1000, 5: float('inf')}
        return xp_requirements.get(self.current_level, float('inf')) - self.total_xp

class StudyPlan(models.Model):
    """Personalized study plans generated by AI"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_plans')
    
    # Plan details
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration_days = models.IntegerField(default=7)  # Plan duration in days
    
    # Plan content
    daily_tasks = models.JSONField(default=list)  # Daily study tasks
    target_categories = models.ManyToManyField(Category, blank=True)
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Boshlang\'ich'),
        ('intermediate', 'O\'rta'),
        ('advanced', 'Yuqori'),
    ], default='beginner')
    
    # Progress tracking
    is_active = models.BooleanField(default=True)
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # AI metadata
    generated_by_ai = models.BooleanField(default=True)
    ai_confidence = models.IntegerField(default=0)  # 0-100
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
