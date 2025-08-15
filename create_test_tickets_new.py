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

def create_test_tickets():
    """Create test tickets with 20 questions each"""
    questions = list(Question.objects.all())
    if len(questions) < 20:
        print(f"Test biletlarini yaratish uchun kamida 20 ta savol kerak. Hozir {len(questions)} ta bor.")
        return
    
    # Delete existing tickets to recreate them
    TestTicket.objects.all().delete()
    print("Eski test biletlari o'chirildi.")
    
    # Create 10 test tickets
    for i in range(1, 11):
        ticket = TestTicket.objects.create(
            ticket_number=i,
            name=f'Test bileti {i}'
        )
        
        # Add 20 random questions to each ticket
        ticket_questions = random.sample(questions, min(20, len(questions)))
        ticket.questions.set(ticket_questions)
        print(f"Test bileti {i} yaratildi - {len(ticket_questions)} ta savol")

def main():
    print("Test biletlari yaratilmoqda...")
    create_test_tickets()
    
    print(f"\nStatistika:")
    print(f"Test biletlari: {TestTicket.objects.count()}")

if __name__ == '__main__':
    main()
