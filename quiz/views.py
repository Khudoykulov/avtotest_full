from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg, Count, Q, Max
from django.db.models.functions import TruncDate
from django.db import models
from .models import Category, TestTicket, Question, TestResult, UserAnswer, EducationContent, UserProgress
from .ai_analytics import get_ai_insights_for_user
import json
from datetime import timedelta, datetime
from random import sample
import math


def home_view(request):
    """Main homepage view"""
    categories = Category.objects.all()
    recent_results = None
    if request.user.is_authenticated:
        recent_results = TestResult.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'categories': categories,
        'recent_results': recent_results,
    }
    return render(request, 'home.html', context)


def categories_view(request):
    """Display all quiz categories"""
    categories = Category.objects.annotate(
        question_count=Count('questions')
    ).all()
    return render(request, 'quiz/categories.html', {'categories': categories})


def tickets_view(request):
    """Display all test tickets"""
    tickets = TestTicket.objects.all().order_by('ticket_number')
    return render(request, 'quiz/tickets.html', {'tickets': tickets})


@login_required
def take_test_view(request, ticket_id=None, category_id=None):
    """Take a quiz test"""
    questions = []
    test_type = None
    test_name = ""

    if ticket_id:
        ticket = get_object_or_404(TestTicket, ticket_number=ticket_id)
        questions = ticket.questions.all()
        test_type = 'ticket'
        test_name = f"Bilet {ticket.ticket_number}"
    elif category_id:
        category = get_object_or_404(Category, id=category_id)
        all_questions = list(Question.objects.filter(category=category))
        # Select 20 random questions or all if less than 20
        questions = sample(all_questions, min(20, len(all_questions)))
        test_type = 'category'
        test_name = category.name_uz

    if not questions:
        return redirect('quiz:categories')

    context = {
        'questions': questions,
        'test_type': test_type,
        'test_name': test_name,
        'ticket_id': ticket_id,
        'category_id': category_id,
    }
    return render(request, 'quiz/take_test.html', context)


@login_required
def submit_test_view(request):
    """Submit test results"""
    if request.method == 'POST':
        data = json.loads(request.body)
        answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
        test_type = data.get('test_type')
        ticket_id = data.get('ticket_id')
        category_id = data.get('category_id')

        # Calculate score
        correct_answers = 0
        total_questions = len(answers)

        # Create test result
        ticket_obj = None
        category_obj = None
        
        if test_type == 'ticket' and ticket_id:
            try:
                ticket_obj = TestTicket.objects.get(ticket_number=ticket_id)
            except TestTicket.DoesNotExist:
                pass
        elif test_type == 'category' and category_id:
            try:
                category_obj = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        
        # Test turini aniqlash
        test_type_value = 'general'
        variant_id_value = None
        
        if test_type == 'ticket':
            test_type_value = 'ticket'
        elif test_type == 'category':
            test_type_value = 'category'
        elif test_type == 'general':
            test_type_value = 'general'
            variant_id_value = data.get('variant_id')
        
        # Agar avval shu test ishlatilgan bo'lsa, yangi natija yaratish o'rniga yangisini yangilash
        existing_result = None
        if test_type_value == 'general' and variant_id_value:
            # Umumiy test uchun variant bo'yicha tekshirish
            existing_result = TestResult.objects.filter(
                user=request.user,
                test_type='general',
                variant_id=variant_id_value
            ).first()
        elif test_type_value == 'ticket' and ticket_obj:
            # Bilet testi uchun
            existing_result = TestResult.objects.filter(
                user=request.user,
                ticket=ticket_obj,
                test_type='ticket'
            ).first()
        elif test_type_value == 'category' and category_obj:
            # Kategoriya testi uchun - eng oxirgi natijani yangilash
            existing_result = TestResult.objects.filter(
                user=request.user,
                category=category_obj,
                test_type='category'
            ).order_by('-created_at').first()
        
        if existing_result:
            # Mavjud natijani yangilash
            test_result = existing_result
            test_result.total_questions = total_questions
            test_result.time_taken = timedelta(seconds=time_taken)
            # score va passed keyinroq yangilanadi
            
            # Eski javoblarni o'chirish
            UserAnswer.objects.filter(test_result=test_result).delete()
        else:
            # Yangi natija yaratish
            test_result = TestResult.objects.create(
                user=request.user,
                ticket=ticket_obj,
                category=category_obj,
                test_type=test_type_value,
                variant_id=variant_id_value,
                score=0,  # Will update after calculating
                total_questions=total_questions,
                time_taken=timedelta(seconds=time_taken),
                passed=False  # Will update after calculating
            )

        # Process each answer
        for question_id, answer_id in answers.items():
            question = Question.objects.get(id=question_id)
            selected_answer = question.answers.get(id=answer_id)
            is_correct = selected_answer.is_correct

            if is_correct:
                correct_answers += 1

            UserAnswer.objects.create(
                test_result=test_result,
                question=question,
                selected_answer=selected_answer,
                is_correct=is_correct
            )

        # Update test result
        test_result.score = correct_answers
        pass_threshold = 18  # 18/20 = 90% to pass
        test_result.passed = correct_answers >= pass_threshold
        test_result.save()
        

        # Update user stats
        user = request.user
        user.total_tests_taken += 1
        if correct_answers > user.best_score:
            user.best_score = correct_answers
        user.save()

        return JsonResponse({
            'success': True,
            'score': correct_answers,
            'total': total_questions,
            'passed': test_result.passed,
            'result_id': test_result.id
        })

    return JsonResponse({'success': False})


@login_required
def statistics_view(request):
    """Enhanced user statistics dashboard with detailed analytics"""
    user_results = TestResult.objects.filter(user=request.user).order_by('-created_at')

    # Basic statistics
    total_tests = user_results.count()
    passed_tests = user_results.filter(passed=True).count()
    average_score = user_results.aggregate(Avg('score'))['score__avg'] or 0
    best_score = request.user.best_score
    

    # Recent results (last 10)
    recent_results = user_results[:10]

    # Performance over time (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_performance = user_results.filter(
        created_at__gte=thirty_days_ago
    ).annotate(
        created_at_date=TruncDate('created_at')
    ).values('created_at_date').annotate(
        avg_score=Avg('score'),
        test_count=Count('id')
    ).order_by('created_at_date')

    # Category performance analysis
    category_stats = {}
    for category in Category.objects.all():
        category_results = user_results.filter(category=category)
        if category_results.exists():
            category_avg = category_results.aggregate(Avg('score'))['score__avg']
            category_best = category_results.aggregate(Max('score'))['score__max']
            category_stats[category.name_uz] = {
                'total': category_results.count(),
                'average': round(category_avg, 1),
                'best': category_best,
                'passed': category_results.filter(passed=True).count(),
                'improvement_trend': calculate_improvement_trend(category_results)
            }

    # Weekly performance analysis
    weekly_stats = calculate_weekly_performance(user_results)

    # Difficulty analysis - which questions are hardest
    difficult_questions = analyze_difficult_questions(request.user)

    # Time analysis - average time per test
    time_stats = calculate_time_statistics(user_results)

    # Comparison with other users (anonymized)
    user_ranking = calculate_user_ranking(request.user)

    stats = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'average_score': round(average_score, 1),
        'best_score': best_score,
        'recent_results': recent_results,
        'pass_rate': round((passed_tests / total_tests * 100) if total_tests > 0 else 0, 1),
        'recent_performance': list(recent_performance),
        'weekly_stats': weekly_stats,
        'difficult_questions': difficult_questions,
        'time_stats': time_stats,
        'user_ranking': user_ranking,
        'improvement_suggestions': generate_improvement_suggestions(user_results, category_stats)
    }

    context = {
        'stats': stats,
        'category_stats': category_stats,
    }
    return render(request, 'quiz/statistics.html', context)


