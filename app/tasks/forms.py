from django import forms
from django.utils import timezone

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'status', 'due_date')
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'status': 'Статус',
            'due_date': 'Срок',
        }
        error_messages = {
            'title': {
                'required': 'Введите название задачи.',
                'max_length': 'Название задачи слишком длинное.',
            },
            'status': {
                'invalid_choice': 'Выберите корректный статус задачи.',
            },
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например: подготовить отчет'}),
            'description': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Кратко опишите детали задачи',
                }
            ),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title'].strip()

        if not title:
            raise forms.ValidationError('Введите название задачи.')

        if len(title) < 3:
            raise forms.ValidationError('Название должно быть не короче 3 символов.')

        return title

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')

        if due_date and due_date < timezone.localdate():
            raise forms.ValidationError('Срок задачи не может быть в прошлом.')

        return due_date
