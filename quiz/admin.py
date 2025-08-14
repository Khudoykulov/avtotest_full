from django.contrib import admin
from .models import Category, Question, Answer, TestTicket, TestResult, UserAnswer, EducationContent

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name', 'created_at')
    search_fields = ('name', 'name_uz')

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('get_short_question', 'category', 'answers_count', 'has_image', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('question_text',)
    inlines = [AnswerInline]
    
    def get_short_question(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    get_short_question.short_description = 'Savol'
    
    def answers_count(self, obj):
        return obj.answers.count()
    answers_count.short_description = 'Javoblar soni'
    
    def has_image(self, obj):
        return "✅ Ha" if obj.image else "❌ Yo'q"
    has_image.short_description = 'Rasm'

@admin.register(TestTicket)
class TestTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'name', 'created_at')
    filter_horizontal = ('questions',)

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'total_questions', 'passed', 'created_at')
    list_filter = ('passed', 'created_at', 'category', 'ticket')
    search_fields = ('user__username',)

@admin.register(EducationContent)
class EducationContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'content_type', 'has_video', 'has_image', 'order')
    list_filter = ('content_type', 'category')
    search_fields = ('title',)
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('category', 'title', 'content_type', 'order')
        }),
        ('Kontent', {
            'fields': ('text_content',),
        }),
        ('Video', {
            'fields': ('video_url',),
            'description': 'YouTube, Vimeo yoki boshqa video platformalarning embed URL manzilini kiriting'
        }),
        ('Rasm', {
            'fields': ('image',),
        }),
    )
    
    def has_video(self, obj):
        return "✅ Ha" if obj.video_url else "❌ Yo'q"
    has_video.short_description = 'Video'
    
    def has_image(self, obj):
        return "✅ Ha" if obj.image else "❌ Yo'q"
    has_image.short_description = 'Rasm'
