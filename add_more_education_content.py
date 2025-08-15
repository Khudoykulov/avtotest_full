import os
import sys
import django

# Django environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, EducationContent

def add_sample_education_content():
    """Test uchun qo'shimcha education content qo'shish"""
    
    try:
        # Yo'l harakati qoidalari kategoriyasi
        category = Category.objects.get(name_uz="Yo'l harakati qoidalari")
        
        # 7 ta qo'shimcha content qo'shamiz
        contents = [
            {
                'title': 'Asosiy yo\'l qoidalari',
                'content_type': 'text',
                'text_content': 'Yo\'l harakati qatnashchilarining asosiy majburiyatlari va huquqlari. Xavfsizlik - birinchi o\'rinda.',
                'order': 1
            },
            {
                'title': 'Haydovchilik etiket va madaniyati',
                'content_type': 'video',
                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'order': 2
            },
            {
                'title': 'Yo\'lda xavfsizlik choralari',
                'content_type': 'text',
                'text_content': 'Har bir haydovchi bilishi kerak bo\'lgan xavfsizlik qoidalari va favqulodda vaziyatlarda harakat qilish tartibi.',
                'order': 3
            },
            {
                'title': 'Piyoda va transport vositasi munosabatlari',
                'content_type': 'video',
                'video_url': 'https://www.youtube.com/watch?v=3JZ_D3ELwOQ',
                'order': 4
            },
            {
                'title': 'Yo\'l belgilariga amal qilish',
                'content_type': 'text',
                'text_content': 'Turli yo\'l belgilarining ma\'nosi va ularga to\'g\'ri amal qilish usullari.',
                'order': 5
            },
            {
                'title': 'Kechasi xavfsiz haydash',
                'content_type': 'video',
                'video_url': 'https://www.youtube.com/watch?v=ScMzIvxBSi4',
                'order': 6
            },
            {
                'title': 'Avtopark va to\'xtash qoidalari',
                'content_type': 'text',
                'text_content': 'Transport vositasini qayerda va qanday qilib to\'g\'ri to\'xtatish kerakligi haqida.',
                'order': 7
            }
        ]
        
        created_count = 0
        for content_data in contents:
            # Agar shu title'da content mavjud bo'lmasa, yaratish
            if not EducationContent.objects.filter(title=content_data['title']).exists():
                EducationContent.objects.create(
                    category=category,
                    **content_data
                )
                created_count += 1
                print(f"+ {content_data['title']} qo'shildi")
        
        print(f"\n{created_count} ta yangi education content yaratildi!")
        
        # Statistika
        total_count = EducationContent.objects.filter(category=category).count()
        print(f"'{category.name_uz}' kategoriyasida jami {total_count} ta content mavjud")
        
    except Category.DoesNotExist:
        print("Kategoriya topilmadi!")
    except Exception as e:
        print(f"Xatolik: {e}")

if __name__ == '__main__':
    add_sample_education_content()