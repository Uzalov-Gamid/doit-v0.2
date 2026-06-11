from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, UpdateView

from activity.models import ActionLog
from activity.services import log_action

from .forms import TaskForm
from .models import Task


@login_required
def dashboard(request):
    base_tasks = Task.objects.filter(user=request.user)
    tasks = base_tasks
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if status in dict(Task.STATUS_CHOICES):
        tasks = tasks.filter(status=status)

    stats = {
        'total': base_tasks.count(),
        'new': base_tasks.filter(status=Task.STATUS_NEW).count(),
        'in_progress': base_tasks.filter(status=Task.STATUS_IN_PROGRESS).count(),
        'done': base_tasks.filter(status=Task.STATUS_DONE).count(),
    }

    context = {
        'tasks': tasks,
        'stats': stats,
        'query': query,
        'selected_status': status,
        'status_choices': Task.STATUS_CHOICES,
    }
    return render(request, 'tasks/dashboard.html', context)


class UserTaskMixin(LoginRequiredMixin):
    model = Task

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Задача создана.')
        response = super().form_valid(form)
        log_action(
            self.request.user,
            ActionLog.ACTION_TASK_CREATE,
            f'Создана задача: {self.object.title}',
        )
        return response


class TaskUpdateView(UserTaskMixin, UpdateView):
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Задача обновлена.')
        response = super().form_valid(form)
        log_action(
            self.request.user,
            ActionLog.ACTION_TASK_UPDATE,
            f'Обновлена задача: {self.object.title}',
        )
        return response


class TaskDeleteView(UserTaskMixin, DeleteView):
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:dashboard')

    def form_valid(self, form):
        title = self.object.title
        messages.success(self.request, 'Задача удалена.')
        response = super().form_valid(form)
        log_action(
            self.request.user,
            ActionLog.ACTION_TASK_DELETE,
            f'Удалена задача: {title}',
        )
        return response


@login_required
@require_POST
def change_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    status = request.POST.get('status')

    if status in dict(Task.STATUS_CHOICES):
        old_status = task.get_status_display()
        task.status = status
        task.save(update_fields=('status', 'updated_at'))
        log_action(
            request.user,
            ActionLog.ACTION_STATUS_CHANGE,
            f'Статус задачи "{task.title}" изменен: {old_status} -> {task.get_status_display()}',
        )
        messages.success(request, 'Статус задачи обновлен.')
    else:
        messages.error(request, 'Некорректный статус задачи.')

    return redirect('tasks:dashboard')
