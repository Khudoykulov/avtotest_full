#!/usr/bin/env python
import os
import sys
import django

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, Question, Answer, TestTicket, EducationContent

def create_categories():
    """Create quiz categories"""
    categories_data = [
        {
            'name': 'Traffic Rules',
            'name_uz': 'Yo\'lda harakat qoidalari',
            'description': 'Avtomobil haydovchiligi uchun asosiy yo\'lda harakat qoidalari'
        },
        {
            'name': 'Road Signs',
            'name_uz': 'Yo\'l belgilari',
            'description': 'Yo\'l belgilarini tanish va tushunish'
        },
        {
            'name': 'Traffic Lights',
            'name_uz': 'Svetafor',
            'description': 'Svetafor signallari va ularning ma\'nosi'
        },
        {
            'name': 'Safe Driving',
            'name_uz': 'Xavfsiz haydash',
            'description': 'Xavfsiz haydash texnikasi va qoidalari'
        },
        {
            'name': 'Emergency Situations',
            'name_uz': 'Favqulodda vaziyatlar',
            'description': 'Yo\'lda yuzaga keladigan favqulodda vaziyatlarda harakat qilish'
        }
    ]
    
    created_categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'name_uz': cat_data['name_uz'],
                'description': cat_data['description']
            }
        )
        created_categories.append(category)
        if created:
            print(f"Kategoriya yaratildi: {category.name_uz}")
        else:
            print(f"Kategoriya mavjud: {category.name_uz}")
    
    return created_categories

