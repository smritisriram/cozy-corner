"""
Cozy Corner URL configuration.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('courses/', views.courses_view, name='courses'),
    path('courses/<str:subject>/', views.course_topics_view, name='course_topics'),
    path('exams/', views.exams_view, name='exams'),
    path('exams/active/', views.exam_active_view, name='exam_active'),
    path('exams/complete/', views.exam_complete_view, name='exam_complete'),
    path('habits/', views.habits_view, name='habits'),
    path('habits/add/', views.habit_add_view, name='habit_add'),
    path('habits/<int:pk>/toggle/', views.habit_toggle_view, name='habit_toggle'),
    path('habits/<int:pk>/delete/', views.habit_delete_view, name='habit_delete'),
    path('journal/', views.journal_view, name='journal'),
    path('journal/new/', views.journal_entry_view, name='journal_new'),
    path('journal/<int:pk>/', views.journal_entry_view, name='journal_entry'),
    path('journal/<int:pk>/save/', views.journal_save_view, name='journal_save'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/message/', views.chat_message_view, name='chat_message'),
    path('account/', views.account_view, name='account'),
]
