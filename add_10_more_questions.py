import os
import sys
import django

# Django environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, Question, Answer

def add_more_questions():
    """Yana 10 ta savol qo'shish"""
    
    # Mavjud category'larni olish
    categories = {
        'traffic_rules': Category.objects.get(name_uz="Yo'l harakati qoidalari"),
        'road_signs': Category.objects.get(name_uz="Yo'l belgilari"),
        'vehicle_tech': Category.objects.get(name_uz="Transport vositasi texnikasi"),
        'emergency': Category.objects.get(name_uz="Favqulodda holatlar"),
        'speed_limits': Category.objects.get(name_uz="Tezlik chegarasi"),
    }
    
    # Qo'shimcha 10 ta savol
    questions_data = [
        {
            'category': 'traffic_rules',
            'question': 'Avtomobil haydovchisi necha yoshdan haydovchilik guvohnomasini olishi mumkin?',
            'answers': [
                ('18 yoshdan', True),
                ('16 yoshdan', False),
                ('21 yoshdan', False),
                ('25 yoshdan', False)
            ]
        },
        {
            'category': 'traffic_rules', 
            'question': 'Yo\'lda piyodalar qaysi tomonda yurishlari kerak?',
            'answers': [
                ('Transport harakatiga qarshi tomonda', True),
                ('Transport harakati bo\'yicha', False),
                ('O\'ng tomonda', False),
                ('O\'rtada', False)
            ]
        },
        {
            'category': 'road_signs',
            'question': 'Piyoda o\'tkazmasida haydovchi nimaga majbur?',
            'answers': [
                ('Piyodalarga yo\'l berish', True),
                ('Ovoz signali berish', False),
                ('Tezlikni oshirish', False),
                ('To\'xtamasdan o\'tish', False)
            ]
        },
        {
            'category': 'road_signs',
            'question': 'Yo\'lda "Bolalar" belgisi nimani anglatadi?',
            'answers': [
                ('Maktab, bog\'cha yaqinligi', True),
                ('O\'yingohlarga kirish', False),
                ('Bolalar do\'koni', False),
                ('Park joylashuvi', False)
            ]
        },
        {
            'category': 'vehicle_tech',
            'question': 'Mashinaning farasi qachon yoqilishi shart?',
            'answers': [
                ('Qorong\'u vaqtda va yomon ob-havoda', True),
                ('Faqat tunda', False),
                ('Faqat qishda', False),
                ('Hech qachon majburiy emas', False)
            ]
        },
        {
            'category': 'vehicle_tech',
            'question': 'Avtomobilning shinalari qanday holatda bo\'lishi kerak?',
            'answers': [
                ('Yetarli chuqurlikdagi protektori bo\'lishi', True),
                ('Yangi bo\'lishi', False),
                ('Qimmat bo\'lishi', False),
                ('Katta o\'lchamli bo\'lishi', False)
            ]
        },
        {
            'category': 'emergency',
            'question': 'Yo\'lda baxtsiz hodisa bo\'lsa, voqea joyini qanday himoya qilish kerak?',
            'answers': [
                ('Ogohlantiruvchi uchburchak qo\'yish', True),
                ('Faqat signal yoqish', False),
                ('Hech narsa qilmaslik', False),
                ('Tez ketib qolish', False)
            ]
        },
        {
            'category': 'speed_limits',
            'question': 'Qanday sharoitda tezlikni kamaytirishga majbur?',
            'answers': [
                ('Yomg\'ir, tuman, qor paytida', True),
                ('Faqat tunda', False),
                ('Hech qachon', False),
                ('Faqat qishda', False)
            ]
        },
        {
            'category': 'traffic_rules',
            'question': 'Haydovchi ichkilikbozlik holatida transport vositasini boshqarishi mumkinmi?',
            'answers': [
                ('Yo\'q, qat\'iyan taqiqlanadi', True),
                ('Oz miqdorda mumkin', False),
                ('Faqat kechqurun', False),
                ('Qisqa masofada mumkin', False)
            ]
        },
        {
            'category': 'road_signs',
            'question': '"Aylanma harakat" belgisi qanday ko\'rinishda?',
            'answers': [
                ('Ko\'k fonda oq doiraviy o\'qlar', True),
                ('Qizil fonda oq o\'qlar', False),
                ('Sariq fonda qora o\'qlar', False),
                ('Yashil fonda oq o\'qlar', False)
            ]
        }
    ]
    
    print("10 ta qo'shimcha savol qo'shilmoqda...\n")
    
    added_count = 0
    for q_data in questions_data:
        # Savol yaratish
        question = Question.objects.create(
            category=categories[q_data['category']],
            question_text=q_data['question']
        )
        
        # Javoblar yaratish
        for answer_text, is_correct in q_data['answers']:
            Answer.objects.create(
                question=question,
                answer_text=answer_text,
                is_correct=is_correct
            )
        
        added_count += 1
        print(f"+ {added_count}. {q_data['question'][:50]}...")
    
    print(f"\nQo'shimcha {added_count} ta savol muvaffaqiyatli qo'shildi!")
    
    # Jami statistika
    total_questions = Question.objects.count()
    print(f"Jami savollar soni: {total_questions}")

if __name__ == '__main__':
    add_more_questions()