import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Question, Answer, Category

# Get first category
cat1 = Category.objects.first()
if not cat1:
    print("No categories found!")
    exit()

# Add more questions
questions_data = [
    {
        'text': 'Shahar ichida maksimal tezlik chegarasi nima?',
        'answers': [
            {'text': '60 km/soat', 'correct': True},
            {'text': '80 km/soat', 'correct': False},
            {'text': '50 km/soat', 'correct': False},
            {'text': '70 km/soat', 'correct': False},
        ]
    },
    {
        'text': 'Sariq svetofor signali nimani bildiradi?',
        'answers': [
            {'text': 'Tez harakat qiling', 'correct': False},
            {'text': 'Ehtiyot bilan harakat qiling', 'correct': True},
            {'text': 'To\'xtang', 'correct': False},
            {'text': 'Orqaga qaytish', 'correct': False},
        ]
    },
    {
        'text': 'Avtomobil to\'xtash masofasi nimaga bog\'liq?',
        'answers': [
            {'text': 'Faqat tezlikka', 'correct': False},
            {'text': 'Faqat yo\'l sharoitiga', 'correct': False},
            {'text': 'Tezlik va yo\'l sharoitiga', 'correct': True},
            {'text': 'Faqat ob-havoga', 'correct': False},
        ]
    },
    {
        'text': 'Avtomobil haydovchisi qachon fara yoqishi kerak?',
        'answers': [
            {'text': 'Faqat kechqurun', 'correct': False},
            {'text': 'Qorong\'uda va yomg\'irda', 'correct': True},
            {'text': 'Faqat qishda', 'correct': False},
            {'text': 'Har doim', 'correct': False},
        ]
    },
    {
        'text': 'Birinchi yordam kit avtomobildan qayerda bo\'lishi kerak?',
        'answers': [
            {'text': 'Bagajda', 'correct': False},
            {'text': 'Haydovchi o\'rnida', 'correct': True},
            {'text': 'Orqa o\'rindiqda', 'correct': False},
            {'text': 'Uyda', 'correct': False},
        ]
    }
]

for i, q_data in enumerate(questions_data, start=3):
    # Create question
    question = Question.objects.create(
        category=cat1,
        question_text=q_data['text']
    )
    
    # Create answers
    for a_data in q_data['answers']:
        Answer.objects.create(
            question=question,
            answer_text=a_data['text'],
            is_correct=a_data['correct']
        )
    
    print(f"Question {i} created: {q_data['text']}")

print(f"Successfully added {len(questions_data)} questions!")