def create_questions_and_answers():
    """Create questions with multiple choice answers"""
    categories = Category.objects.all()
    
    # Traffic Rules questions
    traffic_rules = categories.filter(name_uz='Yo\'lda harakat qoidalari').first()
    if traffic_rules:
        questions_data = [
            {
                'question_text': 'Avtomobil haydovchisi yo\'lda qanday tezlikda harakat qilishi mumkin?',
                'answers': [
                    {'text': 'Shahar ichida 60 km/soat', 'correct': True},
                    {'text': 'Shahar ichida 80 km/soat', 'correct': False},
                    {'text': 'Shahar ichida 40 km/soat', 'correct': False},
                    {'text': 'Cheklovsiz', 'correct': False}
                ],
                'explanation': 'Shahar ichida maksimal tezlik 60 km/soat.'
            },
            {
                'question_text': 'Piyodalar yo\'lini kesib o\'tishda nima qilish kerak?',
                'answers': [
                    {'text': 'Tezlikni pasaytirish va ehtiyotkorlik bilan o\'tish', 'correct': True},
                    {'text': 'Signal bermasdan o\'tish', 'correct': False},
                    {'text': 'Tezlikni oshirish', 'correct': False},
                    {'text': 'To\'xtatish shart emas', 'correct': False}
                ],
                'explanation': 'Piyodalar yo\'lida har doim ehtiyotkor bo\'lish va tezlikni kamaytirish kerak.'
            }
        ]
        create_questions_for_category(traffic_rules, questions_data)
    
    # Road Signs questions
    road_signs = categories.filter(name_uz='Yo\'l belgilari').first()
    if road_signs:
        questions_data = [
            {
                'question_text': 'Qizil rang doira shaklidagi yo\'l belgisi nimani anglatadi?',
                'answers': [
                    {'text': 'Taqiq belgisi', 'correct': True},
                    {'text': 'Ogohlantiruvchi belgisi', 'correct': False},
                    {'text': 'Majburiy belgisi', 'correct': False},
                    {'text': 'Ma\'lumot belgisi', 'correct': False}
                ],
                'explanation': 'Qizil rang doira shaklidagi belgilar taqiq belgilardir.'
            },
            {
                'question_text': 'Ko\'k rang doira shaklidagi yo\'l belgisi nimani anglatadi?',
                'answers': [
                    {'text': 'Majburiy belgisi', 'correct': True},
                    {'text': 'Taqiq belgisi', 'correct': False},
                    {'text': 'Ogohlantiruvchi belgisi', 'correct': False},
                    {'text': 'Ma\'lumot belgisi', 'correct': False}
                ],
                'explanation': 'Ko\'k rang doira shaklidagi belgilar majburiy belgilardir.'
            }
        ]
        create_questions_for_category(road_signs, questions_data)
    
    # Traffic Lights questions
    traffic_lights = categories.filter(name_uz='Svetafor').first()
    if traffic_lights:
        questions_data = [
            {
                'question_text': 'Qizil svetafor yonib tursa nima qilish kerak?',
                'answers': [
                    {'text': 'To\'liq to\'xtash', 'correct': True},
                    {'text': 'Sekin harakat qilish', 'correct': False},
                    {'text': 'Ehtiyotkorlik bilan o\'tish', 'correct': False},
                    {'text': 'Signal berish', 'correct': False}
                ],
                'explanation': 'Qizil svetafor signal - to\'liq to\'xtash.'
            },
            {
                'question_text': 'Sariq svetafor yonib tursa nima qilish kerak?',
                'answers': [
                    {'text': 'Tayyorgarlik ko\'rish va to\'xtashga tayyor bo\'lish', 'correct': True},
                    {'text': 'Tezlikni oshirish', 'correct': False},
                    {'text': 'Darhol to\'xtash', 'correct': False},
                    {'text': 'Davom etish', 'correct': False}
                ],
                'explanation': 'Sariq svetafor - tayyorgarlik signali.'
            }
        ]
        create_questions_for_category(traffic_lights, questions_data)
    
    # Safe Driving questions
    safe_driving = categories.filter(name_uz='Xavfsiz haydash').first()
    if safe_driving:
        questions_data = [
            {
                'question_text': 'Yomg\'irli ob-havoda haydashda nima qilish kerak?',
                'answers': [
                    {'text': 'Tezlikni kamaytirish va masofani oshirish', 'correct': True},
                    {'text': 'Tezlikni oshirish', 'correct': False},
                    {'text': 'Odatdagidek haydash', 'correct': False},
                    {'text': 'Chiroqlarni o\'chirish', 'correct': False}
                ],
                'explanation': 'Yomg\'irda yo\'l sirpanchiq bo\'ladi, shuning uchun ehtiyotkorlik kerak.'
            },
            {
                'question_text': 'Xavfsizlik kamarini qachon taqish kerak?',
                'answers': [
                    {'text': 'Har doim, yo\'lga chiqishdan oldin', 'correct': True},
                    {'text': 'Faqat uzoq safarlarda', 'correct': False},
                    {'text': 'Faqat tezkor yo\'llarda', 'correct': False},
                    {'text': 'Shart emas', 'correct': False}
                ],
                'explanation': 'Xavfsizlik kamari har doim taqilishi shart.'
            }
        ]
        create_questions_for_category(safe_driving, questions_data)
    
    # Emergency Situations questions
    emergency = categories.filter(name_uz='Favqulodda vaziyatlar').first()
    if emergency:
        questions_data = [
            {
                'question_text': 'Avtomobil buzilgan bo\'lsa yo\'l chetida nima qilish kerak?',
                'answers': [
                    {'text': 'Favqulodda to\'xtash belgisini qo\'yish', 'correct': True},
                    {'text': 'Hech narsa qilmaslik', 'correct': False},
                    {'text': 'Yo\'l o\'rtasida qoldirish', 'correct': False},
                    {'text': 'Chiroqlarni o\'chirish', 'correct': False}
                ],
                'explanation': 'Favqulodda to\'xtash belgisi boshqa haydovchilarni ogohlantiradi.'
            }
        ]
        create_questions_for_category(emergency, questions_data)

def create_questions_for_category(category, questions_data):
    """Helper function to create questions for a specific category"""
    for q_data in questions_data:
        question = Question.objects.create(
            category=category,
            question_text=q_data['question_text'],
            explanation=q_data.get('explanation', '')
        )
        
        for answer_data in q_data['answers']:
            Answer.objects.create(
                question=question,
                answer_text=answer_data['text'],
                is_correct=answer_data['correct']
            )
        
        print(f"Savol yaratildi: {question.question_text[:50]}...")

