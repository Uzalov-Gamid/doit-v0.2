from django import forms

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
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
