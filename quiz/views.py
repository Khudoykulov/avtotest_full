from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg, Count, Q, Max
from django.db.models.functions import TruncDate
from .models import Category, TestTicket, Question, TestResult, UserAnswer, EducationContent
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
        test_result = TestResult.objects.create(
            user=request.user,
            ticket_id=ticket_id if test_type == 'ticket' else None,
            category_id=category_id if test_type == 'category' else None,
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
        test_result.passed = correct_answers >= (total_questions * 0.7)  # 70% to pass
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
        # Show all categories with preview content
        categories = Category.objects.prefetch_related('education_content').all()
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
            'study_plan': get_beginner_study_plan(),
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

    # Generate personalized study plan
    study_plan = generate_study_plan(performance_analysis, weak_categories)

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
        'study_plan': study_plan,
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
    older_tests = user_results[5:10] if user_results.count() > 5 else []

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

                weak_categories.append({
                    'category': category,
                    'average_score': round(avg_score, 1),
                    'total_attempts': category_results.count(),
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
    """Display detailed test results"""
    test_result = get_object_or_404(TestResult, id=result_id, user=request.user)
    user_answers = UserAnswer.objects.filter(test_result=test_result).select_related('question', 'selected_answer')

    # Group answers by correctness for analysis
    correct_answers = user_answers.filter(is_correct=True)
    incorrect_answers = user_answers.filter(is_correct=False)

    # Calculate category performance for this test
    category_performance = {}
    if test_result.category:
        category_performance[test_result.category.name_uz] = {
            'correct': correct_answers.count(),
            'total': user_answers.count(),
            'percentage': round((correct_answers.count() / user_answers.count() * 100), 1)
        }

    # Get recommendations based on incorrect answers
    weak_topics = []
    if incorrect_answers.exists():
        # Find most common mistake categories
        mistake_categories = incorrect_answers.values('question__category__name_uz').annotate(
            mistake_count=Count('id')
        ).order_by('-mistake_count')[:3]

        for cat in mistake_categories:
            weak_topics.append({
                'category': cat['question__category__name_uz'],
                'mistakes': cat['mistake_count']
            })

    context = {
        'test_result': test_result,
        'user_answers': user_answers,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'category_performance': category_performance,
        'weak_topics': weak_topics,
        'pass_percentage': 70,  # Required percentage to pass
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
        variants.append({
            'id': i,
            'name': f"Variant {i}",
            'description': f"{start_index + 1}-{end_index} savollar",
            'questions_count': end_index - start_index
        })
    
    # User's previous general test results
    user_results = TestResult.objects.filter(
        user=request.user,
        category__isnull=True,
        ticket__isnull=True
    ).order_by('-created_at')[:10]
    
    context = {
        'variants': variants,
        'total_questions': total_questions,
        'user_results': user_results
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