def create_test_tickets():
    """Create test tickets with 20 questions each"""
    questions = Question.objects.all()
    if questions.count() < 20:
        print("Test biletlarini yaratish uchun kamida 20 ta savol kerak")
        return
    
    # Create 5 test tickets
    for i in range(1, 6):
        ticket, created = TestTicket.objects.get_or_create(
            ticket_number=i,
            defaults={'name': f'Test bileti {i}'}
        )
        
        if created:
            # Add 20 random questions to each ticket
            import random
            ticket_questions = random.sample(list(questions), min(20, questions.count()))
            ticket.questions.set(ticket_questions)
            print(f"Test bileti {i} yaratildi - {len(ticket_questions)} ta savol")
        else:
            print(f"Test bileti {i} mavjud")

def create_education_content():
    """Create educational content for each category"""
    categories = Category.objects.all()
    
    for category in categories:
        education_data = []
        
        if category.name_uz == 'Yo\'lda harakat qoidalari':
            education_data = [
                {
                    'title': 'Asosiy yo\'l qoidalari',
                    'content_type': 'text',
                    'text_content': '''
Avtomobil haydovchilari quyidagi asosiy qoidalarga amal qilishi shart:

1. Tezlik cheklovlariga rioya qilish:
   - Shahar ichida: 60 km/soat
   - Shahar tashqarisida: 90 km/soat
   - Magistral yo\'llarda: 110 km/soat

2. Xavfsizlik qoidalari:
   - Xavfsizlik kamarini taqish
   - Chiroqlardan to\'g\'ri foydalanish
   - Boshqa transport vositalariga hurmat qilish

3. Piyodalar huquqlari:
   - Piyoda yo\'laklarida piyodalarga yo\'l berish
   - Bolalar va nogironlar atrofida alohida ehtiyotkorlik
                    ''',
                    'order': 1
                },
                {
                    'title': 'Yo\'l harakati madaniyati',
                    'content_type': 'text',
                    'text_content': '''
Yo\'l harakati madaniyati - bu barcha yo\'l ishtirokchilarining o\'zaro hurmat va qoidalarga rioya qilishidir.

Asosiy tamoyillar:
- Sabr-toqat va xotirjamlik
- Boshqalarga yo\'l berish
- Qoidabuzarlikka yo\'l qo\'ymaslik
- Atrof-muhitni muhofaza qilish
                    ''',
                    'order': 2
                }
            ]
        
        elif category.name_uz == 'Yo\'l belgilari':
            education_data = [
                {
                    'title': 'Yo\'l belgilarining turlari',
                    'content_type': 'text',
                    'text_content': '''
Yo\'l belgilari quyidagi turlarga bo\'linadi:

1. Ogohlatiruvchi belgilar (uchburchak, qizil ramka)
   - Yo\'ldagi xavflar haqida ogohlantiradi
   - Avtoban yoki kesishmalarga yaqinlashganda o\'rnatiladi

2. Taqiqlovchi belgilar (doira, qizil rang)
   - Ma'lum harakatlarni taqiqlaydi
   - Majburiy bajarilishi kerak

3. Majburiy belgilar (doira, ko\'k rang)
   - Bajarilishi shart bo\'lgan harakatlarni ko\'rsatadi

4. Ma'lumot belgilari
   - Yo\'l haqida foydali ma'lumotlar beradi
                    ''',
                    'order': 1
                }
            ]
        
        elif category.name_uz == 'Svetafor':
            education_data = [
                {
                    'title': 'Svetafor signallari',
                    'content_type': 'text',
                    'text_content': '''
Svetafor signallari va ularning ma'nosi:

🔴 QIZIL SIGNAL:
- To'liq to'xtash majburiy
- Kesishmaga kirishga ruxsat yo'q
- Piyodalar ham to'xtashi kerak

🟡 SARIQ SIGNAL:
- Tayyorgarlik signali
- To'xtashga tayyor bo'lish
- Agar xavfsiz to'xtab bo'lmasa, ehtiyotkorlik bilan o'tish mumkin

🟢 YASHIL SIGNAL:
- Harakat qilishga ruxsat
- Lekin kesishmaga kirishdan oldin yo'lni tekshirish kerak
- Piyodalar ham harakat qilishi mumkin

⚠️ MILTILLOVCHI SARIQ:
- Ehtiyotkorlik bilan o'tish
- Svetafor ishlamayotganini bildiradi
                    ''',
                    'order': 1
                }
            ]
        
        elif category.name_uz == 'Xavfsiz haydash':
            education_data = [
                {
                    'title': 'Xavfsiz haydash asoslari',
                    'content_type': 'text',
                    'text_content': '''
Xavfsiz haydash uchun asosiy qoidalar:

1. OLDINDAN TAYYORGARLIK:
   - Avtomobilni tekshirish (yoqilg'i, moy, shinalar)
   - O'rindiq va oynalarni sozlash
   - Xavfsizlik kamarini taqish

2. DIQQAT VA KONCENTRATSIYA:
   - Telefon ishlatmaslik
   - Charchagan holatda haydamaslik
   - Yo'lga diqqatni qaratish

3. MUDOFAALI HAYDASH:
   - Boshqalarning xatolarini nazarda tutish
   - Xavfsiz masofa saqlash
   - Ob-havo sharoitiga mos tezlik

4. TEXNIK QOIDALAR:
   - Indikatorlardan foydalanish
   - Ko'zgularni tekshirish
   - Tormozlash texnikasi
                    ''',
                    'order': 1
                }
            ]
        
        elif category.name_uz == 'Favqulodda vaziyatlar':
            education_data = [
                {
                    'title': 'Favqulodda vaziyatlarda harakat qilish',
                    'content_type': 'text',
                    'text_content': '''
Yo'lda yuzaga kelishi mumkin bo'lgan favqulodda vaziyatlar:

1. AVTOMOBIL BUZILGANDA:
   - Xavfsiz joyga to'xtash
   - Favqulodda signal yoqish
   - Ogohlantirish uchburchagini qo'yish
   - Yordam chaqirish

2. AVTOHALOKATDA:
   - Xotirjamlikni saqlash
   - Jarohatlanganlarga yordam berish
   - Yo'l politsiyasini chaqirish
   - Hodisa joyini saqlab qolish

3. YOMON OB-HAVODA:
   - Tezlikni sezilarli kamaytirish
   - Chiroqlarni yoqish
   - Ko'proq masofa saqlash
   - Ehtiyotkorlik bilan harakat qilish

4. FAVQULODDA TO'XTASH:
   - Noshud to'xtash signalini yoqish
   - Ogohlantirish belgisini qo'yish
   - Xavfsiz masofaga o'tish
                    ''',
                    'order': 1
                }
            ]
        
        for edu_data in education_data:
            content, created = EducationContent.objects.get_or_create(
                category=category,
                title=edu_data['title'],
                defaults={
                    'content_type': edu_data['content_type'],
                    'text_content': edu_data['text_content'],
                    'order': edu_data['order']
                }
            )
            if created:
                print(f"Ta'lim materiali yaratildi: {content.title}")
            else:
                print(f"Ta'lim materiali mavjud: {content.title}")

def main():
    print("Ma'lumotlar bazasini to'ldirish boshlandi...")
    
    # Create categories
    print("\n1. Kategoriyalar yaratilmoqda...")
    create_categories()
    
    # Create questions and answers
    print("\n2. Savollar va javoblar yaratilmoqda...")
    create_questions_and_answers()
    
    # Create test tickets
    print("\n3. Test biletlari yaratilmoqda...")
    create_test_tickets()
    
    # Create education content
    print("\n4. Ta'lim materiallari yaratilmoqda...")
    create_education_content()
    
    print("\nBarcha ma'lumotlar muvaffaqiyatli qo'shildi!")
    
    # Show statistics
    print(f"\nStatistika:")
    print(f"Kategoriyalar: {Category.objects.count()}")
    print(f"Savollar: {Question.objects.count()}")
    print(f"Javoblar: {Answer.objects.count()}")
    print(f"Test biletlari: {TestTicket.objects.count()}")
    print(f"Ta'lim materiallari: {EducationContent.objects.count()}")

if __name__ == '__main__':
    main()