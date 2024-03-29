"""Defines URL patterns for NXReview"""

from django.urls import path

from . import views

app_name = 'nxreview'
urlpatterns = [
    #Home Page 
    path('', views.index, name="index"),
    path('quiz/', views.quiz, name="quiz_page"),
    path('important/', views.important, name="important_page"),
]