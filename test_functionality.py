#!/usr/bin/env python
"""
Yangi AI functionality ni test qilish
"""

import os
import sys
import django
from pathlib import Path

# Django muhitini sozlash
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.ai_analytics import get_ai_insights_for_user, get_ai_analysis_for_single_test
from account.models import CustomUser
from quiz.models import TestResult, Category, Question, UserAnswer, Answer
from django.utils import timezone
from datetime import timedelta

def test_new_functionality():
    """Yangi AI funksiyalarini test qilish"""
    print("[TEST] Yangi AI functionality ni test qilish")
    print("=" * 60)
    
    # 1. Foydalanuvchini topish
    user = CustomUser.objects.first()
    if not user:
        print("[XATO] Foydalanuvchi topilmadi. Admin yarating!")
        return False
    
    print(f"[USER] Test foydalanuvchisi: {user.username}")
    
    # 2. Test natijalarini tekshirish
    test_results = TestResult.objects.filter(user=user)
    print(f"[TESTLAR] Jami testlar: {test_results.count()}")
    
    if test_results.count() == 0:
        print("[OGOHLANTIRISH] Test natijalari yo'q. Sample yaratamizmi?")
        create_sample = create_sample_data(user)
        if not create_sample:
            return False
        test_results = TestResult.objects.filter(user=user)
    
    # 3. Umumiy AI tahlilini test qilish
    print("\n[TEST1] Umumiy AI tahlil...")
    try:
        general_analysis = get_ai_insights_for_user(user)
        if general_analysis and 'ai_analysis' in general_analysis:
            print("[MUVAFFAQIYAT] Umumiy AI tahlil ishlayapti")
            print(f"[JAVOB] {general_analysis['ai_analysis'][:100]}...")
        else:
            print("[MUAMMO] Umumiy AI tahlilida muammo")
    except Exception as e:
        print(f"[XATO] Umumiy AI tahlilida xato: {str(e)}")
    
    # 4. Bitta test tahlilini test qilish
    print("\n[TEST2] Bitta test AI tahlili...")
    first_test = test_results.first()
    if first_test:
        try:
            single_analysis = get_ai_analysis_for_single_test(first_test)
            if single_analysis and 'ai_analysis' in single_analysis:
                print("[MUVAFFAQIYAT] Bitta test AI tahlili ishlayapti")
                print(f"[JAVOB] {single_analysis['ai_analysis'][:100]}...")
                
                # Test ma'lumotlarini ko'rsatish
                if 'data_used' in single_analysis:
                    data = single_analysis['data_used']
                    print(f"[TEST MA'LUMOT] Score: {data['test_info']['score']}/{data['test_info']['total_questions']}")
                    print(f"[XATOLAR] {data['wrong_count']} ta xato")
            else:
                print("[MUAMMO] Bitta test AI tahlilida muammo")
        except Exception as e:
            print(f"[XATO] Bitta test AI tahlilida xato: {str(e)}")
    else:
        print("[XATO] Test natijasi topilmadi")
    
    print("\n" + "=" * 60)
    print("[YAKUNIY] Test yakunlandi")
    return True

def create_sample_data(user):
    """Sample test ma'lumotlari yaratish"""
    print("\n[SAMPLE] Sample ma'lumot yaratish...")
    
    try:
        # Kategoriya topish yoki yaratish
        category, created = Category.objects.get_or_create(
            name="Sample Category",
            defaults={
                'name_uz': 'Test kategoriyasi',
                'description': 'Test uchun kategoriya'
            }
        )
        
        # Savol yaratish
        question, created = Question.objects.get_or_create(
            category=category,
            question_text="Bu test savoli",
            defaults={'explanation': 'Test tushuntirishi'}
        )
        
        # Javoblar yaratish
        correct_answer, created = Answer.objects.get_or_create(
            question=question,
            answer_text="To'g'ri javob",
            defaults={'is_correct': True}
        )
        
        wrong_answer, created = Answer.objects.get_or_create(
            question=question,
            answer_text="Xato javob",
            defaults={'is_correct': False}
        )
        
        # Test result yaratish
        test_result = TestResult.objects.create(
            user=user,
            category=category,
            score=16,
            total_questions=20,
            time_taken=timedelta(minutes=10),
            passed=False,
            test_type='category'
        )
        
        # User answer yaratish (xato javob)
        UserAnswer.objects.create(
            test_result=test_result,
            question=question,
            selected_answer=wrong_answer,
            is_correct=False
        )
        
        print("[SAMPLE] Sample ma'lumotlar yaratildi!")
        return True
        
    except Exception as e:
        print(f"[XATO] Sample yaratishda xato: {str(e)}")
        return False

if __name__ == "__main__":
    test_new_functionality()