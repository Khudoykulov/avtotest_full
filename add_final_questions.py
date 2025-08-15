import os
import sys
import django

# Django environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, Question, Answer

def add_final_questions():
    """Yo'l harakati qoidalari kategoriyasiga 7 ta qo'shimcha savol qo'shish"""
    
    # Yo'l harakati qoidalari kategoriyasi
    traffic_rules_cat = Category.objects.get(name_uz="Yo'l harakati qoidalari")
    
    # 7 ta qo'shimcha savol
    questions_data = [
        {
            'question': 'Piyoda o\'tkazmasida piyoda yo\'q bo\'lsa ham to\'xtash shartmi?',
            'answers': [
                ('Ha, piyoda paydo bo\'lishi mumkin', True),
                ('Yo\'q, piyoda bo\'lmasayu o\'tish mumkin', False),
                ('Faqat maktab yaqinida to\'xtash', False),
                ('Faqat signallarga qarash', False)
            ]
        },
        {
            'question': 'Haydovchi nima uchun kamar taqishi shart?',
            'answers': [
                ('Xavfsizlik va qonuniy talablar uchun', True),
                ('Faqat uzoq yo\'lda', False),
                ('Faqat tez haydashda', False),
                ('Majburiy emas', False)
            ]
        },
        {
            'question': 'Bolalarni transport vositasida qanday tashish kerak?',
            'answers': [
                ('12 yoshgacha maxsus o\'rindiq yoki kamardan foydalanish', True),
                ('Oddiy kamar bilan', False),
                ('Quchoqda ushlab turish', False),
                ('Hech qanday himoya kerak emas', False)
            ]
        },
        {
            'question': 'Yo\'lda velosipedchi bilan qanday munosabatda bo\'lish kerak?',
            'answers': [
                ('Ehtiyotkorlik, xavfsiz masofa saqlash', True),
                ('Tez o\'tib ketish', False),
                ('Signal berib quvish', False),
                ('E\'tibor bermaslik', False)
            ]
        },
        {
            'question': 'Mast holatda transport boshqarish uchun qanday jazo bor?',
            'answers': [
                ('Katta miqdorda jarime va huquqni olib qo\'yish', True),
                ('Faqat ogohlantirilish', False),
                ('Kichik jarime', False),
                ('Hech qanday jazo yo\'q', False)
            ]
        },
        {
            'question': 'Transport vositasida nechta kishi o\'tirishi mumkin?',
            'answers': [
                ('Texnik passport bo\'yicha belgilangan son', True),
                ('Nechtasini sig\'dirse', False),
                ('Maksimal 8 kishi', False),
                ('Cheklov yo\'q', False)
            ]
        },
        {
            'question': 'Haydovchi boshqa yo\'l ishtirokchilari bilan nizoda bo\'lsa nima qilishi kerak?',
            'answers': [
                ('Xotirjamlikni saqlash, nizoni kuchaytirmaslik', True),
                ('O\'z huquqini himoya qilish', False),
                ('Qasos olish', False),
                ('Politsiyaga shikoyat qilish', False)
            ]
        }
    ]
    
    print("Yo'l harakati qoidalari kategoriyasiga 7 ta qo'shimcha savol qo'shilmoqda...\n")
    
    added_count = 0
    for q_data in questions_data:
        # Savol yaratish
        question = Question.objects.create(
            category=traffic_rules_cat,
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
    
    print(f"\n{added_count} ta qo'shimcha savol muvaffaqiyatli qo'shildi!")
    
    # Final statistika
    print("\nFINAL STATISTIKA:")
    print("=" * 50)
    
    categories = Category.objects.exclude(name__in=['test'])
    total_questions = 0
    
    for category in categories:
        count = Question.objects.filter(category=category).count()
        total_questions += count
        status = "OK" if count >= 20 else "KAM"
        print(f"{status} {category.name_uz}: {count} ta savol")
    
    print("=" * 50)
    print(f"JAMI: {total_questions} ta savol")
    print("=" * 50)

if __name__ == '__main__':
    add_final_questions()