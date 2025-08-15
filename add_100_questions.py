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

def add_traffic_rules_questions():
    """Yo'lda harakat qoidalari uchun 20 ta savol"""
    category = Category.objects.filter(name_uz='Yo\'lda harakat qoidalari').first()
    if not category:
        print("Yo'lda harakat qoidalari kategoriyasi topilmadi")
        return
    
    questions_data = [
        {
            'question_text': 'Shahar ichida maksimal ruxsat etilgan tezlik necha km/soat?',
            'answers': [
                {'text': '60 km/soat', 'correct': True},
                {'text': '50 km/soat', 'correct': False},
                {'text': '70 km/soat', 'correct': False},
                {'text': '80 km/soat', 'correct': False}
            ]
        },
        {
            'question_text': 'Magistral yo\'llarda maksimal tezlik necha?',
            'answers': [
                {'text': '110 km/soat', 'correct': True},
                {'text': '100 km/soat', 'correct': False},
                {'text': '120 km/soat', 'correct': False},
                {'text': '90 km/soat', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomagistralda minimal tezlik necha?',
            'answers': [
                {'text': '60 km/soat', 'correct': True},
                {'text': '50 km/soat', 'correct': False},
                {'text': '70 km/soat', 'correct': False},
                {'text': '40 km/soat', 'correct': False}
            ]
        },
        {
            'question_text': 'Piyoda o\'tish joyida piyodaga yo\'l berish majburiymi?',
            'answers': [
                {'text': 'Ha, har doim', 'correct': True},
                {'text': 'Yo\'q', 'correct': False},
                {'text': 'Faqat svetaforda', 'correct': False},
                {'text': 'Faqat bolalarga', 'correct': False}
            ]
        },
        {
            'question_text': 'Haydovchilik guvohnomasiz haydash mumkinmi?',
            'answers': [
                {'text': 'Yo\'q, qat\'iyan taqiqlangan', 'correct': True},
                {'text': 'Ha, qisqa masofada', 'correct': False},
                {'text': 'Ha, tanish yo\'llarda', 'correct': False},
                {'text': 'Ha, katta yoshda', 'correct': False}
            ]
        },
        {
            'question_text': 'Alkogol iste\'mol qilgandan keyin haydash mumkinmi?',
            'answers': [
                {'text': 'Yo\'q, mutlaqo taqiqlangan', 'correct': True},
                {'text': 'Ha, oz miqdorda', 'correct': False},
                {'text': 'Ha, 1 soatdan keyin', 'correct': False},
                {'text': 'Ha, ehtiyotkorlik bilan', 'correct': False}
            ]
        },
        {
            'question_text': 'Yo\'lda to\'xtash uchun qanday signal berish kerak?',
            'answers': [
                {'text': 'Favqulodda signal yoqish', 'correct': True},
                {'text': 'Chap indikator', 'correct': False},
                {'text': 'O\'ng indikator', 'correct': False},
                {'text': 'Hech qanday signal bermaslik', 'correct': False}
            ]
        },
        {
            'question_text': 'Orqadan kelayotgan transport vositasi o\'tmoqchi bo\'lsa nima qilish kerak?',
            'answers': [
                {'text': 'Yo\'l berish', 'correct': True},
                {'text': 'Tezlikni oshirish', 'correct': False},
                {'text': 'E\'tibor bermaslik', 'correct': False},
                {'text': 'To\'siq qilish', 'correct': False}
            ]
        },
        {
            'question_text': 'Kesishmada kim birinchi o\'tadi?',
            'answers': [
                {'text': 'O\'ng tomondagi transport', 'correct': True},
                {'text': 'Chap tomondagi', 'correct': False},
                {'text': 'Tezroq kelgan', 'correct': False},
                {'text': 'Kattaroq transport', 'correct': False}
            ]
        },
        {
            'question_text': 'Yo\'l belgisi va svetafor ziddiyat kelsa nimaga amal qilish kerak?',
            'answers': [
                {'text': 'Svetafor signallariga', 'correct': True},
                {'text': 'Yo\'l belgilariga', 'correct': False},
                {'text': 'O\'z fikrrigacha', 'correct': False},
                {'text': 'Boshqa haydovchilarga', 'correct': False}
            ]
        },
        {
            'question_text': 'Kechasi faralar qanday bo\'lishi kerak?',
            'answers': [
                {'text': 'Yoqilgan bo\'lishi majburiy', 'correct': True},
                {'text': 'O\'chirilgan', 'correct': False},
                {'text': 'Miltillovchi', 'correct': False},
                {'text': 'Faqat tuman faralar', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobil texnik ko\'rigidan o\'tishi kerakmi?',
            'answers': [
                {'text': 'Ha, majburiy', 'correct': True},
                {'text': 'Yo\'q', 'correct': False},
                {'text': 'Faqat eski avtomobillarda', 'correct': False},
                {'text': 'Faqat tijorat transportida', 'correct': False}
            ]
        },
        {
            'question_text': 'Yo\'lda hayvonlar paydo bo\'lsa nima qilish kerak?',
            'answers': [
                {'text': 'Ehtiyotkorlik bilan sekin harakat qilish', 'correct': True},
                {'text': 'Signal berish va o\'tish', 'correct': False},
                {'text': 'Tezlikni oshirish', 'correct': False},
                {'text': 'To\'xtamaslik', 'correct': False}
            ]
        },
        {
            'question_text': 'Yo\'l qoidalarini buzganligi uchun jazo bormi?',
            'answers': [
                {'text': 'Ha, jarima va boshqa jazolar', 'correct': True},
                {'text': 'Yo\'q', 'correct': False},
                {'text': 'Faqat ogohlantirishk', 'correct': False},
                {'text': 'Faqat birinchi marta', 'correct': False}
            ]
        },
        {
            'question_text': 'Transport vositasida birinchi yordam vositalari bo\'lishi kerakmi?',
            'answers': [
                {'text': 'Ha, majburiy', 'correct': True},
                {'text': 'Yo\'q', 'correct': False},
                {'text': 'Faqat taxi\'larda', 'correct': False},
                {'text': 'Faqat yuk mashinalarida', 'correct': False}
            ]
        },
        {
            'question_text': 'Telefon bilan gaplashib haydash mumkinmi?',
            'answers': [
                {'text': 'Yo\'q, hands-free dan tashqari', 'correct': True},
                {'text': 'Ha, doim', 'correct': False},
                {'text': 'Faqat qisqa qo\'ng\'iroqlarda', 'correct': False},
                {'text': 'Faqat muhim qo\'ng\'iroqlarda', 'correct': False}
            ]
        },
        {
            'question_text': 'Yo\'l chetida avtomobil qoldirish mumkinmi?',
            'answers': [
                {'text': 'Maxsus joylarda ruxsat bilan', 'correct': True},
                {'text': 'Ha, istalgan joyda', 'correct': False},
                {'text': 'Yo\'q, hech qayerda', 'correct': False},
                {'text': 'Faqat kechasi', 'correct': False}
            ]
        },
        {
            'question_text': 'Boshqa haydovchiga yordamlashish majburiyatimi?',
            'answers': [
                {'text': 'Ha, agar xavf bo\'lmasa', 'correct': True},
                {'text': 'Yo\'q', 'correct': False},
                {'text': 'Faqat tanishga', 'correct': False},
                {'text': 'Faqat pullik', 'correct': False}
            ]
        },
        {
            'question_text': 'Yo\'l harakati qoidalarini bilmaslik bahonami?',
            'answers': [
                {'text': 'Yo\'q, javobgarlik bor', 'correct': True},
                {'text': 'Ha, bilmasam aybim yo\'q', 'correct': False},
                {'text': 'Ba\'zi hollarda', 'correct': False},
                {'text': 'Faqat birinchi marta', 'correct': False}
            ]
        },
        {
            'question_text': 'Yo\'l qoidalari barcha haydovchilar uchun birxilmi?',
            'answers': [
                {'text': 'Ha, hamma uchun bir xil', 'correct': True},
                {'text': 'Yo\'q, tajribali haydovchilar uchun boshqacha', 'correct': False},
                {'text': 'Yo\'q, yosh haydovchilar uchun boshqacha', 'correct': False},
                {'text': 'Yo\'q, transport turiga qarab', 'correct': False}
            ]
        }
    ]
    
    create_questions_for_category(category, questions_data)

def add_road_signs_questions():
    """Yo'l belgilari uchun 20 ta savol"""
    category = Category.objects.filter(name_uz='Yo\'l belgilari').first()
    if not category:
        print("Yo'l belgilari kategoriyasi topilmadi")
        return
    
    questions_data = [
        {
            'question_text': 'Qizil doira ichida oq chiziq nimani anglatadi?',
            'answers': [
                {'text': 'Kirish taqiqlangan', 'correct': True},
                {'text': 'To\'xtash joyi', 'correct': False},
                {'text': 'Majburiy yo\'nalish', 'correct': False},
                {'text': 'Ogohlantirish', 'correct': False}
            ]
        },
        {
            'question_text': 'Uchburchak shaklidagi sariq belgi nima?',
            'answers': [
                {'text': 'Ogohlantruvchi belgi', 'correct': True},
                {'text': 'Taqiqlovchi belgi', 'correct': False},
                {'text': 'Majburiy belgi', 'correct': False},
                {'text': 'Ma\'lumot belgisi', 'correct': False}
            ]
        },
        {
            'question_text': 'Ko\'k doira shaklidagi belgi nima?',
            'answers': [
                {'text': 'Majburiy belgi', 'correct': True},
                {'text': 'Taqiqlovchi belgi', 'correct': False},
                {'text': 'Ogohlantiruvchi belgi', 'correct': False},
                {'text': 'Ma\'lumot belgisi', 'correct': False}
            ]
        },
        {
            'question_text': 'STOP belgisining rangi qanday?',
            'answers': [
                {'text': 'Qizil', 'correct': True},
                {'text': 'Sariq', 'correct': False},
                {'text': 'Ko\'k', 'correct': False},
                {'text': 'Yashil', 'correct': False}
            ]
        },
        {
            'question_text': 'Yo\'l ustunligi belgisi qanday shakl?',
            'answers': [
                {'text': 'Romb', 'correct': True},
                {'text': 'Doira', 'correct': False},
                {'text': 'Uchburchak', 'correct': False},
                {'text': 'Kvadrat', 'correct': False}
            ]
        },
        {
            'question_text': 'Piyoda o\'tish joyi qanday belgilanadi?',
            'answers': [
                {'text': 'Zebra chiziqlar bilan', 'correct': True},
                {'text': 'Sariq chiziq bilan', 'correct': False},
                {'text': 'Ko\'k rang bilan', 'correct': False},
                {'text': 'Nuqtalar bilan', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtobuslar bekatini qanday belgi ko\'rsatadi?',
            'answers': [
                {'text': 'Avtobusning tasviri', 'correct': True},
                {'text': 'A harfi', 'correct': False},
                {'text': 'Qizil doira', 'correct': False},
                {'text': 'Sariq uchburchak', 'correct': False}
            ]
        },
        {
            'question_text': 'Haydovchilar maktabi belgisi qanday?',
            'answers': [
                {'text': 'U harfi', 'correct': True},
                {'text': 'M harfi', 'correct': False},
                {'text': 'D harfi', 'correct': False},
                {'text': 'H harfi', 'correct': False}
            ]
        },
        {
            'question_text': 'Yoqilg\'i quyish shoxobchasi belgisi?',
            'answers': [
                {'text': 'Benzin kolbasi tasviri', 'correct': True},
                {'text': 'B harfi', 'correct': False},
                {'text': 'Y harfi', 'correct': False},
                {'text': 'Doira', 'correct': False}
            ]
        },
        {
            'question_text': 'Shifokorga qanday belgi yo\'l ko\'rsatadi?',
            'answers': [
                {'text': 'Qizil xoch', 'correct': True},
                {'text': 'S harfi', 'correct': False},
                {'text': 'Ko\'k doira', 'correct': False},
                {'text': 'Sariq kvadrat', 'correct': False}
            ]
        },
        {
            'question_text': 'Telefon belgisining rangi qanday?',
            'answers': [
                {'text': 'Ko\'k', 'correct': True},
                {'text': 'Qizil', 'correct': False},
                {'text': 'Sariq', 'correct': False},
                {'text': 'Yashil', 'correct': False}
            ]
        },
        {
            'question_text': 'Mehmonxona belgisi qanday?',
            'answers': [
                {'text': 'To\'shak tasviri', 'correct': True},
                {'text': 'M harfi', 'correct': False},
                {'text': 'Uy tasviri', 'correct': False},
                {'text': 'H harfi', 'correct': False}
            ]
        },
        {
            'question_text': 'Ovqat belgisining rangi?',
            'answers': [
                {'text': 'Ko\'k', 'correct': True},
                {'text': 'Qizil', 'correct': False},
                {'text': 'Sariq', 'correct': False},
                {'text': 'Pushti', 'correct': False}
            ]
        },
        {
            'question_text': 'Tunnel belgisi qanday ko\'rinadi?',
            'answers': [
                {'text': 'Tunnel tasviri', 'correct': True},
                {'text': 'T harfi', 'correct': False},
                {'text': 'Doira', 'correct': False},
                {'text': 'Kvadrat', 'correct': False}
            ]
        },
        {
            'question_text': 'Ko\'prik belgisi qanday?',
            'answers': [
                {'text': 'Ko\'prik tasviri', 'correct': True},
                {'text': 'K harfi', 'correct': False},
                {'text': 'Chiziqlar', 'correct': False},
                {'text': 'Doira', 'correct': False}
            ]
        },
        {
            'question_text': 'Xavfli burilish belgisi rangi?',
            'answers': [
                {'text': 'Sariq', 'correct': True},
                {'text': 'Qizil', 'correct': False},
                {'text': 'Ko\'k', 'correct': False},
                {'text': 'Yashil', 'correct': False}
            ]
        },
        {
            'question_text': 'Tez yordam xizmati belgisi?',
            'answers': [
                {'text': 'Qizil xoch', 'correct': True},
                {'text': 'T harfi', 'correct': False},
                {'text': 'Yashil xoch', 'correct': False},
                {'text': 'Ko\'k xoch', 'correct': False}
            ]
        },
        {
            'question_text': 'Bolalar o\'ynash joyi belgisi?',
            'answers': [
                {'text': 'Bolalar tasviri', 'correct': True},
                {'text': 'B harfi', 'correct': False},
                {'text': 'O\'yin maydoncha', 'correct': False},
                {'text': 'Sariq rang', 'correct': False}
            ]
        },
        {
            'question_text': 'Velosiped yo\'li belgisi rangi?',
            'answers': [
                {'text': 'Ko\'k', 'correct': True},
                {'text': 'Qizil', 'correct': False},
                {'text': 'Sariq', 'correct': False},
                {'text': 'Yashil', 'correct': False}
            ]
        },
        {
            'question_text': 'Temir yo\'l o\'tish joyi belgisi?',
            'answers': [
                {'text': 'X shaklida chiziqlar', 'correct': True},
                {'text': 'T harfi', 'correct': False},
                {'text': 'Poezd tasviri', 'correct': False},
                {'text': 'Relslar tasviri', 'correct': False}
            ]
        }
    ]
    
    create_questions_for_category(category, questions_data)

def add_traffic_lights_questions():
    """Svetafor uchun 20 ta savol"""
    category = Category.objects.filter(name_uz='Svetafor').first()
    if not category:
        return
    
    questions_data = [
        {
            'question_text': 'Qizil svetafor signali nimani anglatadi?',
            'answers': [
                {'text': 'To\'liq to\'xtash', 'correct': True},
                {'text': 'Sekin harakat', 'correct': False},
                {'text': 'Ehtiyotkorlik', 'correct': False},
                {'text': 'Yo\'l berish', 'correct': False}
            ]
        },
        {
            'question_text': 'Sariq svetafor signali nima?',
            'answers': [
                {'text': 'Tayyorgarlik signali', 'correct': True},
                {'text': 'To\'xtash signali', 'correct': False},
                {'text': 'Harakat signali', 'correct': False},
                {'text': 'Tezlashtirish signali', 'correct': False}
            ]
        },
        {
            'question_text': 'Yashil svetafor yonganda nima qilish kerak?',
            'answers': [
                {'text': 'Ehtiyotkorlik bilan harakat qilish', 'correct': True},
                {'text': 'Darhol tezlashish', 'correct': False},
                {'text': 'To\'xtab turish', 'correct': False},
                {'text': 'Ortga qaytish', 'correct': False}
            ]
        },
        {
            'question_text': 'Miltillovchi sariq svetafor nima?',
            'answers': [
                {'text': 'Ehtiyotkorlik signali', 'correct': True},
                {'text': 'To\'xtash signali', 'correct': False},
                {'text': 'Tezlik signali', 'correct': False},
                {'text': 'Yo\'l berish signali', 'correct': False}
            ]
        },
        {
            'question_text': 'Svetafor ishlamay qolsa nima qilish kerak?',
            'answers': [
                {'text': 'Yo\'l belgilariga amal qilish', 'correct': True},
                {'text': 'Tez o\'tib ketish', 'correct': False},
                {'text': 'To\'xtab kutish', 'correct': False},
                {'text': 'Ixtiyoriy harakat', 'correct': False}
            ]
        },
        {
            'question_text': 'Qizil va sariq svetafor birga yonsa?',
            'answers': [
                {'text': 'Yashilga tayyorgarlik', 'correct': True},
                {'text': 'Darhol to\'xtash', 'correct': False},
                {'text': 'Tez harakat qilish', 'correct': False},
                {'text': 'Kutib turish', 'correct': False}
            ]
        },
        {
            'question_text': 'Piyoda svetafori qizil bo\'lsa?',
            'answers': [
                {'text': 'Piyodalar to\'xtashi kerak', 'correct': True},
                {'text': 'Ehtiyotkorlik bilan o\'tish mumkin', 'correct': False},
                {'text': 'Yo\'lni bo\'sh bo\'lsa o\'tish mumkin', 'correct': False},
                {'text': 'Yugurib o\'tish mumkin', 'correct': False}
            ]
        },
        {
            'question_text': 'Svetaforda yashil strelka nimani bildiradi?',
            'answers': [
                {'text': 'Shu yo\'nalishga harakat mumkin', 'correct': True},
                {'text': 'Barcha yo\'nalishlarga mumkin', 'correct': False},
                {'text': 'To\'xtash kerak', 'correct': False},
                {'text': 'Kutish kerak', 'correct': False}
            ]
        },
        {
            'question_text': 'Qizil strelka nimani anglatadi?',
            'answers': [
                {'text': 'Shu yo\'nalishga harakat taqiq', 'correct': True},
                {'text': 'Ehtiyotkorlik bilan o\'tish', 'correct': False},
                {'text': 'Yo\'l berish', 'correct': False},
                {'text': 'Kutib turish', 'correct': False}
            ]
        },
        {
            'question_text': 'Svetafor qancha masofadan ko\'rinishi kerak?',
            'answers': [
                {'text': '100 metrdan', 'correct': True},
                {'text': '50 metrdan', 'correct': False},
                {'text': '200 metrdan', 'correct': False},
                {'text': '25 metrdan', 'correct': False}
            ]
        },
        {
            'question_text': 'Kechasi svetafor ko\'rinmaslik mumkinmi?',
            'answers': [
                {'text': 'Yo\'q, har doim yoritilgan bo\'lishi kerak', 'correct': True},
                {'text': 'Ha, kechasi o\'chadi', 'correct': False},
                {'text': 'Ba\'zida', 'correct': False},
                {'text': 'Zarurat bo\'lgandagina', 'correct': False}
            ]
        },
        {
            'question_text': 'Svetafor ustida qanday belgir bo\'lishi mumkin?',
            'answers': [
                {'text': 'Yo\'nalish strelkalari', 'correct': True},
                {'text': 'Harflar', 'correct': False},
                {'text': 'Raqamlar', 'correct': False},
                {'text': 'Rasmlar', 'correct': False}
            ]
        },
        {
            'question_text': 'Svetafor signalini kimimlar kuzatishi kerak?',
            'answers': [
                {'text': 'Barcha yo\'l foydalanuvchilari', 'correct': True},
                {'text': 'Faqat haydovchilar', 'correct': False},
                {'text': 'Faqat piyodalar', 'correct': False},
                {'text': 'Faqat velosipedchilar', 'correct': False}
            ]
        },
        {
            'question_text': 'Svetafor buzilgan bo\'lsa kim ta\'mirlaydi?',
            'answers': [
                {'text': 'Maxsus xizmatlar', 'correct': True},
                {'text': 'Haydovchilar o\'zlari', 'correct': False},
                {'text': 'Piyodalar', 'correct': False},
                {'text': 'Politsiya', 'correct': False}
            ]
        },
        {
            'question_text': 'Svetafor va regulsovchik signallari zid kelsa?',
            'answers': [
                {'text': 'Regulsovchiga amal qilish', 'correct': True},
                {'text': 'Svetaforga amal qilish', 'correct': False},
                {'text': 'O\'z fikriga amal qilish', 'correct': False},
                {'text': 'Kutib turish', 'correct': False}
            ]
        },
        {
            'question_text': 'Svetafor qancha vaqt yashil yonadi?',
            'answers': [
                {'text': 'Dastur bo\'yicha o\'zgaruvchan', 'correct': True},
                {'text': 'Har doim 30 soniya', 'correct': False},
                {'text': 'Har doim 60 soniya', 'correct': False},
                {'text': 'Har doim 15 soniya', 'correct': False}
            ]
        },
        {
            'question_text': 'Tunda svetafor rejimi o\'zgaradimi?',
            'answers': [
                {'text': 'Ha, miltillovchi rejimga o\'tishi mumkin', 'correct': True},
                {'text': 'Yo\'q, har doim bir xil', 'correct': False},
                {'text': 'Butunlay o\'chadi', 'correct': False},
                {'text': 'Faqat sariq yonadi', 'correct': False}
            ]
        },
        {
            'question_text': 'Svetaforga yaqinlashganda tezlikni kamaytirish kerakmi?',
            'answers': [
                {'text': 'Ha, ehtiyotkorlik uchun', 'correct': True},
                {'text': 'Yo\'q, oshirish kerak', 'correct': False},
                {'text': 'Bir xil saqlash', 'correct': False},
                {'text': 'To\'xtash kerak', 'correct': False}
            ]
        },
        {
            'question_text': 'Svetafor chiroqlari necha rang bo\'ladi?',
            'answers': [
                {'text': 'Uch rang: qizil, sariq, yashil', 'correct': True},
                {'text': 'Ikki rang', 'correct': False},
                {'text': 'To\'rt rang', 'correct': False},
                {'text': 'Besh rang', 'correct': False}
            ]
        },
        {
            'question_text': 'Svetafor signalini noto\'g\'ri bajarish uchun jazo bormi?',
            'answers': [
                {'text': 'Ha, jarima va boshqa jazolar', 'correct': True},
                {'text': 'Yo\'q, jazo yo\'q', 'correct': False},
                {'text': 'Faqat ogohlantirishk', 'correct': False},
                {'text': 'Faqat birinchi marta', 'correct': False}
            ]
        }
    ]
    
    create_questions_for_category(category, questions_data)

def add_safe_driving_questions():
    """Xavfsiz haydash uchun 20 ta savol"""
    category = Category.objects.filter(name_uz='Xavfsiz haydash').first()
    if not category:
        return
    
    questions_data = [
        {
            'question_text': 'Xavfsizlik kamari qachon taqilishi kerak?',
            'answers': [
                {'text': 'Har doim, yo\'lga chiqishdan oldin', 'correct': True},
                {'text': 'Faqat uzoq safarlarda', 'correct': False},
                {'text': 'Faqat tezkor yo\'llarda', 'correct': False},
                {'text': 'Zarurat bo\'lgandagina', 'correct': False}
            ]
        },
        {
            'question_text': 'Charchagan holatda haydash xavflimi?',
            'answers': [
                {'text': 'Juda xavfli', 'correct': True},
                {'text': 'Unchalik xavfli emas', 'correct': False},
                {'text': 'Xavfli emas', 'correct': False},
                {'text': 'Faqat tunda xavfli', 'correct': False}
            ]
        },
        {
            'question_text': 'Yomg\'ir paytida tezlikni nima qilish kerak?',
            'answers': [
                {'text': 'Kamaytirish', 'correct': True},
                {'text': 'Oshirish', 'correct': False},
                {'text': 'O\'zgartirmaslik', 'correct': False},
                {'text': 'To\'xtash', 'correct': False}
            ]
        },
        {
            'question_text': 'Bolalar uchun avtokursi majburiyatimi?',
            'answers': [
                {'text': 'Ha, 12 yoshgacha', 'correct': True},
                {'text': 'Yo\'q', 'correct': False},
                {'text': 'Faqat chaqaloqlar uchun', 'correct': False},
                {'text': 'Faqat uzoq safarlarda', 'correct': False}
            ]
        },
        {
            'question_text': 'Telefon bilan gaplashib haydash mumkinmi?',
            'answers': [
                {'text': 'Faqat hands-free qurilma bilan', 'correct': True},
                {'text': 'Ha, doim mumkin', 'correct': False},
                {'text': 'Qisqa qo\'ng\'irojlarda mumkin', 'correct': False},
                {'text': 'Mutlaqo mumkin emas', 'correct': False}
            ]
        },
        {
            'question_text': 'Qishda qanday shinalar ishlatish kerak?',
            'answers': [
                {'text': 'Qishki shinalar', 'correct': True},
                {'text': 'Yozgi shinalar', 'correct': False},
                {'text': 'Universal shinalar', 'correct': False},
                {'text': 'Istalgan shinalar', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobilda birinchi yordam to\'plami bo\'lishi kerakmi?',
            'answers': [
                {'text': 'Ha, majburiy', 'correct': True},
                {'text': 'Yo\'q', 'correct': False},
                {'text': 'Faqat tijorat transportida', 'correct': False},
                {'text': 'Faqat uzoq safarlarda', 'correct': False}
            ]
        },
        {
            'question_text': 'Kechasi haydashda qanday faralar ishlatiladi?',
            'answers': [
                {'text': 'Yaqin nur', 'correct': True},
                {'text': 'Uzoq nur', 'correct': False},
                {'text': 'Tuman faralari', 'correct': False},
                {'text': 'Hech qanday', 'correct': False}
            ]
        },
        {
            'question_text': 'O\'ng ko\'zgu nimaga xizmat qiladi?',
            'answers': [
                {'text': 'O\'ng tarafdagi yo\'lni ko\'rish', 'correct': True},
                {'text': 'Orqa ko\'rinishni kengaytirish', 'correct': False},
                {'text': 'Bezak uchun', 'correct': False},
                {'text': 'Quyoshdan himoya', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobil oldida qancha masofa saqlash kerak?',
            'answers': [
                {'text': 'Kamida 3 soniyalik masofa', 'correct': True},
                {'text': '1 soniyalik masofa', 'correct': False},
                {'text': '5 metr', 'correct': False},
                {'text': '10 metr', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobil texnik holatini qancha vaqtda tekshirish kerak?',
            'answers': [
                {'text': 'Har yo\'lga chiqishdan oldin', 'correct': True},
                {'text': 'Haftada bir marta', 'correct': False},
                {'text': 'Oyda bir marta', 'correct': False},
                {'text': 'Yiliga bir marta', 'correct': False}
            ]
        },
        {
            'question_text': 'Haydovchilik davomida ovqat iste\'mol qilish mumkinmi?',
            'answers': [
                {'text': 'Xavfli, tavsiya etilmaydi', 'correct': True},
                {'text': 'Ha, mumkin', 'correct': False},
                {'text': 'Faqat sekin harakatlda', 'correct': False},
                {'text': 'Faqat svetaforlarda', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobildan tushayotganda nimaga e\'tibor berish kerak?',
            'answers': [
                {'text': 'Orqadan kelayotgan transport', 'correct': True},
                {'text': 'Oldinga e\'tibor berish', 'correct': False},
                {'text': 'Hech narsaga', 'correct': False},
                {'text': 'Faqat kalitni olish', 'correct': False}
            ]
        },
        {
            'question_text': 'Stress holatida haydash tavsiya etiladimi?',
            'answers': [
                {'text': 'Yo\'q, xavfli', 'correct': True},
                {'text': 'Ha, oddiy holat', 'correct': False},
                {'text': 'Faqat qisqa masofada', 'correct': False},
                {'text': 'Muhim emas', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobil old oynasi tozami?',
            'answers': [
                {'text': 'Ha, har doim toza bo\'lishi kerak', 'correct': True},
                {'text': 'Muhim emas', 'correct': False},
                {'text': 'Ba\'zida tozalash yetadi', 'correct': False},
                {'text': 'Faqat yomg\'irdan keyin', 'correct': False}
            ]
        },
        {
            'question_text': 'Yo\'l chetidagi bolalar oldidan o\'tayotganda nima qilish kerak?',
            'answers': [
                {'text': 'Tezlikni sezilarli kamaytirish', 'correct': True},
                {'text': 'Signal berib o\'tish', 'correct': False},
                {'text': 'Oddiy tezlikda davom etish', 'correct': False},
                {'text': 'Tezlikni oshirish', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobil o\'rindiqlarini to\'g\'ri sozlash muhimmi?',
            'answers': [
                {'text': 'Juda muhim, xavfsizlik uchun', 'correct': True},
                {'text': 'Muhim emas', 'correct': False},
                {'text': 'Faqat uzun safarlarda', 'correct': False},
                {'text': 'Faqat qulaylik uchun', 'correct': False}
            ]
        },
        {
            'question_text': 'Tirbandlikda qanday harakat qilish kerak?',
            'answers': [
                {'text': 'Sabr-toqatli va xotirjam', 'correct': True},
                {'text': 'Tez-tez qator almashtirish', 'correct': False},
                {'text': 'Signal berib o\'tish', 'correct': False},
                {'text': 'Yonboshdan o\'tish', 'correct': False}
            ]
        },
        {
            'question_text': 'Mashina ichida musiqa baland ovozda tinglash mumkinmi?',
            'answers': [
                {'text': 'Yo\'q, diqqatni chalg\'itadi', 'correct': True},
                {'text': 'Ha, mumkin', 'correct': False},
                {'text': 'Faqat sevimli qo\'shiqlar', 'correct': False},
                {'text': 'Faqat yo\'lda emas', 'correct': False}
            ]
        },
        {
            'question_text': 'Yo\'lda xavfli hodisa ko\'rsangiz nima qilasiz?',
            'answers': [
                {'text': 'Tegishli xizmatlarga xabar berish', 'correct': True},
                {'text': 'O\'tib ketish', 'correct': False},
                {'text': 'Suratga olish', 'correct': False},
                {'text': 'Hech narsa qilmaslik', 'correct': False}
            ]
        }
    ]
    
    create_questions_for_category(category, questions_data)

def add_emergency_questions():
    """Favqulodda vaziyatlar uchun 20 ta savol"""
    category = Category.objects.filter(name_uz='Favqulodda vaziyatlar').first()
    if not category:
        return
    
    questions_data = [
        {
            'question_text': 'Avtohalokatda birinchi nima qilish kerak?',
            'answers': [
                {'text': 'Jarohatlanganlarga yordam berish', 'correct': True},
                {'text': 'Politsiyaga qo\'ng\'iroq', 'correct': False},
                {'text': 'Suratga olish', 'correct': False},
                {'text': 'Hodisa joyini tark etish', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobil yo\'lda buzilsa nimani birinchi qo\'yish kerak?',
            'answers': [
                {'text': 'Favqulodda to\'xtash belgisini', 'correct': True},
                {'text': 'Telefon raqamini', 'correct': False},
                {'text': 'Yordam so\'rash yozuvini', 'correct': False},
                {'text': 'Hech narsani', 'correct': False}
            ]
        },
        {
            'question_text': 'Tez yordam chaqirish uchun qaysi raqam?',
            'answers': [
                {'text': '103', 'correct': True},
                {'text': '101', 'correct': False},
                {'text': '102', 'correct': False},
                {'text': '104', 'correct': False}
            ]
        },
        {
            'question_text': 'Yong\'in xizmati raqami qaysi?',
            'answers': [
                {'text': '101', 'correct': True},
                {'text': '102', 'correct': False},
                {'text': '103', 'correct': False},
                {'text': '104', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobil yonib ketsa nima qilish kerak?',
            'answers': [
                {'text': 'O\'t o\'chiruvchi vosita bilan o\'chirish', 'correct': True},
                {'text': 'Suv quyish', 'correct': False},
                {'text': 'Kutib turish', 'correct': False},
                {'text': 'Qochish', 'correct': False}
            ]
        },
        {
            'question_text': 'Yo\'lda qon ketayotgan odamni ko\'rsangiz?',
            'answers': [
                {'text': 'Qonni to\'xtatishga harakat qilish', 'correct': True},
                {'text': 'O\'tib ketish', 'correct': False},
                {'text': 'Faqat qo\'ng\'iroq qilish', 'correct': False},
                {'text': 'Kutib turish', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobil fary ishlamay qolsa?',
            'answers': [
                {'text': 'Favqulodda signal yoqish', 'correct': True},
                {'text': 'Oddiy davom etish', 'correct': False},
                {'text': 'Tezlikni oshirish', 'correct': False},
                {'text': 'To\'xtab qolish', 'correct': False}
            ]
        },
        {
            'question_text': 'Shina portlasa nima qilish kerak?',
            'answers': [
                {'text': 'Sekin to\'xtash, rulni mahkam ushlab turish', 'correct': True},
                {'text': 'Keskin tormoz bosish', 'correct': False},
                {'text': 'Rulni keskin burash', 'correct': False},
                {'text': 'Davom etish', 'correct': False}
            ]
        },
        {
            'question_text': 'Tormoz ishlamasa qanday to\'xtash mumkin?',
            'answers': [
                {'text': 'Qo\'l tormozi va motor tormozi', 'correct': True},
                {'text': 'Rulni burish', 'correct': False},
                {'text': 'Gaz berish', 'correct': False},
                {'text': 'Svetaforda kutish', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtohalokatdan keyin hodisa joyini tark etish mumkinmi?',
            'answers': [
                {'text': 'Yo\'q, ruxsatsiz', 'correct': True},
                {'text': 'Ha, darhol ketish kerak', 'correct': False},
                {'text': 'Agar kichik halokat bo\'lsa', 'correct': False},
                {'text': 'Politsiya kelgandan keyin', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobildan benzin hidi kelsa?',
            'answers': [
                {'text': 'Darhol to\'xtab tekshirish', 'correct': True},
                {'text': 'Davom etish', 'correct': False},
                {'text': 'Oynalarni ochish', 'correct': False},
                {'text': 'Chekish', 'correct': False}
            ]
        },
        {
            'question_text': 'Qish sharoitida avtomobil sirpanib ketsa?',
            'answers': [
                {'text': 'Rulni sirpanish yo\'nalishiga burish', 'correct': True},
                {'text': 'Keskin tormoz bosish', 'correct': False},
                {'text': 'Gaz berish', 'correct': False},
                {'text': 'Qo\'lni ruldan olish', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtohalokatda ikkinchi avtomobil haydovchisi bilan nima qilish kerak?',
            'answers': [
                {'text': 'Tinchlik bilan gaplashish', 'correct': True},
                {'text': 'Janjal qilish', 'correct': False},
                {'text': 'Aybdor deb ayblash', 'correct': False},
                {'text': 'Gapirmaslik', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobildan chiqib bo\'lmasa nima qilish kerak?',
            'answers': [
                {'text': 'Signal berish, yordam chaqirish', 'correct': True},
                {'text': 'Kutib turish', 'correct': False},
                {'text': 'Uyqulab qolish', 'correct': False},
                {'text': 'Hech nima qilmaslik', 'correct': False}
            ]
        },
        {
            'question_text': 'Yo\'l politsiyasi raqami?',
            'answers': [
                {'text': '102', 'correct': True},
                {'text': '101', 'correct': False},
                {'text': '103', 'correct': False},
                {'text': '104', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtohalokatda dalillar yo\'qolmasligi uchun nima qilish kerak?',
            'answers': [
                {'text': 'Suratga olish', 'correct': True},
                {'text': 'Hech narsa qilmaslik', 'correct': False},
                {'text': 'Tozalab tashlash', 'correct': False},
                {'text': 'Hodisa joyini o\'zgartirish', 'correct': False}
            ]
        },
        {
            'question_text': 'Avtomobil suvga tushib ketsa?',
            'answers': [
                {'text': 'Tezda chiqish, oynalarni sindjrish', 'correct': True},
                {'text': 'Kutib turish', 'correct': False},
                {'text': 'Eshiklarni ochishga urinish', 'correct': False},
                {'text': 'Yordam kutish', 'correct': False}
            ]
        },
        {
            'question_text': 'Boshqa odamga avtohalokatda yordam berish majburiyatimi?',
            'answers': [
                {'text': 'Ha, agar xavf yo\'q bo\'lsa', 'correct': True},
                {'text': 'Yo\'q', 'correct': False},
                {'text': 'Faqat tanishga', 'correct': False},
                {'text': 'Faqat pullik', 'correct': False}
            ]
        },
        {
            'question_text': 'Halokatda shuhudlar kerakmi?',
            'answers': [
                {'text': 'Ha, juda muhim', 'correct': True},
                {'text': 'Yo\'q', 'correct': False},
                {'text': 'Faqat katta halokatda', 'correct': False},
                {'text': 'Faqat politsiya so\'rasa', 'correct': False}
            ]
        },
        {
            'question_text': 'Favqulodda to\'xtash belgisini qancha masofaga qo\'yish kerak?',
            'answers': [
                {'text': '50-100 metr masofaga', 'correct': True},
                {'text': '10 metr masofaga', 'correct': False},
                {'text': '200 metr masofaga', 'correct': False},
                {'text': 'Avtomobil yoniga', 'correct': False}
            ]
        }
    ]
    
    create_questions_for_category(category, questions_data)

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
    print("Har bir kategoriya uchun 20 tadan savol qo'shilmoqda...\n")
    
    add_traffic_rules_questions()
    print(f"Yo'lda harakat qoidalari: {Question.objects.filter(category__name_uz='Yo\'lda harakat qoidalari').count()} ta savol")
    
    add_road_signs_questions()
    print(f"Yo'l belgilari: {Question.objects.filter(category__name_uz='Yo\'l belgilari').count()} ta savol")
    
    add_traffic_lights_questions()
    print(f"Svetafor: {Question.objects.filter(category__name_uz='Svetafor').count()} ta savol")
    
    add_safe_driving_questions()
    print(f"Xavfsiz haydash: {Question.objects.filter(category__name_uz='Xavfsiz haydash').count()} ta savol")
    
    add_emergency_questions()
    print(f"Favqulodda vaziyatlar: {Question.objects.filter(category__name_uz='Favqulodda vaziyatlar').count()} ta savol")
    
    print(f"\nUmumiy statistika:")
    print(f"Kategoriyalar: {Category.objects.count()}")
    print(f"Jami savollar: {Question.objects.count()}")
    print(f"Jami javoblar: {Answer.objects.count()}")

if __name__ == '__main__':
    main()