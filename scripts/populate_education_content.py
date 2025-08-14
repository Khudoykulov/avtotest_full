import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, EducationContent

def populate_education_content():
    """Add sample education content to categories"""
    
    # Get categories
    categories = Category.objects.all()
    
    education_data = {
        "Yo'l qoidalari": [
            {
                'title': "Yo'l harakati qoidalarining asoslari",
                'content_type': 'text',
                'text_content': """
Yo'l harakati qoidalari - bu barcha yo'l foydalanuvchilari uchun majburiy qoidalar to'plami.

Asosiy tamoyillar:
• Yo'l harakati xavfsizligi birinchi o'rinda turadi
• Barcha ishtirokchilar bir-birini hurmat qilishi kerak
• Qoidalarni bilish va bajarish har bir haydovchining burchi

Yo'l harakati ishtirokchilari:
1. Haydovchilar
2. Piyodalar
3. Velosipedchilar
4. Yo'lovchilar

Har bir guruh o'zining huquq va majburiyatlariga ega.
                """,
                'order': 1
            },
            {
                'title': "Haydovchilik guvohnomasi turlari",
                'content_type': 'video',
                'text_content': """
Haydovchilik guvohnomasi turlari va ularning imkoniyatlari haqida batafsil ma'lumot.

Guvohnoma toifalari:
• A toifa - mototsikllar
• B toifa - yengil avtomobillar
• C toifa - yuk avtomobillari
• D toifa - avtobuslar

Har bir toifa uchun alohida talablar va imtihonlar mavjud.
                """,
                'order': 2
            }
        ],
        "Yo'l belgilari": [
            {
                'title': "Ogohlantiruvchi belgilar",
                'content_type': 'text',
                'text_content': """
Ogohlantiruvchi belgilar haydovchilarni oldinda kutilayotgan xavf haqida ogohlantiradi.

Asosiy xususiyatlari:
• Uchburchak shakli
• Qizil ramka
• Oq yoki sariq fon

Eng muhim ogohlantiruvchi belgilar:
1. Xavfli burilish
2. Keskin ko'tarilish/tushish
3. Tor yo'l
4. Yo'l ishlari
5. Bolalar o'tish joyi

Bu belgilarni ko'rganingizda tezlikni kamaytiring va ehtiyot bo'ling.
                """,
                'order': 1
            },
            {
                'title': "Taqiqlovchi belgilar",
                'content_type': 'text',
                'text_content': """
Taqiqlovchi belgilar ma'lum harakatlarni taqiqlaydi yoki cheklaydi.

Asosiy xususiyatlari:
• Dumaloq shakli
• Qizil ramka yoki qizil chiziq
• Oq fon

Muhim taqiqlovchi belgilar:
1. Kirish taqiqlangan
2. To'xtash taqiqlangan
3. Tezlik cheklovi
4. Overtaking taqiqlangan
5. Tovush signali taqiqlangan

Bu belgilarni buzish jarimaga olib keladi.
                """,
                'order': 2
            }
        ],
        "Birinchi yordam": [
            {
                'title': "Yo'l-transport hodisasida birinchi yordam",
                'content_type': 'text',
                'text_content': """
Yo'l-transport hodisasida birinchi yordam ko'rsatish hayot saqlab qolishi mumkin.

Birinchi navbatda:
1. O'z xavfsizligingizni ta'minlang
2. Hodisa joyini belgilang
3. Tez tibbiy yordam chaqiring
4. Jarohatlanganlarni tekshiring

Asosiy qoidalar:
• Panik qilmang
• Jarohatlanganlarni keraksiz harakatlantirmang
• Qon ketishini to'xtating
• Nafas yo'llarini tozalang
• Hushsiz holatda lateral pozitsiya bering

Birinchi yordam vositalari avtomobilda doim bo'lishi kerak.
                """,
                'order': 1
            }
        ]
    }
    
    for category_name, contents in education_data.items():
        try:
            category = Category.objects.get(name_uz=category_name)
            
            for content_data in contents:
                content, created = EducationContent.objects.get_or_create(
                    category=category,
                    title=content_data['title'],
                    defaults={
                        'content_type': content_data['content_type'],
                        'text_content': content_data['text_content'],
                        'order': content_data['order']
                    }
                )
                
                if created:
                    print(f"✓ Created education content: {content.title}")
                else:
                    print(f"- Education content already exists: {content.title}")
                    
        except Category.DoesNotExist:
            print(f"✗ Category not found: {category_name}")
    
    print(f"\n📚 Education content population completed!")
    print(f"Total education materials: {EducationContent.objects.count()}")

if __name__ == '__main__':
    populate_education_content()
