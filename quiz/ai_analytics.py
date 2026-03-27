import json
import requests
import logging
import time
from django.conf import settings
from .models import UserAnswer, TestResult, Question, Category

logger = logging.getLogger('groq_api')
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


class AIAnalytics:

    def __init__(self):
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.model_name = "llama-3.3-70b-versatile"
        self.current_config = self._get_active_config()
        self.api_key = self.current_config.api_key if self.current_config else getattr(settings, 'GROQ_API_KEY', '')

    def _get_active_config(self):
        """Ishlatish mumkin bo'lgan birinchi keyni olish"""
        from .models import APIConfig
        try:
            configs = APIConfig.objects.filter(is_active=True).order_by('priority')
            for config in configs:
                if config.is_available():
                    return config
        except Exception as e:
            logger.error(f"Config olishda xato: {e}")
        return None

    def analyze_user_performance(self, user):
        """Foydalanuvchining barcha xatolarini tahlil qilib, AI maslahatlari berish"""
        test_results = TestResult.objects.filter(user=user).order_by('-created_at')

        if not test_results.exists():
            return {
                'ai_analysis': "Hali test topshirmagan foydalanuvchi. Birinchi testingizni topshiring!",
                'recommendations': [],
                'confidence': 0
            }

        wrong_answers = UserAnswer.objects.filter(
            test_result__in=test_results,
            is_correct=False
        ).select_related('question', 'question__category', 'selected_answer')

        analysis_data = self._prepare_analysis_data(user, test_results, wrong_answers)
        ai_response = self._get_ai_analysis(analysis_data)
        return ai_response

    def _prepare_analysis_data(self, user, test_results, wrong_answers):
        """AI uchun ma'lumotlarni tayyorlash"""
        total_tests = test_results.count()
        avg_score = sum(result.score for result in test_results) / total_tests
        total_questions = sum(result.total_questions for result in test_results)
        total_wrong = wrong_answers.count()

        category_errors = {}
        for answer in wrong_answers:
            category = answer.question.category.name_uz
            if category not in category_errors:
                category_errors[category] = {'count': 0, 'questions': []}
            category_errors[category]['count'] += 1
            category_errors[category]['questions'].append({
                'question': answer.question.question_text,
                'selected_answer': answer.selected_answer.answer_text,
                'correct_answer': answer.question.answers.filter(is_correct=True).first().answer_text
            })

        worst_categories = sorted(
            category_errors.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:3]

        recent_performance = []
        if total_tests >= 3:
            for test in test_results[:3]:
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
                'accuracy_percentage': round((total_questions - total_wrong) / total_questions * 100,
                                             1) if total_questions > 0 else 0
            },
            'category_errors': dict(worst_categories),
            'recent_performance': recent_performance,
        }

    def _get_ai_analysis(self, data):
        """Umumiy tahlil uchun Groq API ga so'rov"""
        prompt = f"""
Siz haydash yo'l qoidalari bo'yicha ekspert va o'qituvchi sifatida ishlaysiz. 
Quyidagi foydalanuvchi ma'lumotlarini tahlil qiling va uzbek tilida batafsil maslahat bering:

FOYDALANUVCHI STATISTIKASI:
- Jami testlar: {data['user_info']['total_tests']}
- O'rtacha ball: {data['user_info']['avg_score']}/20
- Xato javoblar: {data['user_info']['total_wrong']}
- Aniqlik darajasi: {data['user_info']['accuracy_percentage']}%

ENG KO'P XATO QILINGAN MAVZULAR:
{json.dumps(data['category_errors'], ensure_ascii=False, indent=2)}

SO'NGGI TESTLAR:
{json.dumps(data['recent_performance'], ensure_ascii=False, indent=2)}

VAZIFANGIZ:
1. Umumiy holatni baholang
2. Zaif tomonlarni aniqlang
3. Aniq maslahatlar bering
4. Motivatsion so'zlar bilan yakunlang

Javob o'zbek tilida, aniq va foydali bo'lsin.
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 800
        }

        for attempt in range(3):
            try:
                logger.debug(f"[GROQ] So'rov yuborilmoqda... (Urinish: {attempt + 1})")
                response = requests.post(self.url, json=payload, headers=headers, timeout=120)

                if response.status_code == 200:
                    result = response.json()
                    ai_text = result["choices"][0]["message"]["content"].strip()

                    # Ishlatilgan tokenlarni saqlash
                    if self.current_config:
                        used = result.get('usage', {}).get('total_tokens', 800)
                        self.current_config.add_used_tokens(used)

                    logger.info(f"[GROQ] Muvaffaqiyat!")
                    return {'ai_analysis': ai_text, 'confidence': 95}

                elif response.status_code == 429:
                    # Rate limit — keyingi config ga o'tish
                    logger.warning(f"[GROQ] Rate limit! Keyingi keyga o'tilmoqda...")
                    self.current_config = self._get_active_config()
                    if self.current_config:
                        self.api_key = self.current_config.api_key
                    else:
                        return {'ai_analysis': "Barcha API keylar limiti tugagan. Ertaga urinib ko'ring.",
                                'confidence': 0}
                else:
                    logger.error(f"[GROQ] Xato! Status: {response.status_code}")

            except Exception as e:
                logger.error(f"[GROQ] Xato (Urinish {attempt + 1}): {str(e)}")
                if attempt < 2:
                    time.sleep(3)
                    continue

        return {'ai_analysis': "AI xizmati vaqtincha ishlamayapti.", 'confidence': 0}

    def analyze_single_test(self, test_result):
        """Bitta test natijasini tahlil qilish"""
        wrong_answers = UserAnswer.objects.filter(
            test_result=test_result,
            is_correct=False
        ).select_related('question', 'question__category', 'selected_answer')

        correct_answers = UserAnswer.objects.filter(
            test_result=test_result,
            is_correct=True
        ).count()

        single_test_data = self._prepare_single_test_data(test_result, wrong_answers, correct_answers)
        return self._get_single_test_ai_analysis(single_test_data)

    def _prepare_single_test_data(self, test_result, wrong_answers, correct_answers):
        """Bitta test uchun ma'lumotlarni tayyorlash"""
        test_info = {
            'test_type': test_result.get_test_type_display(),
            'category': test_result.category.name_uz if test_result.category else 'Umumiy test',
            'score': test_result.score,
            'total_questions': test_result.total_questions,
            'passed': test_result.passed,
            'date': test_result.created_at.strftime('%Y-%m-%d %H:%M')
        }

        wrong_details = []
        category_errors = {}

        for answer in wrong_answers:
            category = answer.question.category.name_uz
            correct = answer.question.answers.filter(is_correct=True).first()
            wrong_details.append({
                'question': answer.question.question_text,
                'selected_answer': answer.selected_answer.answer_text,
                'correct_answer': correct.answer_text if correct else '',
                'category': category
            })

            category_errors[category] = category_errors.get(category, 0) + 1

        return {
            'test_info': test_info,
            'wrong_answers': wrong_details,
            'category_errors': category_errors,
            'correct_count': correct_answers,
            'wrong_count': len(wrong_details),
            'accuracy_percentage': round((correct_answers / test_result.total_questions) * 100,
                                         1) if test_result.total_questions > 0 else 0
        }

    def _get_single_test_ai_analysis(self, data):
        """Bitta test uchun Groq API ga so'rov"""
        prompt = f"""
Siz haydash yo'l qoidalari bo'yicha ekspert va o'qituvchi sifatida ishlaysiz.
Quyidagi test natijasini tahlil qiling va o'zbek tilida maslahat bering:

TEST NATIJASI:
- Kategoriya: {data['test_info']['category']}
- Natija: {data['test_info']['score']}/{data['test_info']['total_questions']}
- Holati: {"O'tdi" if data['test_info']['passed'] else "O'tmadi"}
- Aniqlik: {data['accuracy_percentage']}%

XATO QILINGAN SAVOLLAR:
{json.dumps(data['wrong_answers'][:10], ensure_ascii=False, indent=2)}

VAZIFANGIZ:
1. Test natijasini baholang
2. Xatolarni tushuntiring
3. Qaysi mavzularni takrorlash kerakligini ayting
4. Motivatsion so'zlar bilan yakunlang

Javob o'zbek tilida bo'lsin.
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 800
        }

        for attempt in range(3):
            try:
                logger.debug(f"[GROQ SINGLE] So'rov yuborilmoqda... (Urinish: {attempt + 1})")
                response = requests.post(self.url, json=payload, headers=headers, timeout=120)

                if response.status_code == 200:
                    result = response.json()
                    ai_text = result["choices"][0]["message"]["content"].strip()

                    # Ishlatilgan tokenlarni saqlash
                    if self.current_config:
                        used = result.get('usage', {}).get('total_tokens', 800)
                        self.current_config.add_used_tokens(used)

                    recommendations = self._extract_recommendations(data)
                    return {
                        'ai_analysis': ai_text,
                        'recommendations': recommendations,
                        'confidence': 85,
                        'test_specific': True
                    }

                elif response.status_code == 429:
                    logger.warning(f"[GROQ SINGLE] Rate limit! Keyingi keyga o'tilmoqda...")
                    self.current_config = self._get_active_config()
                    if self.current_config:
                        self.api_key = self.current_config.api_key
                    else:
                        return {'ai_analysis': "Barcha API keylar limiti tugagan.", 'confidence': 0}
                else:
                    logger.error(f"[GROQ SINGLE] Xato! Status: {response.status_code}")

            except Exception as e:
                logger.error(f"[GROQ SINGLE] Xato (Urinish {attempt + 1}): {str(e)}")
                if attempt < 2:
                    time.sleep(3)
                    continue

        return {'ai_analysis': "AI xizmati vaqtincha ishlamayapti.", 'confidence': 0, 'test_specific': True}

    def _extract_recommendations(self, data):
        """Tavsiyalar yaratish"""
        recommendations = []

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
                'title': "Ko'proq amaliyot qiling",
                'description': 'Yaxshi natija, lekin yanada yaxshilash mumkin',
                'priority': 'medium',
                'action_url': '/quiz/categories/',
                'icon': '📈'
            })
        else:
            recommendations.append({
                'type': 'excellent',
                'title': 'Ajoyib natija!',
                'description': "Davom eting va yangi mavzularni o'rganing",
                'priority': 'low',
                'action_url': '/quiz/categories/',
                'icon': '🏆'
            })

        if data['category_errors']:
            worst = max(data['category_errors'].items(), key=lambda x: x[1])
            recommendations.append({
                'type': 'category_focus',
                'title': f"{worst[0]} mavzusini takrorlang",
                'description': f"{worst[1]} ta xato aniqlandi",
                'priority': 'high',
                'action_url': '/quiz/education/',
                'icon': '📚'
            })

        return recommendations[:3]


# Asosiy funksiyalar
def get_ai_insights_for_user(user):
    analytics = AIAnalytics()
    return analytics.analyze_user_performance(user)


def get_ai_analysis_for_single_test(test_result):
    analytics = AIAnalytics()
    return analytics.analyze_single_test(test_result)