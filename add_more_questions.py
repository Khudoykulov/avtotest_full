#!/usr/bin/env python
import os
import sys
import django

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, Question, Answer

def add_more_questions():
    """Add more questions to reach at least 20 questions"""
    
    # Traffic Rules - more questions
    traffic_rules = Category.objects.filter(name_uz='Yo\'lda harakat qoidalari').first()
    if traffic_rules:
        questions_data = [
            {
                'question_text': 'Yo\'lda harakat qilayotganda telefon ishlatish mumkinmi?',
                'answers': [
                    {'text': 'Yo\'q, qat\'iyan taqiqlangan', 'correct': True},
                    {'text': 'Ha, ehtiyotkorlik bilan', 'correct': False},
                    {'text': 'Faqat qisqa qo\'ng\'iroqlarda', 'correct': False},
                    {'text': 'Faqat svetaforlarda', 'correct': False}
                ],
                'explanation': 'Haydash paytida telefon ishlatish yo\'l-transport hodisalariga sabab bo\'lishi mumkin.'
            },
            {
                'question_text': 'Avtomobildan chiqayotganda avval nimani tekshirish kerak?',
                'answers': [
                    {'text': 'Orqa tarafdan keladigan transport vositalarini', 'correct': True},
                    {'text': 'Hech narsa', 'correct': False},
                    {'text': 'Faqat kalitlarni olish', 'correct': False},
                    {'text': 'Faqat eshikni yopish', 'correct': False}
                ],
                'explanation': 'Avtomobildan chiqishdan oldin xavfsizlik uchun atrofni tekshirish kerak.'
            },
            {
                'question_text': 'Kechasi haydashda qanday chiroqlardan foydalanish kerak?',
                'answers': [
                    {'text': 'Yaqin nur chiroqlari', 'correct': True},
                    {'text': 'Uzoq nur chiroqlari', 'correct': False},
                    {'text': 'Hech qanday chiroq', 'correct': False},
                    {'text': 'Faqat parking chiroqlari', 'correct': False}
                ],
                'explanation': 'Kechasi shahar ichida yaqin nur chiroqlaridan foydalanish kerak.'
            },
            {
                'question_text': 'Yo\'l belgisiga ko\'ra, qizil chiziq nimani anglatadi?',
                'answers': [
                    {'text': 'Taqiq yoki cheklash', 'correct': True},
                    {'text': 'Majburiylik', 'correct': False},
                    {'text': 'Ogohlantirish', 'correct': False},
                    {'text': 'Ma\'lumot berish', 'correct': False}
                ],
                'explanation': 'Qizil chiziq har doim taqiq yoki cheklashni bildiradi.'
            }
        ]
        create_questions_for_category(traffic_rules, questions_data)
    
    # Road Signs - more questions
    road_signs = Category.objects.filter(name_uz='Yo\'l belgilari').first()
    if road_signs:
        questions_data = [
            {
                'question_text': 'Sariq uchburchak belgisi nimani anglatadi?',
                'answers': [
                    {'text': 'Ogohlantiruvchi belgi', 'correct': True},
                    {'text': 'Taqiqlovchi belgi', 'correct': False},
                    {'text': 'Majburiy belgi', 'correct': False},
                    {'text': 'Ma\'lumot belgisi', 'correct': False}
                ],
                'explanation': 'Sariq rangli uchburchak belgilar ogohlantiruvchi belgilardir.'
            },
            {
                'question_text': 'STOP belgisi qaysi rangda bo\'ladi?',
                'answers': [
                    {'text': 'Qizil', 'correct': True},
                    {'text': 'Sariq', 'correct': False},
                    {'text': 'Ko\'k', 'correct': False},
                    {'text': 'Yashil', 'correct': False}
                ],
                'explanation': 'STOP belgisi doimo qizil rangda bo\'ladi va to\'liq to\'xtashni talab qiladi.'
            },
            {
                'question_text': 'Yo\'l ustunligi belgisi qanday shaklda bo\'ladi?',
                'answers': [
                    {'text': 'Romb shakli', 'correct': True},
                    {'text': 'Doira shakli', 'correct': False},
                    {'text': 'Uchburchak shakli', 'correct': False},
                    {'text': 'Kvadrat shakli', 'correct': False}
                ],
                'explanation': 'Asosiy yo\'l (ustunlik) belgisi romb shaklida bo\'ladi.'
            }
        ]
        create_questions_for_category(road_signs, questions_data)
    
    # Traffic Lights - more questions
    traffic_lights = Category.objects.filter(name_uz='Svetafor').first()
    if traffic_lights:
        questions_data = [
            {
                'question_text': 'Yashil svetafor yonsa darhol harakat qilish kerakmi?',
                'answers': [
                    {'text': 'Yo\'q, avval yo\'lni tekshirish kerak', 'correct': True},
                    {'text': 'Ha, darhol harakat qilish kerak', 'correct': False},
                    {'text': 'Bir necha soniya kutish kerak', 'correct': False},
                    {'text': 'Signal berish kerak', 'correct': False}
                ],
                'explanation': 'Yashil svetaforda ham kesishma xavfsizligini tekshirish kerak.'
            },
            {
                'question_text': 'Svetafor ishlamay qolsa nima qilish kerak?',
                'answers': [
                    {'text': 'Yo\'l belgilariga amal qilish', 'correct': True},
                    {'text': 'Ixtiyoriy harakat qilish', 'correct': False},
                    {'text': 'To\'xtab turish', 'correct': False},
                    {'text': 'Tez o\'tib ketish', 'correct': False}
                ],
                'explanation': 'Svetafor ishlamasa, yo\'l belgilariga va umumiy qoidalarga amal qilish kerak.'
            }
        ]
        create_questions_for_category(traffic_lights, questions_data)
    
    # Safe Driving - more questions
    safe_driving = Category.objects.filter(name_uz='Xavfsiz haydash').first()
    if safe_driving:
        questions_data = [
            {
                'question_text': 'Charchagan holatda haydash xavflimi?',
                'answers': [
                    {'text': 'Ha, juda xavfli', 'correct': True},
                    {'text': 'Yo\'q, oddiy holat', 'correct': False},
                    {'text': 'Qisman xavfli', 'correct': False},
                    {'text': 'Faqat tunda xavfli', 'correct': False}
                ],
                'explanation': 'Charchagan holatda diqqat pasayadi va hodisa xavfi oshadi.'
            },
            {
                'question_text': 'Avtomobilda bolalar uchun maxsus o\'rindiq kerakmi?',
                'answers': [
                    {'text': 'Ha, 12 yoshgacha majburiy', 'correct': True},
                    {'text': 'Yo\'q, shart emas', 'correct': False},
                    {'text': 'Faqat uzoq safarlarda', 'correct': False},
                    {'text': 'Faqat katta yo\'llarda', 'correct': False}
                ],
                'explanation': '12 yoshgacha bolalar uchun maxsus avtokursi majburiy.'
            },
            {
                'question_text': 'Qishda avtomobil shinalari qanday bo\'lishi kerak?',
                'answers': [
                    {'text': 'Qishki shinalar yoki zanjirlar', 'correct': True},
                    {'text': 'Oddiy shinalar yetarli', 'correct': False},
                    {'text': 'Faqat yangi shinalar', 'correct': False},
                    {'text': 'Hech qanday o\'zgarish kerak emas', 'correct': False}
                ],
                'explanation': 'Qishda yo\'l sharoitlari uchun maxsus qishki shinalar kerak.'
            }
        ]
        create_questions_for_category(safe_driving, questions_data)
    
    # Emergency Situations - more questions
    emergency = Category.objects.filter(name_uz='Favqulodda vaziyatlar').first()
    if emergency:
        questions_data = [
            {
                'question_text': 'Yo\'l-transport hodisasida birinchi navbatda nima qilish kerak?',
                'answers': [
                    {'text': 'Jarohatlanganlarga yordam berish', 'correct': True},
                    {'text': 'Politsiyaga qo\'ng\'iroq qilish', 'correct': False},
                    {'text': 'Hodisa joyini tozalash', 'correct': False},
                    {'text': 'Suratga olish', 'correct': False}
                ],
                'explanation': 'Birinchi navbatda inson hayoti muhim - jarohatlanganlarga yordam berish kerak.'
            },
            {
                'question_text': 'Yong\'in bo\'lganda qaysi raqamga qo\'ng\'iroq qilish kerak?',
                'answers': [
                    {'text': '101', 'correct': True},
                    {'text': '102', 'correct': False},
                    {'text': '103', 'correct': False},
                    {'text': '104', 'correct': False}
                ],
                'explanation': 'O\'t o\'chirish xizmati - 101 raqam.'
            },
            {
                'question_text': 'Avtomobil fary ishlamay qolsa qanday harakat qilish kerak?',
                'answers': [
                    {'text': 'Favqulodda signalni yoqish va ehtiyotkorlik bilan harakat qilish', 'correct': True},
                    {'text': 'Oddiy holatdek davom etish', 'correct': False},
                    {'text': 'Tezlikni oshirish', 'correct': False},
                    {'text': 'Yo\'l chetida to\'xtash', 'correct': False}
                ],
                'explanation': 'Chiroqsiz haydash xavfli, ehtiyot choralarini ko\'rish kerak.'
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

def main():
    print("Qo'shimcha savollar qo'shilmoqda...")
    add_more_questions()
    
    print("\nStatistika:")
    print(f"Savollar: {Question.objects.count()}")
    print(f"Javoblar: {Answer.objects.count()}")
    
    if Question.objects.count() >= 20:
        print("Endi test biletlarini yaratish mumkin!")

if __name__ == '__main__':
    main()