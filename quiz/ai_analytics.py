import google.generativeai as genai
import json
from django.conf import settings
from .models import UserAnswer, TestResult, Question, Category

class AIAnalytics:
    def __init__(self):
        # API key from settings
        self.api_key = settings.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
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
            return {
                'ai_analysis': f"AI tahlil xizmatida xatolik yuz berdi. Iltimos keyinroq urinib ko'ring. Xato: {str(e)}",
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


def get_ai_insights_for_user(user):
    """Foydalanuvchi uchun AI tahlilini olish - asosiy funksiya"""
    analytics = AIAnalytics()
    return analytics.analyze_user_performance(user)