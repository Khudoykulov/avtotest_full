"""
Script to populate the database with sample quiz data
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, Question, Answer, TestTicket

def create_categories():
    """Create quiz categories"""
    categories_data = [
        {"name": "Traffic Rules", "name_uz": "Yo'l qoidalari", "description": "Yo'l harakati qoidalari", "icon": "🚦"},
        {"name": "Road Signs", "name_uz": "Yo'l belgilari", "description": "Yo'l belgilari va ularning ma'nosi", "icon": "🛑"},
        {"name": "First Aid", "name_uz": "Birinchi yordam", "description": "Birinchi tibbiy yordam", "icon": "🏥"},
        {"name": "Technical Inspection", "name_uz": "Texnik ko'rik", "description": "Transport vositasining texnik holati", "icon": "🔧"},
        {"name": "Environmental Protection", "name_uz": "Atrof muhit himoyasi", "description": "Ekologiya va muhit himoyasi", "icon": "🌱"},
        {"name": "Penalties", "name_uz": "Jarimalar va jazolar", "description": "Qonun buzganlik uchun jarimalar", "icon": "⚖️"},
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data["name"],
            defaults=cat_data
        )
        if created:
            print(f"Created category: {category.name_uz}")

def create_sample_questions():
    """Create sample questions for each category"""
    
    # Get categories
    traffic_rules = Category.objects.get(name="Traffic Rules")
    road_signs = Category.objects.get(name="Road Signs")
    first_aid = Category.objects.get(name="First Aid")
    
    # Sample questions for Traffic Rules
    traffic_questions = [
        {
            "question_text": "Agar piyodalar o'tish joyida tirbandlik vujudga kelib, haydovchini piyodalar o'tish joyida to'xtagaa majbur qilsa, haydovchi majbur:",
            "answers": [
                {"text": "Piyodalar o'tish joyi oldidan 5 metr berida to'xtash", "correct": False},
                {"text": "Piyodalar o'tish joyi oldidan 15 metr berida to'xtash", "correct": True},
                {"text": "Oldinda turgan transport vositasidan zarar masofaa saqlangan holda piyodalar o'tish joyida to'xtash", "correct": False},
                {"text": "To'xtash va piyodalar o'tish joyiga o'tmaslikka, chunki bu piyodalarning xarakati uchun to'sqinlik qiladi", "correct": False}
            ]
        },
        {
            "question_text": "Shahar ichida transport vositasining maksimal tezligi qancha?",
            "answers": [
                {"text": "40 km/soat", "correct": False},
                {"text": "50 km/soat", "correct": True},
                {"text": "60 km/soat", "correct": False},
                {"text": "70 km/soat", "correct": False}
            ]
        },
        {
            "question_text": "Qizil svetofor signali nimani bildiradi?",
            "answers": [
                {"text": "Ehtiyotkorlik bilan harakat qilish", "correct": False},
                {"text": "To'xtash va kutish", "correct": True},
                {"text": "Tezlikni kamaytirish", "correct": False},
                {"text": "Chap tomonga burilish mumkin", "correct": False}
            ]
        }
    ]
    
    # Sample questions for Road Signs
    road_sign_questions = [
        {
            "question_text": "Quyidagi belgi nimani bildiradi? (Stop belgisi)",
            "answers": [
                {"text": "Ehtiyotkorlik bilan harakat qilish", "correct": False},
                {"text": "To'liq to'xtash majburiy", "correct": True},
                {"text": "Tezlikni kamaytirish", "correct": False},
                {"text": "Yo'l berish", "correct": False}
            ]
        },
        {
            "question_text": "Oq rangdagi yo'l chizig'i nimani bildiradi?",
            "answers": [
                {"text": "Yo'lni kesib o'tish mumkin", "correct": True},
                {"text": "Yo'lni kesib o'tish taqiqlangan", "correct": False},
                {"text": "Ehtiyotkorlik talab qilinadi", "correct": False},
                {"text": "Faqat chap tomonga burilish", "correct": False}
            ]
        }
    ]
    
    # Sample questions for First Aid
    first_aid_questions = [
        {
            "question_text": "Birinchi tibbiy yordam ko'rsatishda eng muhim narsa nima?",
            "answers": [
                {"text": "Tezda shifoxonaga olib borish", "correct": False},
                {"text": "Xavfsizlikni ta'minlash", "correct": True},
                {"text": "Dori berish", "correct": False},
                {"text": "Suv berish", "correct": False}
            ]
        }
    ]
    
    # Create questions
    all_questions = [
        (traffic_rules, traffic_questions),
        (road_signs, road_sign_questions),
        (first_aid, first_aid_questions)
    ]
    
    for category, questions in all_questions:
        for q_data in questions:
            question = Question.objects.create(
                category=category,
                question_text=q_data["question_text"],
                explanation="Bu savol uchun tushuntirish..."
            )
            
            for answer_data in q_data["answers"]:
                Answer.objects.create(
                    question=question,
                    answer_text=answer_data["text"],
                    is_correct=answer_data["correct"]
                )
            
            print(f"Created question: {question.question_text[:50]}...")

def create_test_tickets():
    """Create test tickets with random questions"""
    from random import sample
    
    all_questions = list(Question.objects.all())
    
    for i in range(1, 11):  # Create 10 tickets
        ticket = TestTicket.objects.create(
            ticket_number=i,
            name=f"Bilet {i}"
        )
        
        # Add 20 random questions to each ticket
        if len(all_questions) >= 20:
            selected_questions = sample(all_questions, 20)
            ticket.questions.set(selected_questions)
        else:
            # If we don't have enough questions, use all available
            ticket.questions.set(all_questions)
        
        print(f"Created ticket: {ticket.name}")

def main():
    """Main function to populate all data"""
    print("Starting to populate quiz data...")
    
    create_categories()
    create_sample_questions()
    create_test_tickets()
    
    print("Quiz data population completed!")
    print(f"Categories: {Category.objects.count()}")
    print(f"Questions: {Question.objects.count()}")
    print(f"Answers: {Answer.objects.count()}")
    print(f"Test Tickets: {TestTicket.objects.count()}")

if __name__ == "__main__":
    main()
