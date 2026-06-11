from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
