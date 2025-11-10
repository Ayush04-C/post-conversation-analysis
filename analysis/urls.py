from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.create_conversation, name='create_conversation'),
    path('analyse/', views.analyse_conversation, name='analyse_conversation'),
    path('reports/', views.get_reports, name='get_reports'),
]
