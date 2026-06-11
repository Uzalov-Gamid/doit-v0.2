from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView

from activity.models import ActionLog
from activity.services import log_action

from .forms import RegistrationForm


class RegisterView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('tasks:dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(self.object, ActionLog.ACTION_REGISTER, 'Пользователь зарегистрировался.')
        login(self.request, self.object)
        messages.success(self.request, 'Регистрация завершена.')
        return response
