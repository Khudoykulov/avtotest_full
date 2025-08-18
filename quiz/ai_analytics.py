import google.generativeai as genai
import json
from django.conf import settings
from .models import UserAnswer, TestResult, Question, Category

class AIAnalytics:
    def __init__(self):
        # API key from settings
        self.api_key = settings.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_user_performance(self, user):
        """Foydalanuvchining barcha xatolarini tahlil qilib, AI maslahatlari berish"""
        
        # Foydalanuvchining barcha test natijalarini olish
        test_results = TestResult.objects.filter(user=user).order_by('-created_at')
        
        if not test_results.exists():
            return {
                'ai_analysis': "Hali test topshirmagan foydalanuvchi. Birinchi testingizni topshiring!",
                'recommendations': [],
                'confidence': 0
            }
        
        # Xato javoblarni yig'ish
        wrong_answers = UserAnswer.objects.filter(
            test_result__in=test_results,
            is_correct=False
        ).select_related('question', 'question__category', 'selected_answer')
        
        # Ma'lumotlarni tayyorlash
        analysis_data = self._prepare_analysis_data(user, test_results, wrong_answers)
        
        # Gemini AI dan tahlil so'rash
        ai_response = self._get_ai_analysis(analysis_data)
        
        return ai_response
    
    def _prepare_analysis_data(self, user, test_results, wrong_answers):
        """AI uchun ma'lumotlarni tayyorlash"""
        
        # Umumiy statistika
        total_tests = test_results.count()
        avg_score = sum(result.score for result in test_results) / total_tests
        total_questions = sum(result.total_questions for result in test_results)
        total_wrong = wrong_answers.count()
        
        # Kategoriya bo'yicha xatolar
        category_errors = {}
        for answer in wrong_answers:
            category = answer.question.category.name_uz
            if category not in category_errors:
                category_errors[category] = {
                    'count': 0,
                    'questions': []
                }
            category_errors[category]['count'] += 1
            category_errors[category]['questions'].append({
                'question': answer.question.question_text,
                'selected_answer': answer.selected_answer.answer_text,
                'correct_answer': answer.question.answers.filter(is_correct=True).first().answer_text
            })
        
        # Eng ko'p xato qilingan kategoriyalar
        worst_categories = sorted(
            category_errors.items(), 
            key=lambda x: x[1]['count'], 
            reverse=True
        )[:3]
        
        # So'nggi testlardagi o'zgarish
        recent_performance = []
        if total_tests >= 3:
            recent_tests = test_results[:3]
            for test in recent_tests:
                recent_performance.append({
                    'score': test.score,
                    'total': test.total_questions,
                    'date': test.created_at.strftime('%Y-%m-%d'),
                    'category': test.category.name_uz if test.category else 'Umumiy'
                })
        
        return {
            'user_info': {
                'username': user.username,
                'total_tests': total_tests,
                'avg_score': round(avg_score, 1),
                'total_questions': total_questions,
                'total_wrong': total_wrong,
                'accuracy_percentage': round((total_questions - total_wrong) / total_questions * 100, 1) if total_questions > 0 else 0
            },
            'category_errors': dict(worst_categories),
            'recent_performance': recent_performance,
            'improvement_needed': total_wrong > total_questions * 0.3  # 30% dan ko'p xato
        }
    
    def _get_ai_analysis(self, data):
        """Gemini AI dan tahlil olish"""
        
        prompt = f"""
Siz haydash yo'l qoidalari bo'yicha ekspert va o'qituvchi sifatida ishlaysiz. 
Quyidagi foydalanuvchi ma'lumotlarini tahlil qiling va uzbek tilida batafsil maslahat bering:

FOYDALANUVCHI STATISTIKASI:
- Foydalanuvchi: {data['user_info']['username']}
- Jami testlar: {data['user_info']['total_tests']}
- O'rtacha ball: {data['user_info']['avg_score']}/20
- Jami savollar: {data['user_info']['total_questions']}
- Xato javoblar: {data['user_info']['total_wrong']}
- Aniqlik darajasi: {data['user_info']['accuracy_percentage']}%

ENG KO'P XATO QILINGAN MAVZULAR:
{json.dumps(data['category_errors'], ensure_ascii=False, indent=2)}

SO'NGGI TESTLAR NATIJALARI:
{json.dumps(data['recent_performance'], ensure_ascii=False, indent=2)}

VAZIFANGIZ:
1. Foydalanuvchining umumiy holatini baholang
2. Eng zaif tomonlarini aniqlang
3. Xato qilingan mavzular bo'yicha aniq maslahatlar bering
4. Qaysi mavzularni takrorlash kerakligini aytib bering
5. Keyingi testlarga qanday tayyorlanish kerakligini tushuntiring
6. Motivatsion so'zlar bilan yakunlang

Javobingiz aniq, foydali va o'zbek tilida bo'lsin. Har bir maslahat amaliy bo'lishi kerak.
"""

        try:
            response = self.model.generate_content(prompt)
            ai_analysis = response.text
            
            # Tavsiyalar ro'yxatini yaratish
            recommendations = self._extract_recommendations(ai_analysis, data)
            
            # Ishonch darajasini hisoblash
            confidence = self._calculate_confidence(data)
            
            return {
                'ai_analysis': ai_analysis,
                'recommendations': recommendations,
                'confidence': confidence,
                'data_used': data
            }
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                ai_message = "AI xizmati hozircha ishlamayapti (quota tugagan). Keyinroq urinib ko'ring."
            elif "404" in error_msg or "not found" in error_msg.lower():
                ai_message = "AI xizmati hozircha ishlamayapti (model topilmadi). Keyinroq urinib ko'ring."
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                ai_message = "Internet aloqasida muammo. Iltimos tarmoq ulanishini tekshiring."
            else:
                ai_message = "AI tahlil xizmati hozircha ishlamayapti. Keyinroq urinib ko'ring."
            
            return {
                'ai_analysis': ai_message,
                'recommendations': [],
                'confidence': 0
            }
    
    def _extract_recommendations(self, ai_text, data):
        """AI javobidan aniq tavsiyalarni ajratib olish"""
        recommendations = []
        
        # Zaif kategoriyalar uchun tavsiyalar
        for category, error_data in data['category_errors'].items():
            if error_data['count'] > 2:  # 2 tadan ko'p xato
                recommendations.append({
                    'type': 'category_focus',
                    'title': f"{category} mavzusini takrorlang",
                    'description': f"{error_data['count']} ta xato aniqlandi",
                    'priority': 'high' if error_data['count'] > 5 else 'medium',
                    'action_url': f'/quiz/education/?category={category}',
                    'icon': '📚'
                })
        
        # Umumiy maslahatlar
        accuracy = data['user_info']['accuracy_percentage']
        if accuracy < 60:
            recommendations.append({
                'type': 'study_more',
                'title': 'Asosiy qoidalarni o\'rganing',
                'description': 'Bilim darajangiz past. Nazariy materiallarni takrorlang',
                'priority': 'urgent',
                'action_url': '/quiz/education/',
                'icon': '⚠️'
            })
        elif accuracy < 80:
            recommendations.append({
                'type': 'practice_more',
                'title': 'Ko\'proq test topshiring',
                'description': 'Yaxshi, lekin ko\'proq amaliyot kerak',
                'priority': 'medium',
                'action_url': '/quiz/categories/',
                'icon': '💪'
            })
        else:
            recommendations.append({
                'type': 'maintain',
                'title': 'Ajoyib natija!',
                'description': 'Bilimlaringizni saqlab qoling',
                'priority': 'low',
                'action_url': '/quiz/categories/',
                'icon': '🏆'
            })
        
        return recommendations[:5]  # Maksimal 5 ta tavsiya
    
    def _calculate_confidence(self, data):
        """AI tahlilining ishonch darajasini hisoblash"""
        confidence = 50  # Boshlang'ich
        
        # Test soni bo'yicha
        if data['user_info']['total_tests'] > 10:
            confidence += 20
        elif data['user_info']['total_tests'] > 5:
            confidence += 10
        
        # Savollar soni bo'yicha
        if data['user_info']['total_questions'] > 100:
            confidence += 20
        elif data['user_info']['total_questions'] > 50:
            confidence += 10
        
        # Xatolar bo'yicha ma'lumot
        if data['user_info']['total_wrong'] > 20:
            confidence += 10
        
        return min(confidence, 95)  # Maksimal 95%
    
    def analyze_single_test(self, test_result):
        """Bitta test natijasini tahlil qilish"""
        
        # Test ma'lumotlarini olish
        wrong_answers = UserAnswer.objects.filter(
            test_result=test_result,
            is_correct=False
        ).select_related('question', 'question__category', 'selected_answer')
        
        correct_answers = UserAnswer.objects.filter(
            test_result=test_result,
            is_correct=True
        ).count()
        
        # Ma'lumotlarni tayyorlash
        single_test_data = self._prepare_single_test_data(test_result, wrong_answers, correct_answers)
        
        # AI tahlilini olish
        ai_response = self._get_single_test_ai_analysis(single_test_data)
        
        return ai_response
    
    def _prepare_single_test_data(self, test_result, wrong_answers, correct_answers):
        """Bitta test uchun ma'lumotlarni tayyorlash"""
        
        # Test asosiy ma'lumotlari
        test_info = {
            'test_type': test_result.get_test_type_display(),
            'category': test_result.category.name_uz if test_result.category else 'Umumiy test',
            'ticket_number': test_result.ticket.ticket_number if test_result.ticket else None,
            'score': test_result.score,
            'total_questions': test_result.total_questions,
            'time_taken': str(test_result.time_taken),
            'passed': test_result.passed,
            'date': test_result.created_at.strftime('%Y-%m-%d %H:%M')
        }
        
        # Xato javoblar
        wrong_details = []
        category_errors = {}
        
        for answer in wrong_answers:
            category = answer.question.category.name_uz
            wrong_detail = {
                'question': answer.question.question_text,
                'selected_answer': answer.selected_answer.answer_text,
                'correct_answer': answer.question.answers.filter(is_correct=True).first().answer_text,
                'explanation': answer.question.explanation if answer.question.explanation else '',
                'category': category
            }
            wrong_details.append(wrong_detail)
            
            # Kategoriya bo'yicha xatolarni sanash
            if category not in category_errors:
                category_errors[category] = 0
            category_errors[category] += 1
        
        return {
            'test_info': test_info,
            'wrong_answers': wrong_details,
            'category_errors': category_errors,
            'correct_count': correct_answers,
            'wrong_count': len(wrong_details),
            'accuracy_percentage': round((correct_answers / test_result.total_questions) * 100, 1) if test_result.total_questions > 0 else 0
        }
    
    def _get_single_test_ai_analysis(self, data):
        """Bitta test uchun AI tahlilini olish"""
        
        test_info = data['test_info']
        wrong_answers = data['wrong_answers']
        
        prompt = f"""
Siz haydash yo'l qoidalari bo'yicha ekspert va o'qituvchi sifatida ishlaysiz.
Quyidagi bitta test natijasini batafsil tahlil qiling va o'zbek tilida aniq maslahat bering:

TEST MA'LUMOTLARI:
- Test turi: {test_info['test_type']}
- Kategoriya: {test_info['category']}
- Natija: {test_info['score']}/{test_info['total_questions']}
- Vaqt: {test_info['time_taken']}
- Holati: {"O'tdi" if test_info['passed'] else "O'tmadi"}
- Sana: {test_info['date']}
- Aniqlik: {data['accuracy_percentage']}%

XATO QILINGAN SAVOLLAR ({data['wrong_count']} ta):
{json.dumps(wrong_answers, ensure_ascii=False, indent=2)}

KATEGORIYA BO'YICHA XATOLAR:
{json.dumps(data['category_errors'], ensure_ascii=False, indent=2)}

VAZIFANGIZ:
1. Ushbu test natijasini batafsil baholang
2. Har bir xato qilingan savolni tahlil qiling
3. Nima uchun xato qilganini tushuntiring
4. Qaysi mavzularni takrorlash kerakligini aniq ko'rsating
5. Keyingi testga qanday tayyorlanish kerakligini aytib bering
6. Agar test yaxshi o'tgan bo'lsa, motivatsion so'zlar bilan yakunlang

Javobingiz aniq, batafsil va o'zbek tilida bo'lsin. Har bir xato uchun aniq tushuncha bering.
"""

        try:
            response = self.model.generate_content(prompt)
            ai_analysis = response.text
            
            # Tavsiyalar yaratish
            recommendations = self._extract_single_test_recommendations(data)
            
            # Ishonch darajasi
            confidence = 85 if data['wrong_count'] > 0 else 70
            
            return {
                'ai_analysis': ai_analysis,
                'recommendations': recommendations,
                'confidence': confidence,
                'test_specific': True,
                'data_used': data
            }
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                ai_message = "AI xizmati hozircha ishlamayapti (quota tugagan). Keyinroq urinib ko'ring."
            elif "404" in error_msg or "not found" in error_msg.lower():
                ai_message = "AI xizmati hozircha ishlamayapti (model topilmadi). Keyinroq urinib ko'ring."
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                ai_message = "Internet aloqasida muammo. Iltimos tarmoq ulanishini tekshiring."
            else:
                ai_message = "AI tahlil xizmati hozircha ishlamayapti. Keyinroq urinib ko'ring."
                
            return {
                'ai_analysis': ai_message,
                'recommendations': [],
                'confidence': 0,
                'test_specific': True
            }
    
    def _extract_single_test_recommendations(self, data):
        """Bitta test uchun tavsiyalar"""
        recommendations = []
        
        # Test natijasiga qarab
        if data['accuracy_percentage'] < 60:
            recommendations.append({
                'type': 'urgent_study',
                'title': 'Shoshilinch takrorlash kerak!',
                'description': f"{data['wrong_count']} ta xato. Asosiy mavzularni qayta o'rganing",
                'priority': 'urgent',
                'action_url': '/quiz/education/',
                'icon': '🚨'
            })
        elif data['accuracy_percentage'] < 85:
            recommendations.append({
                'type': 'more_practice',
                'title': 'Ko\'proq amaliyot qiling',
                'description': 'Yaxshi natija, lekin yanada yaxshilash mumkin',
                'priority': 'medium',
                'action_url': '/quiz/categories/',
                'icon': '📈'
            })
        else:
            recommendations.append({
                'type': 'excellent',
                'title': 'Ajoyib natija!',
                'description': 'Davom eting va yangi mavzularni o\'rganing',
                'priority': 'low',
                'action_url': '/quiz/categories/',
                'icon': '🏆'
            })
        
        # Eng ko'p xato qilingan kategoriya uchun
        if data['category_errors']:
            worst_category = max(data['category_errors'].items(), key=lambda x: x[1])
            recommendations.append({
                'type': 'category_focus',
                'title': f"{worst_category[0]} mavzusini takrorlang",
                'description': f"{worst_category[1]} ta xato aniqlandi",
                'priority': 'high',
                'action_url': f'/quiz/education/?category={worst_category[0]}',
                'icon': '📚'
            })
        
        return recommendations[:3]


def get_ai_insights_for_user(user):
    """Foydalanuvchi uchun AI tahlilini olish - asosiy funksiya"""
    analytics = AIAnalytics()
    return analytics.analyze_user_performance(user)


def get_ai_analysis_for_single_test(test_result):
    """Bitta test uchun AI tahlili"""
    analytics = AIAnalytics()
    return analytics.analyze_single_test(test_result)