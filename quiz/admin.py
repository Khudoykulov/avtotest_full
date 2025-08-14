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
    list_display = ('question_text', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('question_text',)
    inlines = [AnswerInline]

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
    list_display = ('title', 'category', 'content_type', 'order')
    list_filter = ('content_type', 'category')
    search_fields = ('title',)
