import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, EducationContent

# Get categories
categories = Category.objects.all()
if not categories.exists():
    print("No categories found!")
    exit()

cat1 = categories.first()

# Add education content with videos and text
education_data = [
    {
        'title': 'Yo\'l belgilari asoslari',
        'content_type': 'video',
        'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',  # Example YouTube embed URL
        'text_content': '''
Bu video darsda siz yo'l belgilarining asosiy turlarini o'rganasiz:

• Taqiqlovchi belgilar - qizil rang bilan
• Majburiy belgilar - ko'k rang bilan  
• Ogohlantiruvchi belgilar - sariq rang bilan
• Ma'lumot beruvchi belgilar - yashil rang bilan

Har bir belgi guruhi alohida ma'noga ega va haydovchilar uchun muhim axborot beradi.
        ''',
        'order': 1
    },
    {
        'title': 'Xavfsiz haydash qoidalari',
        'content_type': 'text',
        'text_content': '''
Xavfsiz haydash - har bir haydovchining asosiy majburiyati.

## Asosiy qoidalar:

1. **Tezlik rejimi**
   - Shahar ichida maksimal 60 km/soat
   - Shahar tashqarisida maksimal 90 km/soat
   - Avtomobil yo'llarida maksimal 120 km/soat

2. **Xavfsizlik kamarini taqish**
   - Barcha yo'lovchilar majburiy ravishda taqishlari kerak
   - Bolalar uchun maxsus o'rindiqlardan foydalanish

3. **Alkogol iste'mol qilish taqiqlangan**
   - Har qanday miqdorda alkogol qonda bo'lsa haydash taqiqlanadi

4. **Telefon ishlatish**
   - Haydash paytida qo'lda telefon ishlatish taqiqlanadi
   - Hands-free qurilmalardan foydalanish mumkin

## Nima uchun muhim?

Xavfsiz haydash qoidalariga rioya qilish yo'l-transport hodisalarini oldini olishga yordam beradi va barcha yo'l foydalanuvchilarining hayotini himoya qiladi.
        ''',
        'order': 2
    },
    {
        'title': 'Birinchi yordam asoslari',
        'content_type': 'video',
        'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',  # Example YouTube embed URL
        'text_content': '''
Yo'l-transport hodisasi sodir bo'lganda birinchi yordam ko'rsatish hayotiy muhim.

Bu video darsda o'rganasiz:
• Hodisa joyini xavfsiz qilish
• Jarohatlanganlarni ko'chirish
• Nafas berish va yurak massaji
• Qon ketishini to'xtatish
• Tez yordam chaqirish

Esda tuting: birinchi yordam - bu professional tibbiy yordam kelguncha hayotni saqlash choralarini ko'rish!
        ''',
        'order': 3
    }
]

for content_data in education_data:
    content, created = EducationContent.objects.get_or_create(
        category=cat1,
        title=content_data['title'],
        defaults={
            'content_type': content_data['content_type'],
            'video_url': content_data.get('video_url', ''),
            'text_content': content_data['text_content'],
            'order': content_data['order']
        }
    )
    
    if created:
        print(f"[+] Created: {content_data['title']} ({content_data['content_type']})")
    else:
        print(f"[!] Already exists: {content_data['title']}")

print("\n[*] Education content setup completed!")
print("You can now:")
print("- View education materials at /quiz/education/")
print("- Add more content through Django admin at /admin/")
print("- Upload videos by putting YouTube embed URLs in video_url field")