from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('categories/', views.categories_view, name='categories'),
    path('tickets/', views.tickets_view, name='tickets'),
    path('test/ticket/<int:ticket_id>/', views.take_test_view, name='take_ticket_test'),
    path('test/category/<int:category_id>/', views.take_test_view, name='take_category_test'),
    path('submit/', views.submit_test_view, name='submit_test'),
    path('results/<int:result_id>/', views.test_results_view, name='test_results'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('education/', views.education_view, name='education'),
    path('education/<int:category_id>/', views.education_view, name='education_category'),
    path('education/content/<int:content_id>/', views.education_content_view, name='education_content'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
]
