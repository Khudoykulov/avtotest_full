from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.html import format_html
from django import forms
from .models import Category, Question, Answer, TestTicket, TestResult, UserAnswer, EducationContent
import random


class TestTicketForm(forms.ModelForm):
    """Custom form for TestTicket with optional questions field"""
    
    class Meta:
        model = TestTicket
        fields = ['ticket_number', 'name', 'questions']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Questions field'ni majburiy qilmaslik
        self.fields['questions'].required = False
        
        # Help text qo'shish
        if not self.instance.pk:  # Yangi bilet
            self.fields['questions'].help_text = (
                '<div style="background: #d1ecf1; padding: 10px; border-radius: 4px; margin: 5px 0; border-left: 4px solid #bee5eb;">'
                '🎯 <strong>Automatic yaratish:</strong> Savollar tanlamasangiz, bilet saqlanganida 161 ta savoldan 20 tasi tasodifiy tanlanadi.<br>'
                '✏️ Bilet yaratilgach, uni tahrirlash orqali savollarni o\'zgartirishingiz mumkin.'
                '</div>'
            )
        else:  # Mavjud bilet
            self.fields['questions'].help_text = (
                '<div style="background: #f8d7da; padding: 8px; border-radius: 4px; margin: 5px 0; border-left: 4px solid #f5c6cb;">'
                '💡 <strong>Maslahat:</strong> Savollarni o\'zgartirishingiz yoki "🎲 Random" tugmasini ishlatishingiz mumkin.'
                '</div>'
            )

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
    form = TestTicketForm  # Custom form ishlatish
    list_display = ('ticket_number', 'name', 'questions_count', 'generate_random_button', 'created_at')
    filter_horizontal = ('questions',)
    actions = ['generate_random_questions_action']
    
    def save_model(self, request, obj, form, change):
        """Bilet yaratilganda automatic random savollar qo'shish"""
        is_new = obj.pk is None
        
        # Biletni saqlash
        super().save_model(request, obj, form, change)
        
        # Agar yangi bilet bo'lsa va savollar bo'sh bo'lsa, automatic qo'shish
        if is_new:
            # ManyToMany field save qilgandan keyin tekshirish
            if obj.questions.count() == 0:
                self.auto_generate_questions(obj, request)
    
    def save_related(self, request, form, formsets, change):
        """ManyToMany save qilgandan keyin tekshirish"""
        super().save_related(request, form, formsets, change)
        
        # Agar yangi bilet bo'lsa va savollar hali ham bo'sh bo'lsa
        if not change and form.instance.questions.count() == 0:
            self.auto_generate_questions(form.instance, request)
    
    def auto_generate_questions(self, ticket, request):
        """Bilet uchun automatic 20 ta random savol yaratish"""
        try:
            # Barcha savollarni olish (test category'siz)
            all_questions = list(Question.objects.exclude(category__name='test'))
            
            if len(all_questions) < 20:
                messages.warning(
                    request, 
                    f'Bazada faqat {len(all_questions)} ta savol bor. Bilet yaratildi, lekin savollar qo\'shilmadi.'
                )
                return
            
            # 20 ta tasodifiy savol tanlash
            selected_questions = random.sample(all_questions, 20)
            
            # Biletga savollarni qo'shish
            ticket.questions.set(selected_questions)
            
            messages.success(
                request, 
                f'Bilet #{ticket.ticket_number} yaratildi va 20 ta tasodifiy savol automatic qo\'shildi!'
            )
            
        except Exception as e:
            messages.error(request, f'Savollar qo\'shishda xatolik: {str(e)}')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:ticket_id>/generate-random/',
                self.admin_site.admin_view(self.generate_random_questions_view),
                name='quiz_testticket_generate_random',
            ),
            path(
                'generate-all-random/',
                self.admin_site.admin_view(self.generate_all_random_questions_view),
                name='quiz_testticket_generate_all_random',
            ),
        ]
        return custom_urls + urls
    
    def questions_count(self, obj):
        count = obj.questions.count()
        if count >= 20:
            return format_html('<span style="color: green; font-weight: bold;">✅ {} ta</span>', count)
        else:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ {} ta</span>', count)
    questions_count.short_description = 'Savollar soni'
    
    def generate_random_button(self, obj):
        return format_html(
            '<a class="button" href="{}" style="background: #417690; color: white; padding: 5px 10px; '
            'text-decoration: none; border-radius: 4px; font-size: 11px;">🎲 20 ta random savol</a>',
            f'/admin/quiz/testticket/{obj.pk}/generate-random/'
        )
    generate_random_button.short_description = 'Tasodifiy savollar'
    
    def generate_random_questions_view(self, request, ticket_id):
        """Bitta bilet uchun 20 ta tasodifiy savol yaratish"""
        try:
            ticket = TestTicket.objects.get(pk=ticket_id)
            
            # Barcha savollarni olish (test category'siz)
            all_questions = list(Question.objects.exclude(category__name='test'))
            
            if len(all_questions) < 20:
                messages.error(request, f'Bazada faqat {len(all_questions)} ta savol bor. Kamida 20 ta savol kerak!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/quiz/testticket/'))
            
            # 20 ta tasodifiy savol tanlash
            selected_questions = random.sample(all_questions, 20)
            
            # Biletga savollarni qo'shish
            ticket.questions.set(selected_questions)
            
            messages.success(
                request, 
                f'Bilet #{ticket.ticket_number} uchun 20 ta tasodifiy savol muvaffaqiyatli yaratildi!'
            )
            
        except TestTicket.DoesNotExist:
            messages.error(request, 'Bilet topilmadi!')
        except Exception as e:
            messages.error(request, f'Xatolik yuz berdi: {str(e)}')
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/quiz/testticket/'))
    
    def generate_random_questions_action(self, request, queryset):
        """Ko'p biletlar uchun tasodifiy savollar yaratish"""
        success_count = 0
        
        # Barcha savollarni olish
        all_questions = list(Question.objects.exclude(category__name='test'))
        
        if len(all_questions) < 20:
            messages.error(request, f'Bazada faqat {len(all_questions)} ta savol bor. Kamida 20 ta savol kerak!')
            return
        
        for ticket in queryset:
            try:
                # Har bilet uchun 20 ta tasodifiy savol
                selected_questions = random.sample(all_questions, 20)
                ticket.questions.set(selected_questions)
                success_count += 1
            except Exception as e:
                messages.error(request, f'Bilet #{ticket.ticket_number} uchun xatolik: {str(e)}')
        
        messages.success(request, f'{success_count} ta bilet uchun tasodifiy savollar yaratildi!')
    
    generate_random_questions_action.short_description = "🎲 Tanlangan biletlar uchun tasodifiy savollar yaratish"
    
    def generate_all_random_questions_view(self, request):
        """Barcha biletlar uchun tasodifiy savollar yaratish"""
        try:
            # Barcha biletlarni olish
            all_tickets = TestTicket.objects.all()
            
            # Barcha savollarni olish
            all_questions = list(Question.objects.exclude(category__name='test'))
            
            if len(all_questions) < 20:
                messages.error(request, f'Bazada faqat {len(all_questions)} ta savol bor. Kamida 20 ta savol kerak!')
                return HttpResponseRedirect('/admin/quiz/testticket/')
            
            success_count = 0
            for ticket in all_tickets:
                try:
                    # Har bilet uchun 20 ta tasodifiy savol
                    selected_questions = random.sample(all_questions, 20)
                    ticket.questions.set(selected_questions)
                    success_count += 1
                except Exception as e:
                    messages.error(request, f'Bilet #{ticket.ticket_number} uchun xatolik: {str(e)}')
            
            messages.success(
                request, 
                f'Barcha {success_count} ta bilet uchun tasodifiy savollar muvaffaqiyatli yaratildi!'
            )
            
        except Exception as e:
            messages.error(request, f'Xatolik yuz berdi: {str(e)}')
        
        return HttpResponseRedirect('/admin/quiz/testticket/')
    
    def changelist_view(self, request, extra_context=None):
        """Admin ro'yxat sahifasiga qo'shimcha button qo'shish"""
        extra_context = extra_context or {}
        extra_context['custom_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

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
