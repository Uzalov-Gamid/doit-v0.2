from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import TaskForm
from .models import Task


@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/dashboard.html', {'tasks': tasks})


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
        return super().form_valid(form)


class TaskUpdateView(UserTaskMixin, UpdateView):
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Задача обновлена.')
        return super().form_valid(form)


class TaskDeleteView(UserTaskMixin, DeleteView):
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Задача удалена.')
        return super().form_valid(form)


@login_required
@require_POST
def change_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    status = request.POST.get('status')

    if status in dict(Task.STATUS_CHOICES):
        task.status = status
        task.save(update_fields=('status', 'updated_at'))
        messages.success(request, 'Статус задачи обновлен.')
    else:
        messages.error(request, 'Некорректный статус задачи.')

    return redirect('tasks:dashboard')