def calculate_improvement_trend(results):
    """Calculate if user is improving in a category"""
    if results.count() < 3:
        return 'insufficient_data'

    recent_half = results[:results.count() // 2]
    older_half = results[results.count() // 2:]

    recent_avg = recent_half.aggregate(Avg('score'))['score__avg'] or 0
    older_avg = older_half.aggregate(Avg('score'))['score__avg'] or 0

    if recent_avg > older_avg + 1:
        return 'improving'
    elif recent_avg < older_avg - 1:
        return 'declining'
    else:
        return 'stable'


def calculate_weekly_performance(results):
    """Calculate performance statistics by week"""
    from django.utils import timezone
    from datetime import timedelta

    weeks = []
    for i in range(4):  # Last 4 weeks
        week_start = timezone.now() - timedelta(weeks=i + 1)
        week_end = timezone.now() - timedelta(weeks=i)

        week_results = results.filter(
            created_at__gte=week_start,
            created_at__lt=week_end
        )

        if week_results.exists():
            weeks.append({
                'week': f"Hafta {i + 1}",
                'tests': week_results.count(),
                'average': round(week_results.aggregate(Avg('score'))['score__avg'], 1),
                'passed': week_results.filter(passed=True).count()
            })

    return weeks


def analyze_difficult_questions(user):
    """Find questions user struggles with most"""
    user_answers = UserAnswer.objects.filter(
        test_result__user=user,
        is_correct=False
    ).values('question__question_text').annotate(
        wrong_count=Count('id')
    ).order_by('-wrong_count')[:5]

    return list(user_answers)


def calculate_time_statistics(results):
    """Calculate time-related statistics"""
    if not results.exists():
        return {}

    times = [r.time_taken.total_seconds() for r in results if r.time_taken]
    if not times:
        return {}

    return {
        'average_time': sum(times) / len(times) / 60,  # in minutes
        'fastest_time': min(times) / 60,
        'slowest_time': max(times) / 60,
    }


def calculate_user_ranking(user):
    """Calculate user's ranking among all users (anonymized)"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    user_avg = TestResult.objects.filter(user=user).aggregate(
        Avg('score')
    )['score__avg'] or 0

    better_users = User.objects.filter(
        test_results__score__gt=user_avg
    ).distinct().count()

    total_users = User.objects.filter(
        test_results__isnull=False
    ).distinct().count()

    if total_users == 0:
        return {'percentile': 100, 'total_users': 0}

    percentile = round((total_users - better_users) / total_users * 100, 1)

    return {
        'percentile': percentile,
        'total_users': total_users,
        'rank': better_users + 1
    }


def generate_improvement_suggestions(results, category_stats):
    """Generate personalized improvement suggestions"""
    suggestions = []

    if not results.exists():
        return ["Birinchi testingizni topshiring!"]

    avg_score = results.aggregate(Avg('score'))['score__avg'] or 0

    # General performance suggestions
    if avg_score < 10:
        suggestions.append("Asosiy yo'l qoidalarini o'rganishdan boshlang")
        suggestions.append("Har kuni 30 daqiqa nazariy materiallarni o'qing")
    elif avg_score < 14:
        suggestions.append("Qiyin mavzularga ko'proq e'tibor bering")
        suggestions.append("Xato javoblaringizni tahlil qiling")
    elif avg_score < 18:
        suggestions.append("Muntazam test topshirib, bilimlaringizni mustahkamlang")
        suggestions.append("Murakkab savollar ustida ishlang")
    else:
        suggestions.append("A'lo natijalaringizni davom ettiring!")
        suggestions.append("Boshqa foydalanuvchilarga yordam bering")

    # Category-specific suggestions
    weak_categories = [
        name for name, stats in category_stats.items()
        if stats['average'] < 14
    ]

    if weak_categories:
        suggestions.append(f"Quyidagi mavzularni takrorlang: {', '.join(weak_categories[:2])}")

    return suggestions[:4]  # Return max 4 suggestions


@login_required
def education_view(request, category_id=None):
    """Educational content view"""
    if category_id:
        # Show specific category content
        category = get_object_or_404(Category, id=category_id)
        contents = EducationContent.objects.filter(category=category).order_by('order', 'created_at')
        return render(request, 'quiz/education_category.html', {
            'category': category,
            'contents': contents
        })
    else:
        # Show all categories with preview content (top 3 per category)
        categories = Category.objects.all()
        
        # Har bir category uchun faqat 3 ta content olish
        for category in categories:
            category.preview_content = category.education_content.order_by('order', 'created_at')[:3]
            category.total_content_count = category.education_content.count()
            
        return render(request, 'quiz/education.html', {
            'categories': categories
        })


@login_required
def education_content_view(request, content_id):
    """Individual education content view"""
    content = get_object_or_404(EducationContent, id=content_id)
    related_content = EducationContent.objects.filter(
        category=content.category
    ).exclude(id=content_id)[:3]

    return render(request, 'quiz/education_content.html', {
        'content': content,
        'related_content': related_content
    })


@login_required
def recommendations_view(request):
    """Advanced recommendation engine with personalized suggestions"""
    user_results = TestResult.objects.filter(user=request.user).order_by('-created_at')

    if not user_results.exists():
        # First-time user recommendations
        context = {
            'total_tests': 0,
            'performance_level': 'beginner',
            'readiness_percentage': 0,
            'estimated_study_days': 30,
            'priority_recommendations': get_beginner_recommendations(),
            'weak_categories': [],
            'achievements_data': get_beginner_achievements(),
            'weekly_goal': {'completed': 0, 'target': 5},
            'next_milestone': {'title': 'Birinchi test', 'description': 'Birinchi testingizni topshiring'},
            'motivation': {'streak': 0, 'message': 'Boshlang\'ich darajada'},
            'smart_suggestions': get_beginner_smart_suggestions()
        }
        return render(request, 'quiz/recommendations.html', context)

    # Analyze user performance
    performance_analysis = analyze_user_performance(request.user, user_results)

    # Generate recommendations based on analysis
    recommendations = generate_personalized_recommendations(request.user, performance_analysis)

    # Find weak categories with detailed analysis
    weak_categories = analyze_weak_categories(request.user, user_results)

    # Generate dynamic achievements and challenges
    achievements_data = generate_achievements(request.user, user_results, performance_analysis)

    # Calculate progress tracking metrics
    progress_metrics = calculate_progress_metrics(request.user, user_results)

    # Generate smart AI-like suggestions
    smart_suggestions = generate_smart_suggestions(performance_analysis, user_results)

    context = {
        'total_tests': user_results.count(),
        'performance_level': performance_analysis['level'],
        'readiness_percentage': performance_analysis['readiness_percentage'],
        'estimated_study_days': performance_analysis['estimated_study_days'],
        'priority_recommendations': recommendations,
        'weak_categories': weak_categories,
        'achievements_data': achievements_data,
        'weekly_goal': progress_metrics['weekly_goal'],
        'next_milestone': progress_metrics['next_milestone'],
        'motivation': progress_metrics['motivation'],
        'smart_suggestions': smart_suggestions
    }

    return render(request, 'quiz/recommendations.html', context)


def analyze_user_performance(user, user_results):
    """Comprehensive performance analysis"""
    total_tests = user_results.count()
    avg_score = user_results.aggregate(Avg('score'))['score__avg'] or 0
    best_score = user.best_score
    passed_tests = user_results.filter(passed=True).count()
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    # Determine performance level
    if avg_score >= 18:
        level = 'excellent'
        readiness = 95
        study_days = 3
    elif avg_score >= 16:
        level = 'good'
        readiness = 80
        study_days = 7
    elif avg_score >= 14:
        level = 'average'
        readiness = 65
        study_days = 14
    elif avg_score >= 10:
        level = 'below_average'
        readiness = 40
        study_days = 21
    else:
        level = 'beginner'
        readiness = 20
        study_days = 30

    # Analyze improvement trend
    recent_tests = user_results[:5]
    older_tests = user_results[5:10] if user_results.count() > 5 else user_results.none()

    improvement_trend = 'stable'
    if recent_tests.exists() and older_tests.exists():
        recent_avg = recent_tests.aggregate(Avg('score'))['score__avg']
        older_avg = older_tests.aggregate(Avg('score'))['score__avg']

        if recent_avg > older_avg + 2:
            improvement_trend = 'improving'
        elif recent_avg < older_avg - 2:
            improvement_trend = 'declining'

    return {
        'level': level,
        'avg_score': avg_score,
        'best_score': best_score,
        'pass_rate': pass_rate,
        'readiness_percentage': readiness,
        'estimated_study_days': study_days,
        'improvement_trend': improvement_trend,
        'total_tests': total_tests
    }


def generate_personalized_recommendations(user, analysis):
    """Generate priority recommendations based on performance analysis"""
    recommendations = []

    if analysis['level'] == 'beginner':
        recommendations.extend([
            {
                'title': 'Asosiy yo\'l qoidalarini o\'rganing',
                'description': 'Haydovchilik asoslari bilan tanishib chiqing. Bu sizning poydevor bilimlaringizni mustahkamlaydi.',
                'icon': '📚',
                'priority': 'high',
                'action_url': '/quiz/education/1/',
                'action_text': 'O\'rganishni boshlash',
                'estimated_time': '2-3 soat'
            },
            {
                'title': 'Har kuni 1 ta test topshiring',
                'description': 'Muntazam mashq qilish bilimlaringizni mustahkamlash uchun eng yaxshi usul.',
                'icon': '📝',
                'priority': 'high',
                'action_url': '/quiz/categories/',
                'action_text': 'Test topshirish',
                'estimated_time': '15-20 daqiqa'
            }
        ])

    elif analysis['level'] == 'below_average':
        recommendations.extend([
            {
                'title': 'Xato javoblaringizni tahlil qiling',
                'description': 'Qaysi savollar qiyin bo\'lganini aniqlang va shu mavzularga e\'tibor bering.',
                'icon': '🔍',
                'priority': 'high',
                'action_url': '/quiz/statistics/',
                'action_text': 'Statistikani ko\'rish',
                'estimated_time': '30 daqiqa'
            }
        ])

    elif analysis['level'] == 'average':
        recommendations.extend([
            {
                'title': 'Qiyin mavzularga fokus qiling',
                'description': 'O\'rtacha natijalaringiz bor, endi qiyin mavzularni o\'rganish vaqti keldi.',
                'icon': '🎯',
                'priority': 'medium',
                'action_url': '/quiz/categories/',
                'action_text': 'Qiyin testlar',
                'estimated_time': '45 daqiqa'
            }
        ])

    elif analysis['level'] in ['good', 'excellent']:
        recommendations.extend([
            {
                'title': 'Bilimlaringizni mustahkamlang',
                'description': 'A\'lo natijalaringiz bor! Endi barqarorlikni saqlash muhim.',
                'icon': '🏆',
                'priority': 'medium',
                'action_url': '/quiz/tickets/',
                'action_text': 'Tasodifiy testlar',
                'estimated_time': '20 daqiqa'
            }
        ])

    # Add improvement trend based recommendations
    if analysis['improvement_trend'] == 'declining':
        recommendations.insert(0, {
            'title': 'Diqqat! Natijalaringiz pasaymoqda',
            'description': 'So\'nggi testlaringiz oldingilaridan yomonroq. Qo\'shimcha mashq kerak.',
            'icon': '⚠️',
            'priority': 'high',
            'action_url': '/quiz/education/',
            'action_text': 'Takrorlash',
            'estimated_time': '1 soat'
        })

    return recommendations


def analyze_weak_categories(user, user_results):
    """Detailed analysis of weak categories"""
    weak_categories = []

    for category in Category.objects.all():
        category_results = user_results.filter(category=category)
        if category_results.exists():
            avg_score = category_results.aggregate(Avg('score'))['score__avg']
            if avg_score < 14:  # Less than 70%
                # Get specific education content for this category
                education_content = EducationContent.objects.filter(category=category)[:3]

                # Get detailed attempt results
                detailed_attempts = []
                for result in category_results[:3]:  # Son 3ta urinish
                    correct_count = result.score
                    total_questions = result.total_questions
                    wrong_count = total_questions - correct_count
                    detailed_attempts.append({
                        'date': result.created_at,
                        'correct_count': correct_count,
                        'wrong_count': wrong_count,
                        'total_questions': total_questions,
                        'percentage': round((correct_count / total_questions) * 100, 1)
                    })
                
                weak_categories.append({
                    'category': category,
                    'average_score': round(avg_score, 1),
                    'total_attempts': category_results.count(),
                    'detailed_attempts': detailed_attempts,
                    'education_content': education_content,
                    'improvement_potential': calculate_improvement_potential(category_results),
                    'difficulty_level': get_category_difficulty(avg_score)
                })

    # Sort by improvement potential (worst first)
    weak_categories.sort(key=lambda x: x['average_score'])

    return weak_categories


def generate_study_plan(analysis, weak_categories):
    """Generate a personalized weekly study plan"""
    study_plan = []

    if analysis['level'] == 'beginner':
        study_plan = [
            {
                'day_name': 'Dushanba',
                'duration': 45,
                'activities': [
                    {'icon': '📖', 'title': 'Yo\'l qoidalarini o\'qish', 'time': 20},
                    {'icon': '📝', 'title': 'Amaliyot test', 'time': 20},
                    {'icon': '🔄', 'title': 'Takrorlash', 'time': 5}
                ],
                'tip': 'Asosiy tushunchalar bilan tanishing'
            },
            {
                'day_name': 'Chorshanba',
                'duration': 30,
                'activities': [
                    {'icon': '🚦', 'title': 'Yo\'l belgilarini o\'rganish', 'time': 15},
                    {'icon': '📝', 'title': 'Test topshirish', 'time': 15}
                ],
                'tip': 'Belgilarni yodlab oling'
            },
            {
                'day_name': 'Juma',
                'duration': 40,
                'activities': [
                    {'icon': '🏥', 'title': 'Birinchi yordam', 'time': 20},
                    {'icon': '📝', 'title': 'Aralash test', 'time': 20}
                ],
                'tip': 'Haftaning yakuniy testi'
            }
        ]

    elif analysis['level'] == 'average':
        study_plan = [
            {
                'day_name': 'Dushanba',
                'duration': 35,
                'activities': [
                    {'icon': '🎯', 'title': 'Kuchsiz mavzular', 'time': 20},
                    {'icon': '📝', 'title': 'Maxsus test', 'time': 15}
                ],
                'tip': 'Kuchsiz tomonlaringizga e\'tibor bering'
            },
            {
                'day_name': 'Chorshanba',
                'duration': 25,
                'activities': [
                    {'icon': '📝', 'title': 'Tasodifiy test', 'time': 20},
                    {'icon': '📊', 'title': 'Natijalarni tahlil', 'time': 5}
                ],
                'tip': 'Muntazamlik muhim'
            },
            {
                'day_name': 'Shanba',
                'duration': 30,
                'activities': [
                    {'icon': '🔄', 'title': 'Haftalik takror', 'time': 15},
                    {'icon': '📝', 'title': 'Nazorat testi', 'time': 15}
                ],
                'tip': 'Haftalik yutuqlaringizni baholang'
            }
        ]

    else:  # good/excellent
        study_plan = [
            {
                'day_name': 'Chorshanba',
                'duration': 20,
                'activities': [
                    {'icon': '📝', 'title': 'Qiyin test', 'time': 20}
                ],
                'tip': 'Darajangizni saqlang'
            },
            {
                'day_name': 'Shanba',
                'duration': 25,
                'activities': [
                    {'icon': '🎲', 'title': 'Tasodifiy bilet', 'time': 20},
                    {'icon': '📊', 'title': 'Tahlil', 'time': 5}
                ],
                'tip': 'Barqarorlikni nazorat qiling'
            }
        ]

    return study_plan

def generate_achievements(user, user_results, analysis):
    """Generate dynamic achievements and challenges based on database"""
    from django.utils import timezone
    
    # Get or create user progress
    progress_data = get_user_progress_data(user)
    
    achievements = []
    challenges = []
    
    # Define all achievements with their unlock conditions
    all_achievements = [
        {'id': 'first_test', 'icon': '🎯', 'title': 'Birinchi qadam', 'description': 'Birinchi testingizni topshirdingiz!', 'condition': progress_data['total_tests'] >= 1},
        {'id': 'active_learner', 'icon': '📈', 'title': 'Faol o\'quvchi', 'description': '5 ta test topshirdingiz', 'condition': progress_data['total_tests'] >= 5},
        {'id': 'test_champion', 'icon': '🏆', 'title': 'Test chempioni', 'description': '10 ta test topshirdingiz', 'condition': progress_data['total_tests'] >= 10},
        {'id': 'excellent_student', 'icon': '⭐', 'title': 'A\'lo o\'quvchi', 'description': 'O\'rtacha 18+ ball', 'condition': progress_data['average_score'] >= 18},
        {'id': 'streak_master', 'icon': '🔥', 'title': 'Ketma-ketlik ustasi', 'description': f'{progress_data["current_streak"]} kun ketma-ket test', 'condition': progress_data['current_streak'] >= 7},
        {'id': 'experienced_driver', 'icon': '🎖️', 'title': 'Tajribali haydovchi', 'description': '20 ta test topshiring', 'condition': progress_data['total_tests'] >= 20, 'max_progress': 20},
        {'id': 'perfectionist', 'icon': '🌟', 'title': 'Mukammallik', 'description': 'O\'rtacha 19+ ball olish', 'condition': progress_data['average_score'] >= 19, 'max_progress': 19},
        {'id': 'streak_legend', 'icon': '💎', 'title': 'Ketma-ketlik afsonasi', 'description': '30 kun ketma-ket test', 'condition': progress_data['current_streak'] >= 30, 'max_progress': 30},
        {'id': 'master_driver', 'icon': '👑', 'title': 'Usta haydovchi', 'description': '50 ta test topshiring', 'condition': progress_data['total_tests'] >= 50, 'max_progress': 50},
    ]
    
    for achievement in all_achievements:
        if achievement['id'] in progress_data['unlocked_achievements']:
            # Already unlocked
            achievements.append({
                'icon': achievement['icon'],
                'title': achievement['title'],
                'description': achievement['description'],
                'type': 'unlocked',
                'progress': 100
            })
        elif achievement['condition']:
            # Just unlocked
            achievements.append({
                'icon': achievement['icon'],
                'title': achievement['title'],
                'description': achievement['description'],
                'type': 'unlocked',
                'progress': 100
            })
        else:
            # Still locked, show progress
            if 'max_progress' in achievement:
                if achievement['id'] == 'experienced_driver':
                    progress = int((progress_data['total_tests'] / achievement['max_progress']) * 100)
                elif achievement['id'] == 'perfectionist':
                    progress = int((progress_data['average_score'] / achievement['max_progress']) * 100) if progress_data['average_score'] > 0 else 0
                elif achievement['id'] == 'streak_legend':
                    progress = int((progress_data['current_streak'] / achievement['max_progress']) * 100)
                elif achievement['id'] == 'master_driver':
                    progress = int((progress_data['total_tests'] / achievement['max_progress']) * 100)
                else:
                    progress = 0
                
                achievements.append({
                    'icon': achievement['icon'],
                    'title': achievement['title'],
                    'description': achievement['description'],
                    'type': 'locked',
                    'progress': min(100, progress)
                })
    
    # Generate dynamic challenges
    today_tests = user_results.filter(created_at__date=timezone.now().date()).count()
    
    if today_tests == 0:
        challenges.append({
            'icon': '🎯',
            'title': 'Bugungi maqsad',
            'description': 'Bugun 1 ta test topshiring',
            'reward': '+15 XP',
            'difficulty': 'Oson',
            'time_left': 'Bugun'
        })
    
    week_tests = user_results.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7)).count()
    if week_tests < 5:
        challenges.append({
            'icon': '📅',
            'title': 'Haftalik challenge',
            'description': '5 ta test topshiring (hafta davomida)',
            'reward': '+50 XP',
            'difficulty': 'O\'rta',
            'time_left': f'{5-week_tests} ta test qoldi'
        })
    
    # Perfect score challenge
    if progress_data['total_tests'] > 0:
        challenges.append({
            'icon': '💎',
            'title': 'Mukammal natija',
            'description': 'Keyingi testda 20/20 ball oling',
            'reward': '+30 XP',
            'difficulty': 'Qiyin',
            'time_left': 'Keyingi test'
        })
    
    return {
        'achievements': achievements,
        'challenges': challenges,
        'total_xp': progress_data['total_xp'],
        'level': {
            'level': progress_data['current_level'],
            'title': progress_data['level_title'],
            'icon': get_level_icon(progress_data['current_level'])
        },
        'next_level_progress': {
            'needed_xp': progress_data['next_level_xp'],
            'current_xp': progress_data['total_xp']
        }
    }

def get_level_icon(level):
    """Get icon for user level"""
    icons = {1: '🌱', 2: '📈', 3: '⭐', 4: '🏆', 5: '👑'}
    return icons.get(level, '🌱')

def calculate_test_streak(user_results):
    """Calculate consecutive days with tests"""
    from django.utils import timezone
    
    if not user_results.exists():
        return 0
    
    streak = 0
    current_date = timezone.now().date()
    
    for i in range(30):  # Check last 30 days
        check_date = current_date - timezone.timedelta(days=i)
        if user_results.filter(created_at__date=check_date).exists():
            streak += 1
        else:
            break
    
    return streak

def get_user_level(total_tests, avg_score):
    """Calculate user level based on tests and performance"""
    if total_tests >= 20 and avg_score >= 18:
        return {'level': 5, 'title': 'Ekspert haydovchi', 'icon': '👑'}
    elif total_tests >= 15 and avg_score >= 16:
        return {'level': 4, 'title': 'Malakali haydovchi', 'icon': '🏆'}
    elif total_tests >= 10 and avg_score >= 14:
        return {'level': 3, 'title': 'Tajribali o\'quvchi', 'icon': '⭐'}
    elif total_tests >= 5:
        return {'level': 2, 'title': 'Faol o\'quvchi', 'icon': '📈'}
    else:
        return {'level': 1, 'title': 'Yangi boshlovchi', 'icon': '🌱'}

def get_next_level_progress(total_tests, avg_score):
    """Calculate progress to next level"""
    current_level = get_user_level(total_tests, avg_score)['level']
    
    if current_level == 1:
        return {'needed_tests': max(0, 5 - total_tests), 'needed_avg': 0}
    elif current_level == 2:
        return {'needed_tests': max(0, 10 - total_tests), 'needed_avg': max(0, 14 - avg_score)}
    elif current_level == 3:
        return {'needed_tests': max(0, 15 - total_tests), 'needed_avg': max(0, 16 - avg_score)}
    elif current_level == 4:
        return {'needed_tests': max(0, 20 - total_tests), 'needed_avg': max(0, 18 - avg_score)}
    else:
        return {'needed_tests': 0, 'needed_avg': 0}

def get_beginner_achievements():
    """Achievements for beginners"""
    return {
        'achievements': [
            {
                'icon': '🎯',
                'title': 'Birinchi qadam',
                'description': 'Birinchi testingizni topshiring',
                'type': 'locked',
                'progress': 0
            }
        ],
        'challenges': [
            {
                'icon': '🚀',
                'title': 'Boshlang\'ich qadamlar',
                'description': 'Birinchi testingizni topshiring',
                'reward': '+10 XP',
                'difficulty': 'Oson',
                'time_left': 'Hoziroq'
            }
        ],
        'total_xp': 0,
        'level': {'level': 1, 'title': 'Yangi boshlovchi', 'icon': '🌱'},
        'next_level_progress': {'needed_tests': 5, 'needed_avg': 0}
    }

def update_user_progress(user, test_result):
    """Update user progress after completing a test"""
    progress, created = UserProgress.objects.get_or_create(user=user)
    
    # Update basic stats
    progress.total_tests_completed += 1
    progress.total_questions_answered += test_result.total_questions
    progress.total_correct_answers += test_result.score
    progress.average_score = (progress.total_correct_answers / progress.total_questions_answered * 20) if progress.total_questions_answered > 0 else 0
    
    # Update streak
    progress.update_streak()
    
    # Calculate XP rewards
    base_xp = 10  # Base XP per test
    score_bonus = test_result.score * 2  # 2 XP per correct answer
    streak_bonus = progress.current_streak * 5 if progress.current_streak >= 3 else 0
    perfect_bonus = 20 if test_result.score == test_result.total_questions else 0
    
    total_xp = base_xp + score_bonus + streak_bonus + perfect_bonus
    level_up_data = progress.add_xp(total_xp)
    
    # Update category mastery
    if test_result.category:
        category_id = str(test_result.category.id)
        current_mastery = progress.category_mastery.get(category_id, 0)
        score_percentage = (test_result.score / test_result.total_questions) * 100
        
        # Update mastery (weighted average)
        new_mastery = (current_mastery * 0.7) + (score_percentage * 0.3)
        progress.category_mastery[category_id] = min(100, max(0, new_mastery))
    
    # Check and unlock achievements
    new_achievements = check_achievements(progress, test_result)
    
    # Update challenges
    update_challenges(progress, test_result)
    
    progress.save()
    
    return {
        'xp_gained': total_xp,
        'level_up': level_up_data,
        'new_achievements': new_achievements,
        'streak': progress.current_streak,
        'total_xp': progress.total_xp,
        'level': progress.current_level
    }

def check_achievements(progress, test_result):
    """Check and unlock new achievements"""
    new_achievements = []
    
    achievements_to_check = [
        {'id': 'first_test', 'condition': progress.total_tests_completed >= 1, 'title': 'Birinchi qadam'},
        {'id': 'active_learner', 'condition': progress.total_tests_completed >= 5, 'title': 'Faol o\'quvchi'},
        {'id': 'test_champion', 'condition': progress.total_tests_completed >= 10, 'title': 'Test chempioni'},
        {'id': 'excellent_student', 'condition': progress.average_score >= 18, 'title': 'A\'lo o\'quvchi'},
        {'id': 'streak_master', 'condition': progress.current_streak >= 7, 'title': 'Ketma-ketlik ustasi'},
        {'id': 'perfect_score', 'condition': test_result.score == test_result.total_questions, 'title': 'Mukammal natija'},
        {'id': 'experienced_driver', 'condition': progress.total_tests_completed >= 20, 'title': 'Tajribali haydovchi'},
        {'id': 'perfectionist', 'condition': progress.average_score >= 19.5, 'title': 'Mukammallik'},
    ]
    
    for achievement in achievements_to_check:
        if achievement['condition'] and achievement['id'] not in progress.unlocked_achievements:
            progress.unlocked_achievements.append(achievement['id'])
            new_achievements.append(achievement)
    
    return new_achievements

def update_challenges(progress, test_result):
    """Update user challenges"""
    from django.utils import timezone
    
    # Update daily challenge
    today = timezone.now().date()
    daily_challenge = f"daily_{today.strftime('%Y-%m-%d')}"
    
    if daily_challenge not in progress.completed_challenges:
        progress.completed_challenges.append(daily_challenge)
        progress.add_xp(5, "Daily challenge completed")
    
    # Update weekly challenge
    week_start = today - timezone.timedelta(days=today.weekday())
    weekly_tests = TestResult.objects.filter(
        user=progress.user,
        created_at__date__gte=week_start
    ).count()
    
    if weekly_tests >= 5:
        weekly_challenge = f"weekly_{week_start.strftime('%Y-%m-%d')}"
        if weekly_challenge not in progress.completed_challenges:
            progress.completed_challenges.append(weekly_challenge)
            progress.add_xp(20, "Weekly challenge completed")

def get_user_progress_data(user):
    """Get comprehensive user progress data"""
    try:
        progress = UserProgress.objects.get(user=user)
    except UserProgress.DoesNotExist:
        progress = UserProgress.objects.create(user=user)
    
    return {
        'total_xp': progress.total_xp,
        'current_level': progress.current_level,
        'level_title': progress.level_title,
        'current_streak': progress.current_streak,
        'best_streak': progress.best_streak,
        'total_tests': progress.total_tests_completed,
        'average_score': round(progress.average_score, 1),
        'unlocked_achievements': progress.unlocked_achievements,
        'category_mastery': progress.category_mastery,
        'next_level_xp': progress.get_next_level_xp(),
        'improvement_rate': progress.improvement_rate
    }

def calculate_time_statistics(user_results):
    """Calculate time-related statistics"""
    if not user_results.exists():
        return {}

    times = [r.time_taken.total_seconds() for r in user_results if r.time_taken]
    if not times:
        return {}

    return {
        'average_time': sum(times) / len(times) / 60,  # in minutes
        'fastest_time': min(times) / 60,
        'slowest_time': max(times) / 60,
    }


def calculate_user_ranking(user):
    """Calculate user's ranking among all users (anonymized)"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    user_avg = TestResult.objects.filter(user=user).aggregate(
        Avg('score')
    )['score__avg'] or 0

    better_users = User.objects.filter(
        test_results__score__gt=user_avg
    ).distinct().count()

    total_users = User.objects.filter(
        test_results__isnull=False
    ).distinct().count()

    if total_users == 0:
        return {'percentile': 100, 'total_users': 0}

    percentile = round((total_users - better_users) / total_users * 100, 1)

    return {
        'percentile': percentile,
        'total_users': total_users,
        'rank': better_users + 1
    }


def generate_smart_suggestions(analysis, user_results):
    """Generate AI-like smart suggestions"""
    suggestions = []

    # Time-based suggestions
    from django.utils import timezone
    now = timezone.now()
    hour = now.hour

    if 9 <= hour <= 11:
        suggestions.append({
            'title': 'Ertalabki mashq vaqti',
            'description': 'Ertalab miya eng faol ishlaydi. Test topshirish uchun eng yaxshi vaqt!',
            'icon': '🌅',
            'confidence': 85
        })
    elif 14 <= hour <= 16:
        suggestions.append({
            'title': 'Tushdan keyin takrorlash',
            'description': 'Bu vaqt takrorlash uchun juda mos. Kecha o\'rgangan narsalarni mustahkamlang.',
            'icon': '🔄',
            'confidence': 78
        })

    # Performance-based suggestions
    if analysis['improvement_trend'] == 'improving':
        suggestions.append({
            'title': 'Taraqqiyot davom etmoqda!',
            'description': 'Natijalaringiz yaxshilanmoqda. Hozirgi tempni saqlang va yanada qiyin testlarni sinab ko\'ring.',
            'icon': '📈',
            'confidence': 92
        })

    # Pattern-based suggestions
    recent_results = user_results[:5]
    if recent_results.exists():
        avg_time = sum([r.time_taken.total_seconds() for r in recent_results if r.time_taken]) / len(recent_results)
        if avg_time > 900:  # More than 15 minutes
            suggestions.append({
                'title': 'Tezlikni oshiring',
                'description': 'Testlarni juda sekin topshiryapsiz. Vaqtni boshqarishni o\'rganing.',
                'icon': '⏱️',
                'confidence': 73
            })

    # Motivational suggestions
    if analysis['total_tests'] >= 20:
        suggestions.append({
            'title': 'Tajribali foydalanuvchi',
            'description': 'Siz allaqachon ko\'p tajribaga egasiz. Boshqalarga yordam berishni o\'ylab ko\'ring.',
            'icon': '🎓',
            'confidence': 88
        })

    return suggestions


def get_beginner_recommendations():
    """Recommendations for first-time users"""
    return [
        {
            'title': 'Xush kelibsiz!',
            'description': 'Avtotest platformasiga xush kelibsiz. Birinchi testingizni topshirib, darajangizni aniqlang.',
            'icon': '👋',
            'priority': 'high',
            'action_url': '/quiz/categories/',
            'action_text': 'Birinchi test',
            'estimated_time': '20 daqiqa'
        },
        {
            'title': 'Asosiy qoidalarni o\'rganing',
            'description': 'Yo\'l harakati qoidalari bilan tanishib chiqing.',
            'icon': '📚',
            'priority': 'medium',
            'action_url': '/quiz/education/',
            'action_text': 'O\'rganish',
            'estimated_time': '30 daqiqa'
        }
    ]


def get_beginner_study_plan():
    """Study plan for beginners"""
    return [
        {
            'day_name': 'Bugun',
            'duration': 20,
            'activities': [
                {'icon': '📝', 'title': 'Birinchi test', 'time': 20}
            ],
            'tip': 'Darajangizni aniqlash uchun'
        }
    ]


def get_beginner_smart_suggestions():
    """Smart suggestions for beginners"""
    return [
        {
            'title': 'Boshlang\'ich darajada',
            'description': 'Hech qaysi test topshirmadingiz. Birinchi testingizni topshirib, o\'z darajangizni bilib oling.',
            'icon': '🚀',
            'confidence': 100
        }
    ]


def calculate_improvement_potential(results):
    """Calculate how much a user can improve in a category"""
    if results.count() < 2:
        return 'unknown'

    scores = [r.score for r in results.order_by('-created_at')[:5]]
    trend = sum(scores[-2:]) / 2 - sum(scores[:2]) / 2

    if trend > 1:
        return 'high'
    elif trend > -1:
        return 'medium'
    else:
        return 'low'


def get_category_difficulty(avg_score):
    """Determine difficulty level of a category for the user"""
    if avg_score < 8:
        return 'very_hard'
    elif avg_score < 12:
        return 'hard'
    elif avg_score < 16:
        return 'medium'
    else:
        return 'easy'


def calculate_consecutive_days(results):
    """Calculate consecutive days of activity"""
    if not results.exists():
        return 0

    from django.utils import timezone
    today = timezone.now().date()
    consecutive = 0

    # Get unique dates of tests
    test_dates = set(results.values_list('created_at__date', flat=True))

    current_date = today
    while current_date in test_dates:
        consecutive += 1
        current_date -= timedelta(days=1)

    return consecutive


@login_required
def test_results_view(request, result_id):
    """Display detailed test results with comprehensive analysis"""
    test_result = get_object_or_404(TestResult, id=result_id, user=request.user)
    user_answers = UserAnswer.objects.filter(test_result=test_result).select_related(
        'question', 'question__category', 'selected_answer'
    ).prefetch_related('question__answers')

    # Group answers by correctness for analysis
    correct_answers = user_answers.filter(is_correct=True)
    incorrect_answers = user_answers.filter(is_correct=False)

    # Prepare detailed answer analysis
    detailed_answers = []
    for user_answer in user_answers:
        question = user_answer.question
        correct_answer = question.answers.filter(is_correct=True).first()
        
        detailed_answers.append({
            'question': question,
            'user_answer': user_answer.selected_answer,
            'correct_answer': correct_answer,
            'is_correct': user_answer.is_correct,
            'explanation': question.explanation,
            'category': question.category
        })

    # Calculate category performance for this test
    category_performance = {}
    category_stats = {}
    
    # Analyze each category in this test
    for answer_detail in detailed_answers:
        category = answer_detail['category']
        if category not in category_stats:
            category_stats[category] = {
                'correct': 0,
                'total': 0,
                'questions': []
            }
        
        category_stats[category]['total'] += 1
        category_stats[category]['questions'].append(answer_detail)
        
        if answer_detail['is_correct']:
            category_stats[category]['correct'] += 1

    # Convert to percentage and find weak categories
    weak_categories = []
    for category, stats in category_stats.items():
        percentage = round((stats['correct'] / stats['total'] * 100), 1)
        category_performance[category.name_uz] = {
            'correct': stats['correct'],
            'total': stats['total'],
            'percentage': percentage
        }
        
        if percentage < 70:  # Less than 70% is considered weak
            # Get education materials for this category
            education_materials = EducationContent.objects.filter(
                category=category
            ).order_by('order')[:3]
            
            weak_categories.append({
                'category': category,
                'percentage': percentage,
                'wrong_count': stats['total'] - stats['correct'],
                'total_count': stats['total'],
                'education_materials': education_materials,
                'wrong_questions': [q for q in stats['questions'] if not q['is_correct']]
            })

    # Get AI insights for this specific test
    ai_insights = None
    try:
        from .ai_analytics import get_ai_insights_for_user
        ai_insights = get_ai_insights_for_user(request.user)
    except Exception as e:
        pass

    # Generate specific recommendations for this test
    test_recommendations = []
    
    # Performance-based recommendations
    percentage = round((correct_answers.count() / user_answers.count() * 100), 1)
    
    if percentage >= 90:
        test_recommendations.append({
            'title': 'Mukammal natija! 🏆',
            'description': 'Siz bu mavzuni a\'lo darajada bilasiz.',
            'priority': 'success',
            'action': 'Boshqa kategoriyalarni ham sinab ko\'ring',
            'url': '/quiz/categories/'
        })
    elif percentage >= 80:
        test_recommendations.append({
            'title': 'Yaxshi natija! 👍',
            'description': f'Siz {incorrect_answers.count()} ta xato qildingiz.',
            'priority': 'info',
            'action': 'Xato savollarni ko\'rib chiqing',
            'url': '#wrong-answers'
        })
    elif percentage >= 70:
        test_recommendations.append({
            'title': 'O\'tish balli! ✅',
            'description': 'Test o\'tdingiz, lekin yaxshilash mumkin.',
            'priority': 'warning',
            'action': 'Ta\'lim materiallarini o\'qing',
            'url': '/quiz/education/'
        })
    else:
        test_recommendations.append({
            'title': 'Ko\'proq o\'rganish kerak 📚',
            'description': 'Asosiy mavzularni takrorlash tavsiya etiladi.',
            'priority': 'danger',
            'action': 'Nazariy materiallarni o\'rganing',
            'url': '/quiz/education/'
        })

    # Add category-specific recommendations
    for weak_cat in weak_categories:
        test_recommendations.append({
            'title': f'{weak_cat["category"].name_uz} mavzusini takrorlang',
            'description': f'{weak_cat["wrong_count"]} ta xato aniqlandi',
            'priority': 'warning',
            'action': 'Maxsus ta\'lim materiallarini ko\'ring',
            'url': f'/quiz/education/{weak_cat["category"].id}/',
            'materials': weak_cat['education_materials']
        })

    context = {
        'test_result': test_result,
        'user_answers': user_answers,
        'detailed_answers': detailed_answers,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'category_performance': category_performance,
        'weak_categories': weak_categories,
        'ai_insights': ai_insights,
        'test_recommendations': test_recommendations,
        'percentage': percentage,
        'pass_percentage': 70,
    }

    return render(request, 'quiz/results.html', context)


# Yangi view funksiyalar

@login_required
def category_test_view(request, category_id):
    """Show all tests available for a specific category"""
    category = get_object_or_404(Category, id=category_id)
    questions_count = Question.objects.filter(category=category).count()
    
    # Generate test variants (20 questions each)
    variants_count = max(1, questions_count // 20)
    variants = []
    for i in range(1, variants_count + 1):
        variants.append({
            'id': i,
            'name': f"Variant {i}",
            'questions_count': min(20, questions_count - (i-1) * 20)
        })
    
    # User's previous results in this category
    user_results = TestResult.objects.filter(
        user=request.user,
        category=category
    ).order_by('-created_at')[:5]
    
    context = {
        'category': category,
        'variants': variants,
        'questions_count': questions_count,
        'user_results': user_results
    }
    return render(request, 'quiz/category_test.html', context)


@login_required
def take_category_test_view(request, category_id):
    """Take a test for specific category"""
    category = get_object_or_404(Category, id=category_id)
    all_questions = list(Question.objects.filter(category=category))
    
    # Always select exactly 20 questions (first 20 or repeat if less)
    if len(all_questions) >= 20:
        questions = all_questions[:20]  # Take first 20
    else:
        # If less than 20, repeat questions to make 20
        questions = []
        while len(questions) < 20:
            questions.extend(all_questions)
        questions = questions[:20]
    
    context = {
        'questions': questions,
        'test_type': 'category',
        'test_name': f"{category.name_uz} - Kategoriya Test",
        'category_id': category_id,
    }
    return render(request, 'quiz/take_test.html', context)


@login_required
def general_test_view(request):
    """Show general test variants page"""
    total_questions = Question.objects.count()
    variants_count = max(1, total_questions // 20)
    
    variants = []
    for i in range(1, variants_count + 1):
        start_index = (i - 1) * 20
        end_index = min(i * 20, total_questions)
        
        # Variant uchun foydalanuvchining natijasini tekshirish
        variant_result = TestResult.objects.filter(
            user=request.user,
            test_type='general',
            variant_id=i
        ).first()
        
        status_info = {
            'attempted': False,
            'score': 0,
            'total': 20,
            'passed': False,
            'last_attempt': None
        }
        
        if variant_result:
            status_info = {
                'attempted': True,
                'score': variant_result.score,
                'total': variant_result.total_questions,
                'passed': variant_result.passed,
                'last_attempt': variant_result.created_at,
                'percentage': round((variant_result.score / variant_result.total_questions) * 100, 1)
            }
        
        variants.append({
            'id': i,
            'name': f"Variant {i}",
            'description': f"{start_index + 1}-{end_index} savollar",
            'questions_count': end_index - start_index,
            'status': status_info
        })
    
    # Faqat umumiy test uchun statistika
    completed_variants = TestResult.objects.filter(
        user=request.user,
        test_type='general'
    ).values('variant_id').distinct().count()
    
    passed_variants = TestResult.objects.filter(
        user=request.user,
        test_type='general',
        passed=True
    ).values('variant_id').distinct().count()
    
    # Barcha bazadagi savollar soniga nisbatan to'g'ri javoblar foizini hisoblash
    general_results = TestResult.objects.filter(
        user=request.user,
        test_type='general'
    )
    
    # Bazadagi barcha savollar soni
    from quiz.models import Question as QuestionModel
    total_questions_in_db = QuestionModel.objects.count()
    
    if general_results.exists():
        total_correct = sum([result.score for result in general_results])
        overall_correct_percentage = round((total_correct / total_questions_in_db) * 100, 1) if total_questions_in_db > 0 else 0
    else:
        overall_correct_percentage = 0
    
    overall_stats = {
        'total_variants': variants_count,
        'completed_variants': completed_variants,
        'passed_variants': passed_variants,
        'completion_percentage': round((completed_variants / variants_count) * 100, 1) if variants_count > 0 else 0,
        'pass_percentage': round((passed_variants / completed_variants) * 100, 1) if completed_variants > 0 else 0,
        'overall_correct_percentage': overall_correct_percentage
    }
    
    # User's previous general test results (barchasi) with percentage
    user_results_raw = TestResult.objects.filter(
        user=request.user,
        test_type='general'
    ).order_by('-created_at')[:10]
    
    # Har bir natijaga foizni qo'shish
    user_results = []
    for result in user_results_raw:
        result.percentage = round((result.score / result.total_questions) * 100, 1) if result.total_questions > 0 else 0
        user_results.append(result)
    
    context = {
        'variants': variants,
        'total_questions': total_questions,
        'user_results': user_results,
        'overall_stats': overall_stats
    }
    return render(request, 'quiz/general_test.html', context)


@login_required
def take_general_test_view(request, variant_id):
    """Take a general test with specific variant"""
    total_questions = Question.objects.count()
    start_index = (variant_id - 1) * 20
    end_index = min(variant_id * 20, total_questions)
    
    # Get sequential questions for this variant (exactly 20)
    all_questions = list(Question.objects.all())
    if start_index < len(all_questions):
        questions = all_questions[start_index:min(start_index + 20, len(all_questions))]
        
        # If less than 20, pad with more questions
        if len(questions) < 20:
            remaining = 20 - len(questions)
            additional_questions = all_questions[:remaining]
            questions.extend(additional_questions)
    else:
        # If variant goes beyond available questions, start from beginning
        questions = all_questions[:20] if len(all_questions) >= 20 else all_questions
    
    if not questions:
        return redirect('quiz:general_test')
    
    context = {
        'questions': questions,
        'test_type': 'general',
        'test_name': f"Umumiy Test - Variant {variant_id}",
        'variant_id': variant_id,
    }
    return render(request, 'quiz/take_test.html', context)


@login_required
def take_ticket_test_view(request, ticket_id):
    """Take a specific ticket test"""
    ticket = get_object_or_404(TestTicket, ticket_number=ticket_id)
    all_ticket_questions = list(ticket.questions.all())
    
    # Ensure exactly 20 questions
    if len(all_ticket_questions) >= 20:
        questions = all_ticket_questions[:20]
    else:
        # If less than 20, add random questions from other categories
        questions = all_ticket_questions.copy()
        remaining = 20 - len(questions)
        
        # Get additional questions from all categories
        additional_questions = list(Question.objects.exclude(
            id__in=[q.id for q in all_ticket_questions]
        )[:remaining])
        questions.extend(additional_questions)
        
        # If still not enough, repeat existing questions
        while len(questions) < 20:
            questions.extend(all_ticket_questions)
        questions = questions[:20]
    
    if not questions:
        return redirect('quiz:tickets')
    
    context = {
        'questions': questions,
        'test_type': 'ticket',
        'test_name': f"Bilet {ticket.ticket_number}",
        'ticket_id': ticket_id,
    }
    return render(request, 'quiz/take_test.html', context)


@login_required
def analytics_view(request):
    """Advanced analytics dashboard"""
    user_results = TestResult.objects.filter(user=request.user)
    
    if not user_results.exists():
        return redirect('quiz:categories')
    
    # Time-based analytics
    from django.utils import timezone
    now = timezone.now()
    
    # Last 30 days performance
    thirty_days_ago = now - timedelta(days=30)
    recent_results = user_results.filter(created_at__gte=thirty_days_ago)
    
    # Daily performance chart data
    daily_performance = []
    for i in range(30):
        date = now.date() - timedelta(days=i)
        day_results = recent_results.filter(created_at__date=date)
        if day_results.exists():
            daily_performance.append({
                'date': date.strftime('%m-%d'),
                'avg_score': round(day_results.aggregate(Avg('score'))['score__avg'], 1),
                'tests_count': day_results.count()
            })
    
    # Category breakdown
    category_breakdown = {}
    for category in Category.objects.all():
        cat_results = user_results.filter(category=category)
        if cat_results.exists():
            category_breakdown[category.name_uz] = {
                'total_tests': cat_results.count(),
                'avg_score': round(cat_results.aggregate(Avg('score'))['score__avg'], 1),
                'best_score': cat_results.aggregate(Max('score'))['score__max'],
                'pass_rate': round(cat_results.filter(passed=True).count() / cat_results.count() * 100, 1)
            }
    
    # Mistake analysis
    wrong_answers = UserAnswer.objects.filter(
        test_result__user=request.user,
        is_correct=False
    )
    
    common_mistakes = wrong_answers.values(
        'question__question_text'
    ).annotate(
        mistake_count=Count('id')
    ).order_by('-mistake_count')[:10]
    
    context = {
        'daily_performance': daily_performance[-7:],  # Last 7 days
        'category_breakdown': category_breakdown,
        'common_mistakes': common_mistakes,
        'total_tests': user_results.count(),
        'total_mistakes': wrong_answers.count(),
        'avg_score': round(user_results.aggregate(Avg('score'))['score__avg'], 1)
    }
    
    return render(request, 'quiz/analytics.html', context)


@login_required  
def education_category_view(request, category_id):
    """Show education materials for specific category"""
    category = get_object_or_404(Category, id=category_id)
    contents = EducationContent.objects.filter(category=category).order_by('order', 'created_at')
    
    # Get related questions count for this category
    questions_count = Question.objects.filter(category=category).count()
    
    context = {
        'category': category,
        'contents': contents,
        'questions_count': questions_count
    }
    return render(request, 'quiz/education_category.html', context)


def calculate_progress_metrics(user, user_results):
    """Calculate progress tracking metrics"""
    from django.utils import timezone
    now = timezone.now()
    
    # Weekly goal tracking
    week_start = now - timedelta(days=now.weekday())
    week_results = user_results.filter(created_at__gte=week_start)
    
    # Calculate consecutive days streak
    consecutive_days = calculate_consecutive_days(user_results)
    
    # Determine next milestone
    total_tests = user_results.count()
    next_milestone = None
    
    if total_tests < 5:
        next_milestone = {
            'title': '5 ta test',
            'description': 'Birinchi 5 ta testni tugatish',
            'progress': (total_tests / 5) * 100
        }
    elif total_tests < 20:
        next_milestone = {
            'title': '20 ta test', 
            'description': 'Tajribali foydalanuvchi bo\'lish',
            'progress': (total_tests / 20) * 100
        }
    else:
        next_milestone = {
            'title': 'Ekspert daraja',
            'description': 'A\'lo natijalarni saqlash',
            'progress': 100
        }
    
    # Motivation message
    motivation_messages = {
        0: "Birinchi qadamni qo'ying!",
        1: "Yaxshi boshlandi!",
        5: "Mukammal harakatlanmoqdasiz!",
        10: "Siz haqiqiy o'quvchisiz!",
        20: "Ekspert darajada!"
    }
    
    closest_milestone = max([k for k in motivation_messages.keys() if k <= consecutive_days])
    motivation_message = motivation_messages[closest_milestone]
    
    return {
        'weekly_goal': {
            'completed': week_results.count(),
            'target': 5,
            'progress': min(100, (week_results.count() / 5) * 100)
        },
        'next_milestone': next_milestone,
        'motivation': {
            'streak': consecutive_days,
            'message': motivation_message
        }
    }


def generate_detailed_analytics(user):
    """Generate detailed analytics with education recommendations"""
    from .models import EducationContent, Category, UserAnswer
    
    results = TestResult.objects.filter(user=user).order_by('-created_at')
    
    if not results.exists():
        return {
            'total_tests': 0,
            'avg_score': 0,
            'category_analysis': [],
            'recommendations': [],
            'progress_trend': 'no_data'
        }
    
    # Basic stats
    total_tests = results.count()
    avg_score = results.aggregate(Avg('score'))['score__avg'] or 0
    last_5_avg = results[:5].aggregate(Avg('score'))['score__avg'] or 0
    
    # Category analysis with errors
    incorrect_answers = UserAnswer.objects.filter(
        test_result__in=results,
        is_correct=False
    ).select_related('question__category')
    
    category_errors = {}
    total_questions_by_category = {}
    
    # Count errors and total questions by category
    for answer in UserAnswer.objects.filter(test_result__in=results).select_related('question__category'):
        category = answer.question.category
        if category not in category_errors:
            category_errors[category] = 0
            total_questions_by_category[category] = 0
        
        total_questions_by_category[category] += 1
        if not answer.is_correct:
            category_errors[category] += 1
    
    # Calculate error rates and create analysis
    category_analysis = []
    for category in category_errors.keys():
        total_questions = total_questions_by_category[category]
        errors = category_errors[category]
        correct = total_questions - errors
        accuracy = (correct / total_questions * 100) if total_questions > 0 else 0
        
        # Get education materials for this category
        education_materials = EducationContent.objects.filter(
            category=category
        ).order_by('order')[:3]
        
        category_analysis.append({
            'category': category,
            'total_questions': total_questions,
            'correct_answers': correct,
            'wrong_answers': errors,
            'accuracy': round(accuracy, 1),
            'status': 'excellent' if accuracy >= 85 else 'good' if accuracy >= 70 else 'needs_work',
            'education_materials': education_materials
        })
    
    # Sort by accuracy (worst first for recommendations)
    category_analysis.sort(key=lambda x: x['accuracy'])
    
    # Generate recommendations
    recommendations = []
    
    # Top 3 worst categories
    for analysis in category_analysis[:3]:
        if analysis['accuracy'] < 80 and analysis['education_materials']:
            recommendations.append({
                'type': 'improve_category',
                'category': analysis['category'].name_uz,
                'accuracy': analysis['accuracy'],
                'wrong_count': analysis['wrong_answers'],
                'materials': [
                    {
                        'title': material.title,
                        'type': material.content_type,
                        'url': f'/quiz/education/content/{material.id}/',
                        'icon': '📹' if material.content_type == 'video' else '📄' if material.content_type == 'text' else '🖼️'
                    } for material in analysis['education_materials']
                ]
            })
    
    # Progress trend
    if total_tests >= 3:
        recent_avg = results[:total_tests//2].aggregate(Avg('score'))['score__avg'] or 0
        older_avg = results[total_tests//2:].aggregate(Avg('score'))['score__avg'] or 0
        
        if recent_avg > older_avg + 1:
            progress_trend = 'improving'
        elif recent_avg < older_avg - 1:
            progress_trend = 'declining'
        else:
            progress_trend = 'stable'
    else:
        progress_trend = 'insufficient_data'
    
    return {
        'total_tests': total_tests,
        'avg_score': round(avg_score, 1),
        'last_5_avg': round(last_5_avg, 1),
        'category_analysis': category_analysis,
        'recommendations': recommendations,
        'progress_trend': progress_trend
    }


@login_required
def detailed_statistics_view(request):
    """Batafsil statistika sahifasi"""
    analytics = generate_detailed_analytics(request.user)
    
    context = {
        'analytics': analytics
    }
    return render(request, 'quiz/detailed_statistics.html', context)


@login_required 
def ai_analytics_view(request):
    """AI Statistik sahifasi"""
    try:
        # AI tahlilini olish
        ai_insights = get_ai_insights_for_user(request.user)
        
        # Qo'shimcha statistika
        user_results = TestResult.objects.filter(user=request.user)
        basic_stats = {
            'total_tests': user_results.count(),
            'avg_score': user_results.aggregate(Avg('score'))['score__avg'] or 0,
            'last_test_date': user_results.order_by('-created_at').first().created_at if user_results.exists() else None
        }
        
        context = {
            'ai_insights': ai_insights,
            'basic_stats': basic_stats,
            'user': request.user
        }
        
    except Exception as e:
        # Xatolik bo'lsa standart xabar
        context = {
            'ai_insights': {
                'ai_analysis': f"AI xizmati vaqtincha mavjud emas. Iltimos keyinroq urinib ko'ring. Xato: {str(e)}",
                'recommendations': [],
                'confidence': 0
            },
            'basic_stats': {
                'total_tests': 0,
                'avg_score': 0,
                'last_test_date': None
            },
            'user': request.user
        }
    
    return render(request, 'quiz/ai_analytics.html', context)


@login_required
def get_test_recommendations_view(request):
    """Test tugagandan keyin maxsus tavsiyalar berish"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            correct_count = data.get('correct_count', 0)
            total_questions = data.get('total_questions', 20)
            incorrect_answers = data.get('incorrect_answers', [])
            test_type = data.get('test_type', '')
            category_id = data.get('category_id')
            
            recommendations = []
            
            # Natija darajasiga qarab tavsiyalar
            percentage = (correct_count / total_questions) * 100
            
            if percentage >= 90:
                recommendations.append({
                    'title': 'Mukammal natija!',
                    'description': 'Siz bu mavzuni juda yaxshi bilasiz. Boshqa mavzularni ham sinab ko\'ring.',
                    'priority': 'low',
                    'icon': '🏆',
                    'action_url': '/quiz/categories/'
                })
            elif percentage >= 80:
                recommendations.append({
                    'title': 'Yaxshi natija!',
                    'description': 'Bir necha xatoliklar mavjud. Ularni takrorlang.',
                    'priority': 'medium',
                    'icon': '👍',
                    'action_url': '/quiz/education/'
                })
            elif percentage >= 70:
                recommendations.append({
                    'title': 'O\'rtacha natija',
                    'description': 'Bilimlaringizni mustahkamlash zarur. Ta\'lim materiallarini ko\'ring.',
                    'priority': 'high',
                    'icon': '📚',
                    'action_url': '/quiz/education/'
                })
            else:
                recommendations.append({
                    'title': 'Ko\'proq o\'rganish kerak',
                    'description': 'Asosiy qoidalarni qayta o\'rganing. Sizga maxsus rejim tavsiya etiladi.',
                    'priority': 'high',
                    'icon': '⚠️',
                    'action_url': '/quiz/education/'
                })
            
            # Kategoriya bo'yicha maxsus tavsiya
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    education_materials = EducationContent.objects.filter(
                        category=category
                    ).order_by('order')[:2]
                    
                    if education_materials.exists():
                        recommendations.append({
                            'title': f'{category.name_uz} bo\'yicha qo\'shimcha o\'rganish',
                            'description': f'Bu mavzu bo\'yicha video va matn materiallarini ko\'ring.',
                            'priority': 'medium',
                            'icon': '🎯',
                            'action_url': f'/quiz/education/{category.id}/'
                        })
                except Category.DoesNotExist:
                    pass
            
            # Umumiy tavsiyalar
            if len(incorrect_answers) > 5:
                recommendations.append({
                    'title': 'AI Statistik tahlilini ko\'ring',
                    'description': 'Barcha xatolaringiz tahlil qilinadi va maxsus maslahatlar beriladi.',
                    'priority': 'high',
                    'icon': '🤖',
                    'action_url': '/quiz/ai-analytics/'
                })
            
            return JsonResponse({
                'success': True,
                'recommendations': recommendations[:3],  # Maksimal 3 ta
                'test_stats': {
                    'percentage': round(percentage, 1),
                    'correct': correct_count,
                    'total': total_questions
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def ai_analysis_view(request):
    """AI tahlil qilish uchun AJAX view"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            test_result_id = data.get('test_result_id')
            
            if not test_result_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Test result ID ko\'rsatilmagan'
                })
            
            # Test natijasini olish
            test_result = get_object_or_404(TestResult, id=test_result_id, user=request.user)
            
            # AI tahlilini olish
            from .ai_analytics import get_ai_insights_for_user
            ai_insights = get_ai_insights_for_user(request.user)
            
            # Test-specific AI analysis
            user_answers = UserAnswer.objects.filter(test_result=test_result).select_related(
                'question', 'question__category', 'selected_answer'
            )
            
            wrong_answers = user_answers.filter(is_correct=False)
            
            # Bu test uchun maxsus AI prompt yaratish
            test_specific_prompt = f"""
Bu foydalanuvchi hozirgina test topshirdi. Quyidagi ma'lumotlar asosida maxsus tahlil bering:

TEST NATIJASI:
- Umumiy ball: {test_result.score}/{test_result.total_questions}
- Foiz: {round(test_result.score/test_result.total_questions*100, 1)}%
- Test turi: {'Kategoriya' if test_result.category else 'Umumiy'}
- Kategoriya: {test_result.category.name_uz if test_result.category else 'Barcha mavzular'}

XATO QILINGAN SAVOLLAR:
"""
            
            # Xato qilingan savollarni qo'shish
            for i, wrong_answer in enumerate(wrong_answers[:5], 1):  # Faqat birinchi 5 ta
                correct_answer = wrong_answer.question.answers.filter(is_correct=True).first()
                test_specific_prompt += f"""
{i}. SAVOL: {wrong_answer.question.question_text}
   KATEGORIA: {wrong_answer.question.category.name_uz}
   SIZNING JAVOBINGIZ: {wrong_answer.selected_answer.answer_text}
   TO'G'RI JAVOB: {correct_answer.answer_text if correct_answer else 'Noma\'lum'}
"""

            test_specific_prompt += """

VAZIFA:
1. Bu test natijasini qisqacha baholang
2. Xato qilingan har bir savol uchun qisqa tushuntirish bering
3. Keyingi testlarga qanday tayyorlanish kerakligini aytib bering
4. 3-4 ta aniq maslahat bering

Javobingizni o'zbek tilida, tushunarli va motivatsiyali qilib yozing.
"""
            
            # AI dan javob olish
            try:
                import google.generativeai as genai
                from django.conf import settings
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-pro')
                
                response = model.generate_content(test_specific_prompt)
                ai_analysis = response.text
                
                # AI tahlilini bazaga saqlash
                from .models import AIAnalysis
                
                # Zaif va kuchli kategoriyalarni aniqlash
                weak_categories = []
                strong_categories = []
                category_stats = {}
                
                # Kategoriya bo'yicha statistika
                for answer in user_answers:
                    category = answer.question.category
                    if category not in category_stats:
                        category_stats[category] = {'correct': 0, 'total': 0}
                    
                    category_stats[category]['total'] += 1
                    if answer.is_correct:
                        category_stats[category]['correct'] += 1
                
                # Zaif va kuchli kategoriyalarni ajratish
                for category, stats in category_stats.items():
                    percentage = (stats['correct'] / stats['total']) * 100
                    if percentage < 70:
                        weak_categories.append({
                            'name': category.name_uz,
                            'percentage': round(percentage, 1),
                            'correct': stats['correct'],
                            'total': stats['total']
                        })
                    elif percentage >= 85:
                        strong_categories.append({
                            'name': category.name_uz,
                            'percentage': round(percentage, 1),
                            'correct': stats['correct'],
                            'total': stats['total']
                        })
                
                # Tavsiyalar yaratish
                recommendations = []
                if weak_categories:
                    for weak_cat in weak_categories[:3]:
                        recommendations.append({
                            'type': 'study_category',
                            'title': f"{weak_cat['name']} mavzusini takrorlang",
                            'description': f"Bu mavzuda {weak_cat['percentage']}% natija ko'rsatdingiz",
                            'priority': 'high'
                        })
                
                # AI tahlilini saqlash
                ai_analysis_obj = AIAnalysis.objects.create(
                    user=request.user,
                    test_result=test_result,
                    analysis_text=ai_analysis,
                    recommendations=recommendations,
                    confidence_score=85,  # Default confidence
                    analysis_type='test_specific',
                    weak_categories=weak_categories,
                    strong_categories=strong_categories,
                    improvement_suggestions=recommendations
                )
                
                return JsonResponse({
                    'success': True,
                    'ai_analysis': ai_analysis,
                    'analysis_id': ai_analysis_obj.id
                })
                
            except Exception as ai_error:
                return JsonResponse({
                    'success': False,
                    'error': f'AI xizmatida xatolik: {str(ai_error)}'
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Xatolik yuz berdi: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Faqat POST so\'rov qabul qilinadi'})
