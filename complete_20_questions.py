import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Question, Answer, Category

# Get first category
cat1 = Category.objects.first()
current_count = Question.objects.filter(category=cat1).count()

print(f"Current questions: {current_count}")

# Add questions to make it 20 total
remaining = 20 - current_count
if remaining <= 0:
    print("Already have 20 or more questions!")
    exit()

additional_questions = [
    {
        'text': 'Yo\'l bo\'ylab maksimal tezlik necha km/soat?',
        'answers': [
            {'text': '90 km/soat', 'correct': True},
            {'text': '120 km/soat', 'correct': False},
            {'text': '60 km/soat', 'correct': False},
        ]
    },
    {
        'text': 'Qanday holda overtaking (quvish) taqiqlanadi?',
        'answers': [
            {'text': 'Ko\'priklarда', 'correct': True},
            {'text': 'Tekis yo\'lda', 'correct': False},
            {'text': 'Shahar tashqarisida', 'correct': False},
            {'text': 'Kunduzi', 'correct': False},
        ]
    },
    {
        'text': 'Avtomobil to\'xtash masofasiga ta\'sir qiluvchi omillar?',
        'answers': [
            {'text': 'Tezlik va ob-havo', 'correct': True},
            {'text': 'Faqat tezlik', 'correct': False},
        ]
    },
    {
        'text': 'Birinchi yordam kitining tarkibi?',
        'answers': [
            {'text': 'Bint, yod, aspirin', 'correct': True},
            {'text': 'Faqat bint', 'correct': False},
            {'text': 'Faqat dori', 'correct': False},
        ]
    },
    {
        'text': 'Yo\'l belgisi "Stop" nimani bildiradi?',
        'answers': [
            {'text': 'To\'liq to\'xtash', 'correct': True},
            {'text': 'Sekin harakat', 'correct': False},
            {'text': 'Ehtiyot', 'correct': False},
        ]
    },
    {
        'text': 'Kechasi fara qachon yoqiladi?',
        'answers': [
            {'text': 'Qorong\'uda', 'correct': True},
            {'text': 'Har doim', 'correct': False},
        ]
    },
    {
        'text': 'Avtomobil texnik ko\'rigidan o\'tish muddati?',
        'answers': [
            {'text': '1 yilda', 'correct': True},
            {'text': '2 yilda', 'correct': False},
            {'text': '6 oyda', 'correct': False},
        ]
    },
    {
        'text': 'Yo\'l harakati qoidalarini buzgani uchun jarimalar?',
        'answers': [
            {'text': 'Pul jarima', 'correct': True},
            {'text': 'Ogohlantirish', 'correct': False},
            {'text': 'Hech narsa', 'correct': False},
        ]
    },
    {
        'text': 'Avtomobil yonilg\'isi qanday turda bo\'ladi?',
        'answers': [
            {'text': 'Benzin, dizel', 'correct': True},
            {'text': 'Faqat benzin', 'correct': False},
            {'text': 'Suv', 'correct': False},
        ]
    },
    {
        'text': 'Himoya kamarini taqish majburiyimi?',
        'answers': [
            {'text': 'Ha, majburiy', 'correct': True},
            {'text': 'Yo\'q, ixtiyoriy', 'correct': False},
        ]
    },
    {
        'text': 'Piyodalar yo\'lni qayerdan kesib o\'tishlari kerak?',
        'answers': [
            {'text': 'Piyoda o\'tish joyidan', 'correct': True},
            {'text': 'Istalgan joydan', 'correct': False},
            {'text': 'Yo\'l o\'rtasidan', 'correct': False},
        ]
    },
    {
        'text': 'Avtobus bekatida to\'xtash mumkinmi?',
        'answers': [
            {'text': 'Yo\'q, taqiqlangan', 'correct': True},
            {'text': 'Ha, mumkin', 'correct': False},
        ]
    },
    {
        'text': 'Qish paytida qanday ehtiyot choralari ko\'riladi?',
        'answers': [
            {'text': 'Qish shinalari', 'correct': True},
            {'text': 'Oddiy shinalar', 'correct': False},
            {'text': 'Hech narsa', 'correct': False},
        ]
    }
]

for i, q_data in enumerate(additional_questions[:remaining]):
    question = Question.objects.create(
        category=cat1,
        question_text=q_data['text']
    )
    
    for a_data in q_data['answers']:
        Answer.objects.create(
            question=question,
            answer_text=a_data['text'],
            is_correct=a_data['correct']
        )
    
    print(f"Added question {current_count + i + 1}: {q_data['text']}")

final_count = Question.objects.filter(category=cat1).count()
print(f"Final question count: {final_count}")