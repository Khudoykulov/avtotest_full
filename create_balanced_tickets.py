#!/usr/bin/env python
import os
import sys
import django

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, Question, Answer, TestTicket
import random

def create_balanced_test_tickets():
    """Create balanced test tickets with questions from all categories"""
    
    # Delete existing tickets
    TestTicket.objects.all().delete()
    print("Eski test biletlari o'chirildi.")
    
    categories = Category.objects.all()
    
    if categories.count() != 5:
        print("5 ta kategoriya bo'lishi kerak")
        return
    
    # Check if each category has enough questions
    for category in categories:
        question_count = Question.objects.filter(category=category).count()
        if question_count < 20:
            print(f"Kategoriya '{category.name_uz}' da faqat {question_count} ta savol bor, 20 ta kerak")
            return
        print(f"+ {category.name_uz}: {question_count} ta savol")
    
    # Create 20 test tickets
    for i in range(1, 21):
        ticket = TestTicket.objects.create(
            ticket_number=i,
            name=f'Test bileti {i}'
        )
        
        ticket_questions = []
        
        # From each category, take 4 random questions (5 categories * 4 = 20 questions)
        for category in categories:
            category_questions = list(Question.objects.filter(category=category))
            selected_questions = random.sample(category_questions, 4)
            ticket_questions.extend(selected_questions)
        
        # Shuffle the final list to mix categories
        random.shuffle(ticket_questions)
        
        ticket.questions.set(ticket_questions)
        
        # Verify the distribution
        category_distribution = {}
        for question in ticket_questions:
            cat_name = question.category.name_uz
            category_distribution[cat_name] = category_distribution.get(cat_name, 0) + 1
        
        print(f"Bilet {i}: {len(ticket_questions)} ta savol")
        for cat, count in category_distribution.items():
            print(f"  - {cat}: {count} ta")

def main():
    print("Muvozanatli test biletlari yaratilmoqda...\n")
    create_balanced_test_tickets()
    
    print(f"\nYakuniy statistika:")
    print(f"Test biletlari: {TestTicket.objects.count()}")
    
    # Show sample ticket
    sample_ticket = TestTicket.objects.first()
    if sample_ticket:
        print(f"\nNamuna bilet ({sample_ticket.name}):")
        questions = sample_ticket.questions.all()
        for i, question in enumerate(questions[:5], 1):
            print(f"  {i}. {question.question_text[:60]}...")
            print(f"     Kategoriya: {question.category.name_uz}")

if __name__ == '__main__':
    main()