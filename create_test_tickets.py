import os
import sys
import django

# Django environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, Question, Answer, TestTicket
import random

def create_test_tickets():
    """20 ta test bileti yaratish, har birida 20 ta tasodifiy savol"""
    
    # Barcha mavjud savollarni olish (test category'dan tashqari)
    all_questions = list(Question.objects.exclude(category__name='test'))
    
    print(f"Jami savollar soni: {len(all_questions)}")
    print("20 ta test bileti yaratilmoqda...\n")
    
    # Mavjud biletlarni o'chirish
    TestTicket.objects.all().delete()
    print("Mavjud biletlar o'chirildi.")
    
    # 20 ta bilet yaratish
    for ticket_num in range(1, 21):
        # Bilet yaratish
        ticket = TestTicket.objects.create(
            ticket_number=ticket_num,
            name=f"Bilet {ticket_num}"
        )
        
        # 20 ta tasodifiy savol tanlash
        if len(all_questions) >= 20:
            selected_questions = random.sample(all_questions, 20)
        else:
            # Agar savollar 20 tadan kam bo'lsa, qaytarib tanlash
            selected_questions = []
            for i in range(20):
                selected_questions.append(random.choice(all_questions))
        
        # Savollarni biletga qo'shish
        ticket.questions.set(selected_questions)
        
        print(f"+ Bilet {ticket_num}: {len(selected_questions)} ta savol qo'shildi")
    
    print(f"\n20 ta bilet muvaffaqiyatli yaratildi!")
    
    # Statistika
    print("\nBILETLAR STATISTIKASI:")
    print("=" * 40)
    
    tickets = TestTicket.objects.all().order_by('ticket_number')
    for ticket in tickets:
        questions_count = ticket.questions.count()
        print(f"Bilet {ticket.ticket_number}: {questions_count} ta savol")
    
    print("=" * 40)
    print(f"Jami: {tickets.count()} ta bilet yaratildi")

if __name__ == '__main__':
    create_test_tickets()