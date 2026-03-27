from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_total_tests', 'best_score')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    readonly_fields = ('get_total_tests',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha ma\'lumotlar', {'fields': ('phone_number', 'birth_date', 'get_total_tests', 'best_score')}),
    )
    
    def get_total_tests(self, obj):
        """Admin panelda ko'rsatish uchun test sonini olish"""
        return obj.total_tests_taken
    get_total_tests.short_description = 'Jami testlar'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_language')
    list_filter = ('preferred_language',)
    search_fields = ('user__username',)
