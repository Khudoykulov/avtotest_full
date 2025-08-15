import os
import sys
import django

# Django environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, Question, Answer

def add_questions():
    """40 ta test savoli qo'shish"""
    
    # Category'larni olish yoki yaratish
    categories = {}
    cat_names = {
        'traffic_rules': 'Yo\'l harakati qoidalari',
        'road_signs': 'Yo\'l belgilari', 
        'traffic_lights': 'Svetofor',
        'overtaking': 'Quvib o\'tish',
        'parking': 'To\'xtash va turish',
        'speed_limits': 'Tezlik chegarasi',
        'emergency': 'Favqulodda holatlar',
        'vehicle_tech': 'Transport vositasi texnikasi'
    }
    
    for key, name in cat_names.items():
        category, created = Category.objects.get_or_create(
            name_uz=name,
            defaults={'name': name, 'description': f'{name} bo\'yicha savollar'}
        )
        categories[key] = category
        if created:
            print(f"+ Yangi category yaratildi: {name}")
    
    # 40 ta test savoli
    questions_data = [
        # Yo'l harakati qoidalari (10 ta)
        {
            'category': 'traffic_rules',
            'question': 'Yo\'l harakati qatnashchilari qaysilar?',
            'answers': [
                ('Haydovchilar, yo\'lovchilar, piyodalar', True),
                ('Faqat haydovchilar', False),
                ('Faqat avtomobillar', False),
                ('Faqat piyodalar', False)
            ]
        },
        {
            'category': 'traffic_rules',
            'question': 'Haydovchilik guvohnomasisiz transport vositasini boshqarish mumkinmi?',
            'answers': [
                ('Yo\'q, mutlaqo taqiqlanadi', True),
                ('Ha, qisqa masofaga mumkin', False),
                ('Faqat tunda mumkin', False),
                ('Faqat shahar tashqarisida mumkin', False)
            ]
        },
        {
            'category': 'traffic_rules',
            'question': 'Transport vositasida birinchi tibbiy yordam to\'plami bo\'lishi shartmi?',
            'answers': [
                ('Ha, majburiy', True),
                ('Yo\'q, ixtiyoriy', False),
                ('Faqat yuk avtomobillarida', False),
                ('Faqat taksida', False)
            ]
        },
        {
            'category': 'traffic_rules',
            'question': 'Yo\'l harakati qoidalarini buzgani uchun jazoni kim belgilaydi?',
            'answers': [
                ('YHX xodimi', True),
                ('Har qanday fuqaro', False),
                ('Yo\'lovchi', False),
                ('Mexanik', False)
            ]
        },
        {
            'category': 'traffic_rules',
            'question': 'Qanday holatlarda favqulodda to\'xtash signali yoqiladi?',
            'answers': [
                ('Avariya yoki texnik nosozlik', True),
                ('Yoqilg\'i tugaganda', False),
                ('Telefon qo\'ng\'irog\'i kelganda', False),
                ('Charchaganda', False)
            ]
        },
        {
            'category': 'traffic_rules',
            'question': 'Transport vositasida o\'t o\'chiruvchi bo\'lishi shartmi?',
            'answers': [
                ('Ha, majburiy', True),
                ('Yo\'q, talab qilinmaydi', False),
                ('Faqat yuk mashinalarda', False),
                ('Faqat avtobusda', False)
            ]
        },
        {
            'category': 'traffic_rules',
            'question': 'Haydovchi mobil telefon bilan gaplashishi mumkinmi?',
            'answers': [
                ('Faqat hands-free qurilma bilan', True),
                ('Ha, istalgan vaqtda', False),
                ('Yo\'q, hech qachon', False),
                ('Faqat svetoforda', False)
            ]
        },
        {
            'category': 'traffic_rules',
            'question': 'Yo\'l harakati ishtirokchilarining asosiy burchi nima?',
            'answers': [
                ('Xavfsizlik qoidalariga rioya qilish', True),
                ('Tez yetib borish', False),
                ('Yoqilg\'ini tejash', False),
                ('Boshqalarga rozi bo\'lmaslik', False)
            ]
        },
        {
            'category': 'traffic_rules',
            'question': 'Avtomobilning texnik holati qanday bo\'lishi kerak?',
            'answers': [
                ('Yo\'l xavfsizligini ta\'minlaydigan', True),
                ('Faqat ishlaydigan', False),
                ('Yangi', False),
                ('Qimmat', False)
            ]
        },
        {
            'category': 'traffic_rules', 
            'question': 'Haydovchi nima uchun javobgar?',
            'answers': [
                ('Yo\'l harakati xavfsizligi uchun', True),
                ('Faqat o\'zi uchun', False),
                ('Faqat yo\'lovchilar uchun', False),
                ('Hech kim uchun', False)
            ]
        },
        
        # Yo'l belgilari (8 ta)
        {
            'category': 'road_signs',
            'question': 'Qizil rang doirasi ichida oq chiziq qanday belgini bildiradi?',
            'answers': [
                ('Kirish taqiqlanadi', True),
                ('To\'xtash majburiy', False),
                ('Ehtiyot bo\'lish', False),
                ('Yo\'l yakunlanadi', False)
            ]
        },
        {
            'category': 'road_signs',
            'question': 'Uchburchak shaklidagi belgilar nimani bildiradi?',
            'answers': [
                ('Ogohlantiruvchi belgilar', True),
                ('Taqiqlovchi belgilar', False),
                ('Majburiy belgilar', False),
                ('Axborot belgilari', False)
            ]
        },
        {
            'category': 'road_signs',
            'question': 'Ko\'k rang doiraviy belgilar nimani anglatadi?',
            'answers': [
                ('Majburiy belgilar', True),
                ('Taqiqlovchi belgilar', False),
                ('Ogohlantiruvchi belgilar', False),
                ('Xizmat belgilari', False)
            ]
        },
        {
            'category': 'road_signs',
            'question': '"STOP" belgisi qanday shaklda bo\'ladi?',
            'answers': [
                ('Sakkiz burchakli', True),
                ('Dumaloq', False),
                ('Uchburchak', False),
                ('To\'rtburchak', False)
            ]
        },
        {
            'category': 'road_signs',
            'question': 'Sariq rang fonda qanday belgilar joylashadi?',
            'answers': [
                ('Ogohlantiruvchi belgilar', True),
                ('Taqiqlovchi belgilar', False),
                ('Majburiy belgilar', False),
                ('Yo\'nalish belgilari', False)
            ]
        },
        {
            'category': 'road_signs',
            'question': '"Piyodalar yo\'li" belgisi qanday ko\'rinishda?',
            'answers': [
                ('Ko\'k fonda oq piyoda figurasi', True),
                ('Qizil fonda piyoda', False),
                ('Sariq fonda piyoda', False),
                ('Oq fonda qora piyoda', False)
            ]
        },
        {
            'category': 'road_signs',
            'question': 'Tezlik chegarasini ko\'rsatuvchi belgilar qanday?',
            'answers': [
                ('Oq doira ichida qizil raqam', True),
                ('Ko\'k doira ichida oq raqam', False),
                ('Sariq doira ichida qora raqam', False),
                ('Yashil doira ichida oq raqam', False)
            ]
        },
        {
            'category': 'road_signs',
            'question': '"Yo\'l ishlarini" belgilar qayerda qo\'yiladi?',
            'answers': [
                ('Ta\'mirlash zonasidan oldin', True),
                ('Ta\'mirlash zonasidan keyin', False),
                ('Ixtiyoriy joyda', False),
                ('Faqat tunlari', False)
            ]
        },
        
        # Svetofor (5 ta)
        {
            'category': 'traffic_lights',
            'question': 'Svetoforning qizil signali nimani bildiradi?',
            'answers': [
                ('Harakat taqiqlanadi', True),
                ('Ehtiyotkorlik bilan harakat', False),
                ('Tez o\'tish kerak', False),
                ('Kutib turish', False)
            ]
        },
        {
            'category': 'traffic_lights',
            'question': 'Sariq signal qachon yonadi?',
            'answers': [
                ('Qizildan yashilga o\'tishdan oldin', True),
                ('Faqat kechqurun', False),
                ('Xatolik belgisi sifatida', False),
                ('Tezlikni oshirish uchun', False)
            ]
        },
        {
            'category': 'traffic_lights',
            'question': 'Yashil svetofor yonganda nima qilish kerak?',
            'answers': [
                ('Ehtiyotkorlik bilan harakatlanish', True),
                ('Maksimal tezlikda ketish', False),
                ('Kutib turish', False),
                ('Orqaga qaytish', False)
            ]
        },
        {
            'category': 'traffic_lights',
            'question': 'Svetofor ishlamasa, haydovchi nima qilishi kerak?',
            'answers': [
                ('Yo\'l belgilariga amal qilish', True),
                ('Tez o\'tib ketish', False),
                ('Kutib turish', False),
                ('Svetofor tuzatilgunga qadar turish', False)
            ]
        },
        {
            'category': 'traffic_lights',
            'question': 'Qo\'shimcha svetofor (o\'q bilan) nimani bildiradi?',
            'answers': [
                ('Shu yo\'nalishda harakatlanish ruxsat', True),
                ('Barcha yo\'nalishlarga ruxsat', False),
                ('Taqiqlanadi', False),
                ('Faqat piyodalar uchun', False)
            ]
        },
        
        # Quvib o'tish (4 ta)
        {
            'category': 'overtaking',
            'question': 'Qaysi joylarda quvib o\'tish taqiqlanadi?',
            'answers': [
                ('Piyoda o\'tkazmalar, ko\'priklar, burilishlarda', True),
                ('Faqat tunlari', False),
                ('Hech qayerda', False),
                ('Faqat shahar ichida', False)
            ]
        },
        {
            'category': 'overtaking',
            'question': 'Quvib o\'tishdan oldin nima qilish kerak?',
            'answers': [
                ('Chap tomonga burilish signalini berish', True),
                ('Ovoz signali berish', False),
                ('Tezlikni oshirish', False),
                ('Hech narsa qilmaslik', False)
            ]
        },
        {
            'category': 'overtaking',
            'question': 'Quvib o\'tishni qachon boshlash mumkin?',
            'answers': [
                ('Xavfsizlik kafolatlanganda', True),
                ('Doim', False),
                ('Boshqa avtomobil sekin ketayotganda', False),
                ('Shoshilinch holatda', False)
            ]
        },
        {
            'category': 'overtaking',
            'question': 'Davlat raqamidan keyin qaytishda nima qilish kerak?',
            'answers': [
                ('O\'ng tomonga burilish signalini berish', True),
                ('Chap signal davom ettirish', False),
                ('Signal bermaslik', False),
                ('Faqat ovoz signali', False)
            ]
        },
        
        # To'xtash va turish (4 ta)
        {
            'category': 'parking',
            'question': 'Transport vositasini qayerda to\'xtatish mumkin?',
            'answers': [
                ('Belgilangan joylarda', True),
                ('Istalgan joyda', False),
                ('Faqat uydan oldin', False),
                ('Yo\'lning o\'rtasida', False)
            ]
        },
        {
            'category': 'parking',
            'question': 'Piyoda o\'tkazmasida to\'xtash mumkinmi?',
            'answers': [
                ('Yo\'q, qat\'iyan taqiqlanadi', True),
                ('Ha, qisqa vaqtga', False),
                ('Faqat kechqurun', False),
                ('Faqat yo\'lovchi tushirganda', False)
            ]
        },
        {
            'category': 'parking',
            'question': 'Svetofor yaqinida necha metrdan kam to\'xtash taqiq?',
            'answers': [
                ('5 metr', True),
                ('10 metr', False),
                ('1 metr', False),
                ('20 metr', False)
            ]
        },
        {
            'category': 'parking',
            'question': 'Yo\'lda uzoq vaqt turgan avtomobilni qanday belgilash kerak?',
            'answers': [
                ('Favqulodda to\'xtash signali bilan', True),
                ('Chiroqlarni yoqish bilan', False),
                ('Ovoz signali bilan', False),
                ('Hech qanday belgilamaslik', False)
            ]
        },
        
        # Tezlik chegarasi (4 ta)
        {
            'category': 'speed_limits',
            'question': 'Shahar ichidagi maksimal tezlik qancha?',
            'answers': [
                ('60 km/soat', True),
                ('80 km/soat', False),
                ('100 km/soat', False),
                ('40 km/soat', False)
            ]
        },
        {
            'category': 'speed_limits',
            'question': 'Avtomobil yo\'llarda maksimal tezlik?',
            'answers': [
                ('100 km/soat', True),
                ('80 km/soat', False),
                ('120 km/soat', False),
                ('90 km/soat', False)
            ]
        },
        {
            'category': 'speed_limits',
            'question': 'Maktab, bog\'cha yaqinida tezlik qancha bo\'lishi kerak?',
            'answers': [
                ('20-30 km/soat', True),
                ('60 km/soat', False),
                ('40 km/soat', False),
                ('80 km/soat', False)
            ]
        },
        {
            'category': 'speed_limits',
            'question': 'Yomg\'irli havoda tezlik qanday bo\'lishi kerak?',
            'answers': [
                ('Kamaytirilishi kerak', True),
                ('Odatdagidek', False),
                ('Ko\'paytirilishi kerak', False),
                ('Maksimal', False)
            ]
        },
        
        # Favqulodda holatlar (3 ta) 
        {
            'category': 'emergency',
            'question': 'Avariya yuz berganda birinchi navbatda nima qilish kerak?',
            'answers': [
                ('Favqulodda signal yoqish', True),
                ('Tez qochish', False),
                ('Foto suratga olish', False),
                ('Boshqalarni ayblash', False)
            ]
        },
        {
            'category': 'emergency',
            'question': 'Yo\'lda jarohatlangan odam bo\'lsa nima qilish kerak?',
            'answers': [
                ('103 ga qo\'ng\'iroq qilish va tibbiy yordam berish', True),
                ('O\'tib ketish', False),
                ('Foto suratga olish', False),
                ('Faqat kuzatish', False)
            ]
        },
        {
            'category': 'emergency',
            'question': 'Transport vositasi yonayotgan bo\'lsa nima qilish kerak?',
            'answers': [
                ('O\'t o\'chiruvchi yordamida o\'chirish', True),
                ('Suv sepish', False),
                ('Hech narsa qilmaslik', False),
                ('Benzin quyish', False)
            ]
        },
        
        # Transport vositasi texnikasi (2 ta)
        {
            'category': 'vehicle_tech',
            'question': 'Tormoz tizimi qanday tekshiriladi?',
            'answers': [
                ('Sekin harakatda sinab ko\'rish orqali', True),
                ('Tez harakatda', False),
                ('Faqat ko\'zda', False),
                ('Mexanikni chaqirish orqali', False)
            ]
        },
        {
            'category': 'vehicle_tech',
            'question': 'Avtomobilning asosiy xavfsizlik tizimlari qaysilar?',
            'answers': [
                ('Tormoz, rul, chiroqlar', True),
                ('Faqat dvigatel', False),
                ('Faqat g\'ildiraklari', False),
                ('Faqat kuzov', False)
            ]
        }
    ]
    
    print("40 ta test savoli qo'shilmoqda...\n")
    
    added_count = 0
    for q_data in questions_data:
        # Savol yaratish
        question = Question.objects.create(
            category=categories[q_data['category']],
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
    
    print(f"\nJami {added_count} ta savol muvaffaqiyatli qo'shildi!")
    
    # Statistika
    for cat_key, category in categories.items():
        count = Question.objects.filter(category=category).count()
        print(f"   - {category.name_uz}: {count} ta savol")

if __name__ == '__main__':
    add_questions()