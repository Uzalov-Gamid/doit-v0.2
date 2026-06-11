from django.urls import path

from . import views

app_name = 'activity'

urlpatterns = [
    path('logs/', views.action_log_list, name='action_log_list'),
]
