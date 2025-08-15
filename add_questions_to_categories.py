import os
import sys
import django

# Django environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from quiz.models import Category, Question, Answer

def add_questions_to_fill_categories():
    """Har bir category'da kamida 20 ta savol bo'lishi uchun qo'shimcha savollar qo'shish"""
    
    # Mavjud category'larni tekshirish
    categories = Category.objects.exclude(name__in=['test'])  # test category'ni chiqarib tashlash
    
    print("Category'lar bo'yicha savol statistikasi:")
    print("=" * 50)
    
    for category in categories:
        current_count = Question.objects.filter(category=category).count()
        needed = max(0, 20 - current_count)
        print(f"{category.name_uz}: {current_count} ta (kerak: +{needed} ta)")
    
    print("=" * 50)
    print("\nQo'shimcha savollar qo'shilmoqda...\n")
    
    # Yo'l belgilari - 9 ta qo'shimcha kerak
    road_signs_cat = Category.objects.get(name_uz="Yo'l belgilari")
    road_signs_questions = [
        {
            'question': '"Tez yordam" transport vositasi uchun qanday tartib o\'rnatilgan?',
            'answers': [
                ('Barcha transport vositalari yo\'l berishi shart', True),
                ('Faqat svetoforda to\'xtashi kerak', False),
                ('Oddiy tartibda harakatlanadi', False),
                ('Faqat kechqurun ustunlik bor', False)
            ]
        },
        {
            'question': '"Avtobeka" belgisi nimani bildiradi?',
            'answers': [
                ('Avtomobillar uchun benzin quyish joyi', True),
                ('Avtomobil ta\'miri', False),
                ('Avtomobil yuvish', False),
                ('Avtomobil sotish', False)
            ]
        },
        {
            'question': '"Tunnel" belgisi qachon qo\'yiladi?',
            'answers': [
                ('Tunnel yaqinlashganda ogohlantirish uchun', True),
                ('Tunnel ichida', False),
                ('Tunnel tugagach', False),
                ('Ixtiyoriy joyda', False)
            ]
        },
        {
            'question': 'Hayvonlar o\'tish joyini bildiruvchi belgi qanday?',
            'answers': [
                ('Sariq fonda qora hayvon tasviri', True),
                ('Ko\'k fonda oq hayvon', False),
                ('Qizil fonda hayvon', False),
                ('Yashil fonda hayvon', False)
            ]
        },
        {
            'question': '"Xavfli burilish" belgisi qayerda o\'rnatiladi?',
            'answers': [
                ('Xavfli burilishdan 150-300 metr oldin', True),
                ('Burilish joyida', False),
                ('Burilishdan keyin', False),
                ('Ixtiyoriy masofada', False)
            ]
        },
        {
            'question': 'Yo\'l qurilishi ishlarini bildiruvchi belgi qanday rangda?',
            'answers': [
                ('Sariq fonda qora rasm', True),
                ('Qizil fonda oq', False),
                ('Ko\'k fonda oq', False),
                ('Yashil fonda qora', False)
            ]
        },
        {
            'question': '"Velosiped yo\'li" belgisi qaysi transport vositalariga ruxsat beradi?',
            'answers': [
                ('Faqat velosipedlarga', True),
                ('Avtomobil va velosipedlarga', False),
                ('Barcha transport vositalariga', False),
                ('Faqat mototsikllarga', False)
            ]
        },
        {
            'question': 'Maksimal balandlikni cheklovchi belgi qanday ko\'rinishda?',
            'answers': [
                ('Oq doirada qizil chiziq va balandlik raqami', True),
                ('Ko\'k doirada oq raqam', False),
                ('Sariq kvadratda raqam', False),
                ('Yashil uchburchakda raqam', False)
            ]
        },
        {
            'category': 'road_signs',
            'question': '"Yuk mashinalari harakati taqiqlanadi" belgisi qanday?',
            'answers': [
                ('Qizil doirada yuk mashinasi tasviri', True),
                ('Ko\'k doirada yuk mashinasi', False),
                ('Sariq doirada yuk mashinasi', False),
                ('Oq doirada yuk mashinasi', False)
            ]
        }
    ]
    
    # Svetofor - 15 ta qo'shimcha kerak
    traffic_light_cat = Category.objects.get(name_uz="Svetofor")
    traffic_light_questions = [
        {
            'question': 'Svetoforda sariq va qizil signal bir vaqtda yonsa nima qilish kerak?',
            'answers': [
                ('Harakatlanishga tayyorgarlik ko\'rish, lekin kutish', True),
                ('Darhol harakatlanish', False),
                ('Orqaga qaytish', False),
                ('Svetofor tuzatilgunga qadar turish', False)
            ]
        },
        {
            'question': 'Piyodalar uchun svetofor qanday ishlaydi?',
            'answers': [
                ('Yashil - o\'tish mumkin, qizil - kutish', True),
                ('Avtomobil svetofori bilan bir xil', False),
                ('Faqat ovozli signal beradi', False),
                ('Doim yashil yonadi', False)
            ]
        },
        {
            'question': 'Svetofor nazoratchisi (regulliruvshik) bo\'lsa, uning signallariga amal qilish shartmi?',
            'answers': [
                ('Ha, u svetofordan ustun turadi', True),
                ('Yo\'q, svetoforga qarash kerak', False),
                ('Ikkalasini ham e\'tiborsiz qoldirish mumkin', False),
                ('Faqat tunda amal qilish', False)
            ]
        },
        {
            'question': 'Svetoforda miltillovchi sariq signal nimani bildiradi?',
            'answers': [
                ('Ehtiyotkorlik bilan o\'tish, yo\'l belgilariga qarash', True),
                ('Tez o\'tish', False),
                ('To\'xtash', False),
                ('Orqaga qaytish', False)
            ]
        },
        {
            'question': 'Svetofor buzilgan taqdirda chorrahadda kim boshqaradi?',
            'answers': [
                ('YHX regulliruvchisi yoki yo\'l belgilari', True),
                ('Eng birinchi kelgan haydovchi', False),
                ('Hech kim boshqarmaydi', False),
                ('Faqat katta mashina haydovchisi', False)
            ]
        },
        {
            'question': 'T-simon svetoforda qanday qoidalar amal qiladi?',
            'answers': [
                ('Har yo\'nalish uchun alohida signal', True),
                ('Barcha yo\'nalishlar uchun bir xil', False),
                ('Faqat to\'g\'ri yo\'nalish uchun', False),
                ('Signal yo\'q', False)
            ]
        },
        {
            'question': 'Svetofor yonida "STOP" chizig\'i bo\'lsa, qayerda to\'xtash kerak?',
            'answers': [
                ('STOP chizig\'i oldida', True),
                ('Svetofor ostida', False),
                ('Istalgan joyda', False),
                ('Chorrahadan keyin', False)
            ]
        },
        {
            'question': 'Qizil svetoforda o\'ng tomonga burilish qachon mumkin?',
            'answers': [
                ('Alohida belgi bo\'lsa va boshqa transport yo\'q bo\'lsa', True),
                ('Doim mumkin', False),
                ('Hech qachon mumkin emas', False),
                ('Faqat tunda', False)
            ]
        },
        {
            'question': 'Svetoforda 5 sekund qolganini qanday bilish mumkin?',
            'answers': [
                ('Raqamli hisoblagich yoki ovozli signal orqali', True),
                ('Taxminiy hisob-kitob orqali', False),
                ('Boshqa mashinalarni kuzatish orqali', False),
                ('Bilish mumkin emas', False)
            ]
        },
        {
            'question': 'Svetoforda yashil signal yonayotgan paytda ham nima uchun ehtiyot bo\'lish kerak?',
            'answers': [
                ('Boshqa yo\'nalishdan qoidabuzar kelishi mumkin', True),
                ('Svetofor buzilgan bo\'lishi mumkin', False),
                ('Hech narsa uchun', False),
                ('Faqat kechqurun ehtiyot bo\'lish kerak', False)
            ]
        },
        {
            'question': 'Svetoforli chorrahada sirena ovozi eshitilsa nima qilish kerak?',
            'answers': [
                ('Tez yordam, o\'t o\'chiruvchi, politsiyaga yo\'l berish', True),
                ('Signal bermaslik', False),
                ('Tezroq o\'tib ketishga harakat qilish', False),
                ('To\'xtab kutish', False)
            ]
        },
        {
            'question': 'Svetofor signali o\'zgarishida qanday tartibda harakat qilish kerak?',
            'answers': [
                ('Avval xavfsizlikni ta\'minlash, keyin harakat', True),
                ('Darhol harakat boshlash', False),
                ('Boshqa mashinalarni kutmaslik', False),
                ('Signalni e\'tiborsiz qoldirish', False)
            ]
        },
        {
            'question': 'Kecha svetoforda ko\'rinish yomon bo\'lsa nima qilish kerak?',
            'answers': [
                ('Tezlikni kamaytirish va ehtiyotkor bo\'lish', True),
                ('Faralarni maksimal darajada yoqish', False),
                ('Tez o\'tib ketishga harakat qilish', False),
                ('Svetoforni e\'tiborsiz qoldirish', False)
            ]
        },
        {
            'question': 'Svetofor ostida to\'xtash chizig\'ini buzish qanday natija beradi?',
            'answers': [
                ('Jarime to\'lash', True),
                ('Hech qanday oqibat yo\'q', False),
                ('Faqat ogohlantirish', False),
                ('Svetofor buziladi', False)
            ]
        },
        {
            'question': 'Svetoforning qaysi rangi eng muhim hisoblanadi?',
            'answers': [
                ('Qizil - mutlaq to\'xtash', True),
                ('Yashil - tez harakat', False),
                ('Sariq - tezlikni oshirish', False),
                ('Hech qaysi rang muhim emas', False)
            ]
        }
    ]
    
    # Quvib o'tish - 16 ta qo'shimcha kerak
    overtaking_cat = Category.objects.get(name_uz="Quvib o'tish")
    overtaking_questions = [
        {
            'question': 'Quvib o\'tish uchun minimal ko\'rinish masofasi qancha bo\'lishi kerak?',
            'answers': [
                ('Kamida 100 metr', True),
                ('50 metr', False),
                ('20 metr', False),
                ('500 metr', False)
            ]
        },
        {
            'question': 'Quvib o\'tishdan oldin orqa ko\'zguda nimani tekshirish kerak?',
            'answers': [
                ('Orqadan kelayotgan transport yo\'qligini', True),
                ('Faqat oldda yo\'l bo\'shligini', False),
                ('Hech narsani tekshirish shart emas', False),
                ('Faqat tezlikni', False)
            ]
        },
        {
            'question': 'Ikki yo\'lli yo\'lda quvib o\'tish qachon xavfli?',
            'answers': [
                ('Qarama-qarshi yo\'nalishdan transport kelayotganda', True),
                ('Hech qachon xavfli emas', False),
                ('Faqat tunda', False),
                ('Faqat qishda', False)
            ]
        },
        {
            'question': 'Quvib o\'tish paytida boshqa haydovchi qarshilik ko\'rsatsa nima qilish kerak?',
            'answers': [
                ('Quvib o\'tishni to\'xtatish va o\'z joyiga qaytish', True),
                ('Majburlab o\'tish', False),
                ('Ovoz signali berib davom etish', False),
                ('Tezlikni oshirib o\'tish', False)
            ]
        },
        {
            'question': 'Yuk mashinasini quvib o\'tish qanday qiyinchilik tug\'diradi?',
            'answers': [
                ('Ko\'p vaqt va masofa kerak bo\'ladi', True),
                ('Hech qanday qiyinchilik yo\'q', False),
                ('Faqat tunda qiyin', False),
                ('Faqat kichik mashinalar uchun qiyin', False)
            ]
        },
        {
            'question': 'Mototsiklni quvib o\'tish qanchalik xavfli?',
            'answers': [
                ('Juda ehtiyotkor bo\'lish kerak, ular tez manevr qiladi', True),
                ('Xavfsiz', False),
                ('Faqat shamolda xavfli', False),
                ('Mototsikllarni quvib o\'tish mumkin emas', False)
            ]
        },
        {
            'question': 'Quvib o\'tish uchun eng maqbul tezlik qanday bo\'lishi kerak?',
            'answers': [
                ('Quvib o\'tilayotgan transport vositasidan 15-20 km/s tez', True),
                ('Maksimal tezlik', False),
                ('Bir xil tezlik', False),
                ('Sekinroq', False)
            ]
        },
        {
            'question': 'Quvib o\'tish tugagach signal qanday o\'zgartiriladi?',
            'answers': [
                ('Chap signalni o\'chirib, o\'ng signalni yoqish', True),
                ('Signalni o\'chirmaslik', False),
                ('Ikki signalni ham yoqish', False),
                ('Hech qanday signal bermaslik', False)
            ]
        },
        {
            'question': 'Tepalikda quvib o\'tish nima uchun xavfli?',
            'answers': [
                ('Qarama-qarshi yo\'nalishdan kelayotganlar ko\'rinmaydi', True),
                ('Mashina quvvati yetmaydi', False),
                ('Faqat qishda xavfli', False),
                ('Hech qanday xavf yo\'q', False)
            ]
        },
        {
            'question': 'Bir nechta mashinani ketma-ket quvib o\'tish mumkinmi?',
            'answers': [
                ('Yo\'q, birin-ketin quvib o\'tish kerak', True),
                ('Ha, bir vaqtda hammasini', False),
                ('Faqat kichik mashinalarni', False),
                ('Faqat kunduzda mumkin', False)
            ]
        },
        {
            'question': 'Quvib o\'tish paytida tez kechish uchun nima qilish mumkin?',
            'answers': [
                ('Pastroq vitesga o\'tib, tezlikni oshirish', True),
                ('Faqat gazni bosish', False),
                ('Hech narsa qilmaslik', False),
                ('Tormozlash', False)
            ]
        },
        {
            'question': 'Avtobusni quvib o\'tishda qanday ehtiyot choralari ko\'rish kerak?',
            'answers': [
                ('Yo\'lovchilar tushishi mumkinligini hisobga olish', True),
                ('Hech qanday ehtiyot chora yo\'q', False),
                ('Faqat signal berish', False),
                ('Tez o\'tib ketish', False)
            ]
        },
        {
            'question': 'Quvib o\'tish paytida weather sharoiti qanday ta\'sir qiladi?',
            'answers': [
                ('Yomon ob-havo quvib o\'tishni xavfli qiladi', True),
                ('Hech qanday ta\'sir qilmaydi', False),
                ('Faqat qor paytida', False),
                ('Faqat shamolda', False)
            ]
        },
        {
            'question': 'Quvib o\'tish uchun yo\'lning o\'ng tomonidan o\'tish mumkinmi?',
            'answers': [
                ('Yo\'q, faqat chap tomondan', True),
                ('Ha, istalgan tomondan', False),
                ('Faqat avtobuslarni', False),
                ('Faqat tunda', False)
            ]
        },
        {
            'question': 'Quvib o\'tish tugagach, masofani qanday saqlash kerak?',
            'answers': [
                ('Xavfsiz masofa saqlash', True),
                ('Iloji boricha yaqin turish', False),
                ('150 metr masofa', False),
                ('Masofa muhim emas', False)
            ]
        },
        {
            'question': 'Chorrahalarda quvib o\'tish qoidalari qanday?',
            'answers': [
                ('Chorrahalarda quvib o\'tish taqiqlanadi', True),
                ('Erkin quvib o\'tish mumkin', False),
                ('Faqat katta chorrahalarda', False),
                ('Faqat svetoforsiz chorrahalarda', False)
            ]
        }
    ]
    
    # To'xtash va turish - 16 ta qo'shimcha kerak
    parking_cat = Category.objects.get(name_uz="To'xtash va turish")
    parking_questions = [
        {
            'question': 'Ikkinchi qatorda to\'xtash qachon ruxsat etiladi?',
            'answers': [
                ('Hech qachon ruxsat etilmaydi', True),
                ('Qisqa vaqtga', False),
                ('Kechqurun', False),
                ('Dam olish kunlari', False)
            ]
        },
        {
            'question': 'Yo\'lak ajratuvchi chiziq yonida to\'xtash mumkinmi?',
            'answers': [
                ('Yo\'q, traffic harakatini buzadi', True),
                ('Ha, har doim', False),
                ('Faqat tunlari', False),
                ('Faqat 5 daqiqaga', False)
            ]
        },
        {
            'question': 'Avtobeka yaqinida necha metr masofada to\'xtash taqiq?',
            'answers': [
                ('15 metr', True),
                ('5 metr', False),
                ('25 metr', False),
                ('50 metr', False)
            ]
        },
        {
            'question': 'Burchakda to\'xtash qoidalari qanday?',
            'answers': [
                ('Burchakdan 5 metr masofada to\'xtash', True),
                ('To\'g\'ridan-to\'g\'ri burchakda', False),
                ('Burchakdan keyin', False),
                ('Qoida yo\'q', False)
            ]
        },
        {
            'question': 'Invalidlar uchun ajratilgan joyga kim to\'xtashi mumkin?',
            'answers': [
                ('Faqat invalid belgisi bor transport vositalar', True),
                ('Har kim 30 daqiqaga', False),
                ('Faqat kechqurun har kim', False),
                ('Faqat elektr avtomobillari', False)
            ]
        },
        {
            'question': 'Yo\'lda texnik nosozlik tufayli to\'xtashda nima qilish kerak?',
            'answers': [
                ('Favqulodda signal va ogohlantiruvchi uchburchak qo\'yish', True),
                ('Faqat signal yoqish', False),
                ('Hech narsa qilmaslik', False),
                ('Faqat uchburchak qo\'yish', False)
            ]
        },
        {
            'question': 'Tepalik va pastlikda to\'xtash qoidalari qanday?',
            'answers': [
                ('Qiya joyda g\'ildiraklarni bordyur tomonga burish', True),
                ('Oddiy holda qoldirish', False),
                ('Faqat qo\'l tormozini tortish', False),
                ('Hech narsa qilmaslik', False)
            ]
        },
        {
            'question': 'Kechasi to\'xtashda chiroqlar qanday bo\'lishi kerak?',
            'answers': [
                ('Gabarit chiroqlari yoniq bo\'lishi', True),
                ('Barcha chiroqlar o\'chiq', False),
                ('Faqat fara yoniq', False),
                ('Signal chiroqlari miltillashi', False)
            ]
        },
        {
            'question': 'Do\'konlar oldida to\'xtash qoidalari qanday?',
            'answers': [
                ('Belgilangan joyda va vaqt chegarasida', True),
                ('Istalgan joyda istalgan vaqt', False),
                ('Faqat harid qilayotganda', False),
                ('To\'xtash mumkin emas', False)
            ]
        },
        {
            'question': 'Transport vositasini yuvishdan keyin qayerda quritish mumkin?',
            'answers': [
                ('Maxsus belgilangan joylarda', True),
                ('Yo\'lning istalgan joyida', False),
                ('Faqat garaj ichida', False),
                ('Piyoda yo\'llarida', False)
            ]
        },
        {
            'question': 'Pochta bo\'limi yaqinida to\'xtash qoidalari qanday?',
            'answers': [
                ('Qisqa vaqtli to\'xtash ruxsat etilishi mumkin', True),
                ('Umuman taqiqlanadi', False),
                ('Faqat pochta xodimlariga', False),
                ('Faqat kechqurun', False)
            ]
        },
        {
            'question': 'Yo\'lovchi tushirish uchun to\'xtash qoidalari qanday?',
            'answers': [
                ('Trafik harakatini buzmasdan, tez amalga oshirish', True),
                ('Istalgan joyda, istalgan vaqt', False),
                ('Faqat bekatda', False),
                ('Yo\'lovchi tushirish mumkin emas', False)
            ]
        },
        {
            'question': 'Yomg\'irli havoda to\'xtash uchun qo\'shimcha ehtiyot choralari qanday?',
            'answers': [
                ('Favqulodda signal va ko\'rinadigan belgilar qo\'yish', True),
                ('Oddiy holda to\'xtash', False),
                ('Faqat quruq joyda to\'xtash', False),
                ('To\'xtashni kechiktirish', False)
            ]
        },
        {
            'question': 'Maktab hovlisi oldida to\'xtash qoidalari qanday?',
            'answers': [
                ('Bolalar xavfsizligini ta\'minlab, qisqa vaqtga', True),
                ('Umuman taqiqlanadi', False),
                ('Faqat ota-onalarga ruxsat', False),
                ('Faqat transport vositasida kutish', False)
            ]
        },
        {
            'question': 'Katta shahar markazida to\'xtash uchun qanday hujjatlar kerak?',
            'answers': [
                ('To\'xtash ruxsatnomasi yoki to\'lov', True),
                ('Hech qanday hujjat kerak emas', False),
                ('Faqat haydovchilik guvohnomasi', False),
                ('Faqat texnik passport', False)
            ]
        },
        {
            'question': 'Favqulodda xizmatlar uchun ajratilgan joyga to\'xtash mumkinmi?',
            'answers': [
                ('Yo\'q, faqat favqulodda xizmatlar uchun', True),
                ('Ha, qisqa vaqtga', False),
                ('Faqat kechqurun', False),
                ('Ha, agar boshqa joy bo\'lmasa', False)
            ]
        }
    ]
    
    # Tezlik chegarasi - 15 ta qo'shimcha kerak
    speed_limit_cat = Category.objects.get(name_uz="Tezlik chegarasi")
    speed_limit_questions = [
        {
            'question': 'Maktab, shifoxona yaqinida tezlik chegarasi qancha?',
            'answers': [
                ('30 km/soat', True),
                ('60 km/soat', False),
                ('40 km/soat', False),
                ('50 km/soat', False)
            ]
        },
        {
            'question': 'Yangi haydovchi (2 yilgacha tajriba) uchun tezlik chegarasi qanday?',
            'answers': [
                ('Umumiy chegaradan 10 km/s kam', True),
                ('Boshqalar bilan bir xil', False),
                ('20 km/s kam', False),
                ('30 km/s kam', False)
            ]
        },
        {
            'question': 'Avtomobil yo\'lida minimal tezlik chegarasi bormi?',
            'answers': [
                ('Ha, 40 km/soat', True),
                ('Yo\'q, minimal chegara yo\'q', False),
                ('30 km/soat', False),
                ('50 km/soat', False)
            ]
        },
        {
            'question': 'Tungi vaqtda shahar ichida tezlik chegarasi qanday?',
            'answers': [
                ('Kunduzgi bilan bir xil - 60 km/soat', True),
                ('40 km/soat', False),
                ('80 km/soat', False),
                ('Chegara yo\'q', False)
            ]
        },
        {
            'question': 'Yuk mashinasi uchun shahar ichidagi tezlik chegarasi qancha?',
            'answers': [
                ('60 km/soat', True),
                ('50 km/soat', False),
                ('70 km/soat', False),
                ('80 km/soat', False)
            ]
        },
        {
            'question': 'Avtobuslar uchun avtomobil yo\'lidagi tezlik qancha?',
            'answers': [
                ('90 km/soat', True),
                ('100 km/soat', False),
                ('80 km/soat', False),
                ('110 km/soat', False)
            ]
        },
        {
            'question': 'Qor va muzli havoda tezlik chegarasi qanday bo\'lishi kerak?',
            'answers': [
                ('Oddiy chegaradan 20-30% kam', True),
                ('Oddiy chegarada', False),
                ('Ko\'proq', False),
                ('Faqat 20 km/soat', False)
            ]
        },
        {
            'question': 'Tuman paytida maksimal tezlik qancha bo\'lishi kerak?',
            'answers': [
                ('Ko\'rinish masofasiga mos ravishda', True),
                ('Umumiy tezlik chegarasida', False),
                ('20 km/soat', False),
                ('To\'xtash kerak', False)
            ]
        },
        {
            'question': 'Yomg\'irda tormozlash masofasi qanday o\'zgaradi?',
            'answers': [
                ('2-3 baravar uzayadi', True),
                ('O\'zgarmaydi', False),
                ('Qisqaradi', False),
                ('Ozroq uzayadi', False)
            ]
        },
        {
            'question': 'Tezlik o\'lchagichi (spidometr) ishlamasa nima qilish kerak?',
            'answers': [
                ('Tuzatilgunga qadar ehtiyotkorlik bilan harakatlanish', True),
                ('Oddiy tezlikda ketish', False),
                ('Maksimal tezlikda ketish', False),
                ('Transport vositasini ishlatmaslik', False)
            ]
        },
        {
            'question': 'GPS navigatsiyada ko\'rsatilgan tezlik chegarasi har doim to\'g\'rimi?',
            'answers': [
                ('Yo\'q, yo\'l belgilariga qarash kerak', True),
                ('Ha, har doim to\'g\'ri', False),
                ('Faqat shahar ichida to\'g\'ri', False),
                ('Faqat avtomobil yo\'llarida to\'g\'ri', False)
            ]
        },
        {
            'question': 'Overtaking (quvib o\'tish) paytida tezlik chegarasi qanday?',
            'answers': [
                ('Umumiy chegara amal qiladi', True),
                ('15% gacha oshirish mumkin', False),
                ('Chegara bekor bo\'ladi', False),
                ('20 km/s oshirish mumkin', False)
            ]
        },
        {
            'question': 'Yo\'l-transport hodisasi sodir bo\'lsa, tezlik qanday aniqlash mumkin?',
            'answers': [
                ('Tormozlash izlari va boshqa dalillar orqali', True),
                ('Faqat guvohlar so\'zlari orqali', False),
                ('Aniqlab bo\'lmaydi', False),
                ('Faqat kamera yozuvi orqali', False)
            ]
        },
        {
            'question': 'Elektr avtomobil uchun tezlik chegarasi boshqacharmi?',
            'answers': [
                ('Yo\'q, umumiy qoidalar amal qiladi', True),
                ('Ha, 10% kam', False),
                ('Ha, 20% ko\'proq', False),
                ('Alohida qoidalari bor', False)
            ]
        },
        {
            'question': 'Tezlik chegarasini buzgani uchun jarime qancha?',
            'answers': [
                ('Buzish darajasiga qarab turlicha', True),
                ('Doim bir xil', False),
                ('Jarime yo\'q', False),
                ('Faqat ogohlantirishe', False)
            ]
        }
    ]
    
    # Favqulodda holatlar - 16 ta qo'shimcha kerak
    emergency_cat = Category.objects.get(name_uz="Favqulodda holatlar")
    emergency_questions = [
        {
            'question': 'Dvigatel ishlamay qolganda birinchi navbatda nima qilish kerak?',
            'answers': [
                ('Xavfsiz joyga tortib olib o\'tish', True),
                ('Yo\'l o\'rtasida qoldirish', False),
                ('Darhol ta\'mirlashga kirishish', False),
                ('Boshqa mashinalardan yordam so\'rash', False)
            ]
        },
        {
            'question': 'Tormoz ishlamasa, qanday favqulodda usul qo\'llash mumkin?',
            'answers': [
                ('Qo\'l tormozi, motor tormozi, xavfsiz to\'siqqa tegizish', True),
                ('Faqat signal chaqirish', False),
                ('Yo\'lovchilarni tushirish', False),
                ('Dvigatelni o\'chirish', False)
            ]
        },
        {
            'question': 'Olovli hodisada kishilarni qutqarishning to\'g\'ri tartibi qanday?',
            'answers': [
                ('Avval o\'zingizni, keyin boshqalarni qutqarish', True),
                ('Avval boshqalarni qutqarish', False),
                ('Faqat o\'t o\'chiruvchi chaqirish', False),
                ('Hech kimni qutqarmaslik', False)
            ]
        },
        {
            'question': 'Baxtsiz hodisada jarohatlangan kishini qanday ko\'chirish kerak?',
            'answers': [
                ('Umurtqa pog\'onasini buzmaslik uchun ehtiyotkorlik bilan', True),
                ('Tez va kuchli usulda', False),
                ('Ayoqlaridan ushlab', False),
                ('Ko\'chirmaslik kerak', False)
            ]
        },
        {
            'question': 'Qon ketishini to\'xtatishning eng samarali usuli qanday?',
            'answers': [
                ('Yurak ustiga bosim o\'tkazish va bint bilan bog\'lash', True),
                ('Faqat dori berish', False),
                ('Suv sepish', False),
                ('Hech narsa qilmaslik', False)
            ]
        },
        {
            'question': 'Hushini yo\'qotgan kishiga qanday yordam berish mumkin?',
            'answers': [
                ('Yon tomonga yotqizish va nafas yo\'lini tozalash', True),
                ('Ko\'p suv berish', False),
                ('Kuchli chayqash', False),
                ('Ayoqqa bosish', False)
            ]
        },
        {
            'question': 'Yonish uchun kimyoviy modda to\'kilsa nima qilish kerak?',
            'answers': [
                ('Maxsus kimyoviy o\'t o\'chiruvchi ishlatish', True),
                ('Suv sepish', False),
                ('Yoqilg\'i sepish', False),
                ('Havo sepish', False)
            ]
        },
        {
            'question': 'Elektr toki urishi holatida birinchi yordam qanday?',
            'answers': [
                ('Tok manbasini uzish, keyin tibbiy yordam', True),
                ('Darhol tibbiy yordam berish', False),
                ('Suv sepish', False),
                ('Metal buyum bilan tegish', False)
            ]
        },
        {
            'question': 'Yo\'lda hayvon paydo bo\'lsa nima qilish kerak?',
            'answers': [
                ('Tezlikni kamaytirish va ehtiyotkorlik bilan o\'tish', True),
                ('Ovoz chiqarib quvish', False),
                ('Unga qarab borish', False),
                ('To\'xtab kutish', False)
            ]
        },
        {
            'question': 'Favqulodda tez yordam chaqirishda qanday ma\'lumotlar berish kerak?',
            'answers': [
                ('Joylashuv, jarohatlar turi, qancha kishi', True),
                ('Faqat joylashuv', False),
                ('Faqat ismingiz', False),
                ('Hech qanday ma\'lumot kerak emas', False)
            ]
        },
        {
            'question': 'Qish paytida muzga tushib qolgan mashinani chiqarish usuli qanday?',
            'answers': [
                ('Qum, tuz sepish yoki maxsus zanjir ishlatish', True),
                ('Kuchli gaz berish', False),
                ('Suv quyish', False),
                ('Kutib turish', False)
            ]
        },
        {
            'question': 'Radiator qizib ketsa nima qilish kerak?',
            'answers': [
                ('Dvigatelni o\'chirib, sovishini kutish', True),
                ('Suv quyish', False),
                ('Davom etish', False),
                ('Radiator qopqog\'ini ochish', False)
            ]
        },
        {
            'question': 'Yo\'lda yolg\'iz qolgan ayol haydovchiga qanday yordam berish kerak?',
            'answers': [
                ('Ehtiyotkorlik bilan yaqinlashish va yordam taklif qilish', True),
                ('Mashinasini to\'xtatish', False),
                ('Kuchli ovoz bilan chaqirish', False),
                ('E\'tibor bermaslik', False)
            ]
        },
        {
            'question': 'Kuchli shamol paytida haydashda qanday ehtiyot choralari ko\'rish kerak?',
            'answers': [
                ('Ikkala qo\'lni rulda saqlash va tezlikni kamaytirish', True),
                ('Tezlikni oshirish', False),
                ('Derazalarni ochish', False),
                ('Signal chiroqlarini yoqish', False)
            ]
        },
        {
            'question': 'Avtomobildan chiqib bo\'lmasa (eshik ochilmasa) nima qilish kerak?',
            'answers': [
                ('Oynani sindirish uchun maxsus asbob ishlatish', True),
                ('Kuchli itarish', False),
                ('Yordam kelguncha kutish', False),
                ('Signalni bosish', False)
            ]
        },
        {
            'question': 'Baxtsiz hodisa joyida boshqa transport vositalari to\'planishining sababi nima?',
            'answers': [
                ('Qiziquvchanlik, yo\'l harakati sekinlashishi', True),
                ('Yordam berish', False),
                ('Yo\'l yopilganligi', False),
                ('Majburiylik', False)
            ]
        }
    ]
    
    # Transport vositasi texnikasi - 16 ta qo'shimcha kerak
    vehicle_tech_cat = Category.objects.get(name_uz="Transport vositasi texnikasi")
    vehicle_tech_questions = [
        {
            'question': 'Dvigatel moyining darajasini qanday tekshirish mumkin?',
            'answers': [
                ('Maxsus o\'lchagich (dipstik) bilan', True),
                ('Dvigatelni tinglash orqali', False),
                ('Rangini ko\'rish orqali', False),
                ('Hidini bilish orqali', False)
            ]
        },
        {
            'question': 'Akkumlyatorning zaryadi tugasa, qanday belgilar paydo bo\'ladi?',
            'answers': [
                ('Dvigatel qiyin ishga tushadi, chiroqlar xira yonadi', True),
                ('Hech qanday belgi yo\'q', False),
                ('Faqat ovoz o\'zgaradi', False),
                ('Faqat tez sarflanadi', False)
            ]
        },
        {
            'question': 'G\'ildiraklarning bosimi qanday tekshiriladi?',
            'answers': [
                ('Maxsus bosim o\'lchagich bilan', True),
                ('Ko\'z bilan qarash orqali', False),
                ('Oyoq bilan bosish orqali', False),
                ('Ovozga qarash orqali', False)
            ]
        },
        {
            'question': 'Tormoz suyuqligining darajasi qanday nazorat qilinadi?',
            'answers': [
                ('Maxsus idishdagi belgilar bo\'yicha', True),
                ('Pedal bosishda his qilish orqali', False),
                ('Rangi bo\'yicha', False),
                ('Hidi bo\'yicha', False)
            ]
        },
        {
            'question': 'Dvigatelning sovutish suyuqligi (antifreeze) nima uchun kerak?',
            'answers': [
                ('Dvigatelni qizishdan va muzlashdan himoya qilish', True),
                ('Faqat qishda ishlash uchun', False),
                ('Tezlikni oshirish uchun', False),
                ('Yoqilg\'ini tejash uchun', False)
            ]
        },
        {
            'question': 'Rul mashinasining suyuqlik darajasi qanday tekshiriladi?',
            'answers': [
                ('Dvigatel ishlaganda maxsus idishdagi belgi bo\'yicha', True),
                ('Dvigatel o\'chiq holda', False),
                ('Faqat harakatlanganda', False),
                ('Rangini ko\'rish orqali', False)
            ]
        },
        {
            'question': 'Chiroqlarning ishlashini qanday tekshirish kerak?',
            'answers': [
                ('Har safar yo\'lga chiqishdan oldin barcha chiroqlarni yoqib ko\'rish', True),
                ('Faqat kechqurun tekshirish', False),
                ('Hech qachon tekshirmaslik', False),
                ('Faqat qorong\'uda tekshirish', False)
            ]
        },
        {
            'question': 'Yoqilg\'i filtrini nima uchun almashtirish kerak?',
            'answers': [
                ('Yoqilg\'ini tozalab, dvigatel ishlashini yaxshilash', True),
                ('Faqat ko\'rinish uchun', False),
                ('Yoqilg\'ini tejash uchun', False),
                ('Shart emas', False)
            ]
        },
        {
            'question': 'Havo filtrining vazifasi nima?',
            'answers': [
                ('Dvigatelga kiruvchi havoni tozalash', True),
                ('Ovozni pasaytirish', False),
                ('Yoqilg\'ini filtrlas', False),
                ('Haroratni nazorat qilish', False)
            ]
        },
        {
            'question': 'Qanday hollarda texnik ko\'rikdan o\'tkazish kerak?',
            'answers': [
                ('Belgilangan muddatlarda va nosozlik aniqlanganda', True),
                ('Faqat sotishdan oldin', False),
                ('Hech qachon shart emas', False),
                ('Faqat yangi mashina sotib olganda', False)
            ]
        },
        {
            'question': 'Transport vositasining texnik holati qanday nazorat qilinadi?',
            'answers': [
                ('Muntazam tekshiruvlar va texnik ko\'rik orqali', True),
                ('Faqat politsiya tomonidan', False),
                ('Faqat sotuvchi tomonidan', False),
                ('Hech kim nazorat qilmaydi', False)
            ]
        },
        {
            'question': 'Shina protektorining minimal chuqurligi qancha?',
            'answers': [
                ('1.6 mm', True),
                ('3 mm', False),
                ('5 mm', False),
                ('0.5 mm', False)
            ]
        },
        {
            'question': 'Dvigatel qizib ketishining asosiy sabablari nima?',
            'answers': [
                ('Sovutish suyuqligi yetmasligi, radiator ifloslanishi', True),
                ('Faqat issiq havo', False),
                ('Faqat tez haydash', False),
                ('Faqat eski dvigatel', False)
            ]
        },
        {
            'question': 'Avtomobilning kamar (remen) larini qachon almashtirish kerak?',
            'answers': [
                ('Yeyilganda yoki yorilganda', True),
                ('Har yili', False),
                ('Hech qachon', False),
                ('Faqat siniq bo\'lsa', False)
            ]
        },
        {
            'question': 'Transport vositasini qishga qanday tayyorlash kerak?',
            'answers': [
                ('Qishki shinalar, antifreeze, akkumlyator tekshiruvi', True),
                ('Faqat shinalar almashtirish', False),
                ('Hech narsa qilmaslik', False),
                ('Faqat yoqilg\'i to\'ldirish', False)
            ]
        },
        {
            'question': 'G\'ildirak muvozanatini yo\'qotganda qanday belgilar paydo bo\'ladi?',
            'answers': [
                ('Rulda titroq, notekis yeyilish', True),
                ('Faqat ovoz chiqadi', False),
                ('Hech qanday belgi yo\'q', False),
                ('Faqat tezlik oshganda seziladi', False)
            ]
        }
    ]
    
    # Savollarni qo'shish
    all_additional_questions = [
        (road_signs_cat, road_signs_questions),
        (traffic_light_cat, traffic_light_questions),
        (overtaking_cat, overtaking_questions),
        (parking_cat, parking_questions),
        (speed_limit_cat, speed_limit_questions),
        (emergency_cat, emergency_questions),
        (vehicle_tech_cat, vehicle_tech_questions)
    ]
    
    total_added = 0
    for category, questions in all_additional_questions:
        print(f"\n{category.name_uz} kategoriyasiga savollar qo'shilmoqda...")
        for i, q_data in enumerate(questions, 1):
            # Savol yaratish
            question = Question.objects.create(
                category=category,
                question_text=q_data['question']
            )
            
            # Javoblar yaratish
            for answer_text, is_correct in q_data['answers']:
                Answer.objects.create(
                    question=question,
                    answer_text=answer_text,
                    is_correct=is_correct
                )
            
            total_added += 1
            print(f"  + {i}. {q_data['question'][:50]}...")
    
    print(f"\n{'='*60}")
    print(f"JAMI {total_added} ta qo'shimcha savol qo'shildi!")
    print("="*60)
    
    # Final statistika
    print("\nYAKUNIY STATISTIKA:")
    print("-" * 40)
    grand_total = 0
    for category in categories:
        current_count = Question.objects.filter(category=category).count()
        print(f"{category.name_uz}: {current_count} ta savol")
        grand_total += current_count
    
    print("-" * 40)
    print(f"JAMI BARCHA SAVOLLAR: {grand_total} ta")
    print("-" * 40)
    
    # Har category'da 20 tadan savol borligini tekshirish
    print("\n20+ SAVOL TEKSHIRUVI:")
    for category in categories:
        count = Question.objects.filter(category=category).count()
        status = "OK" if count >= 20 else "KAM"
        print(f"{status} {category.name_uz}: {count}/20")

if __name__ == '__main__':
    add_questions_to_fill_categories()