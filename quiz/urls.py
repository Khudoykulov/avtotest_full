from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.home_view, name='home'),
    
    # 1-bo'lim: Kategoriya bo'yicha testlar
    path('categories/', views.categories_view, name='categories'),
    path('category/<int:category_id>/', views.category_test_view, name='category_test'),
    path('test/category/<int:category_id>/', views.take_category_test_view, name='take_category_test'),
    
    # 2-bo'lim: Umumiy testlar (variantlar)
    path('general-test/', views.general_test_view, name='general_test'),
    path('test/general/<int:variant_id>/', views.take_general_test_view, name='take_general_test'),
    
    # 3-bo'lim: Biletlik testlar
    path('tickets/', views.tickets_view, name='tickets'),
    path('test/ticket/<int:ticket_id>/', views.take_ticket_test_view, name='take_ticket_test'),
    
    # Test yakunlash va natijalar
    path('submit-test/', views.submit_test_view, name='submit_test'),
    path('get-test-recommendations/', views.get_test_recommendations_view, name='get_test_recommendations'),
    path('results/<int:result_id>/', views.test_results_view, name='test_results'),
    path('ai-analysis/', views.ai_analysis_view, name='ai_analysis'),
    
    # Statistika va tahlil
    path('statistics/', views.statistics_view, name='statistics'),
    path('detailed-statistics/', views.detailed_statistics_view, name='detailed_statistics'),
    path('ai-analytics/', views.ai_analytics_view, name='ai_analytics'),
    path('test-analysis/<int:test_id>/', views.single_test_analysis_view, name='single_test_analysis'),
    path('analytics/', views.analytics_view, name='analytics'),
    
    # Ta'lim materiallari
    path('education/', views.education_view, name='education'),
    path('education/<int:category_id>/', views.education_category_view, name='education_category'),
    path('education/content/<int:content_id>/', views.education_content_view, name='education_content'),
    
    # Tavsiyalar
    path('recommendations/', views.recommendations_view, name='recommendations'),
]
