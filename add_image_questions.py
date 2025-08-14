import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Question, Answer, Category

# Get categories
categories = Category.objects.all()
if not categories.exists():
    print("No categories found!")
    exit()

cat1 = categories[0]  # First category

# Add questions with different answer counts
questions_data = [
    {
        'text': 'Bu belgi nimani bildiradi?',
        'has_image': True,
        'answers': [
            {'text': 'Tezlikni cheklash', 'correct': True},
            {'text': 'Ruxsat etilgan tezlik', 'correct': False},
        ]
    },
    {
        'text': 'Quyidagi vaziyatda qaysi harakatni bajarish kerak?',
        'has_image': True,
        'answers': [
            {'text': 'Chapga burilish', 'correct': False},
            {'text': 'To\'g\'ri harakat qilish', 'correct': True},
            {'text': 'O\'ngga burilish', 'correct': False},
            {'text': 'To\'xtab turish', 'correct': False},
            {'text': 'Orqaga qaytish', 'correct': False},
        ]
    },
    {
        'text': 'Ushbu yo\'l belgisi qanday ma\'noni bildiradi?',
        'has_image': True,
        'answers': [
            {'text': 'Yo\'l tuzilmoqda', 'correct': False},
            {'text': 'Xavfli yo\'l', 'correct': True},
            {'text': 'Yopiq yo\'l', 'correct': False},
        ]
    },
    {
        'text': 'Birinchi yordam ko\'rsatishda eng muhim qadamlar qaysilar?',
        'has_image': False,
        'answers': [
            {'text': 'Tez-tez suvni berish', 'correct': False},
            {'text': 'Nafas yo\'lini ochish', 'correct': True},
            {'text': 'Oyoqlarni ko\'tarish', 'correct': False},
            {'text': 'Dori berish', 'correct': False},
        ]
    }
]

for i, q_data in enumerate(questions_data):
    # Create question
    question = Question.objects.create(
        category=cat1,
        question_text=q_data['text']
        # Note: We'll add image field separately via admin
    )
    
    # Create answers
    for a_data in q_data['answers']:
        Answer.objects.create(
            question=question,
            answer_text=a_data['text'],
            is_correct=a_data['correct']
        )
    
    print(f"Question created with {len(q_data['answers'])} answers: {q_data['text']}")

print(f"Successfully added {len(questions_data)} questions with varying answer counts!")