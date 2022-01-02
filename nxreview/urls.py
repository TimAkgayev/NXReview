"""Defines URL patterns for NXReview"""

from django.urls import path

from . import views

app_name = 'nxreview'
urlpatterns = [
    #Home Page 
    path('', views.index, name="index"),
    path('conflicts/', views.conflicts, name="conflicts_page"),
]