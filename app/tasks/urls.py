from django.urls import path

from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tasks/new/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('tasks/<int:pk>/status/', views.change_task_status, name='task_status'),
]
