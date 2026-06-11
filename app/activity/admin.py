from django.contrib import admin

from .models import ActionLog


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'description', 'created_at')
    list_filter = ('action_type', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('user', 'action_type', 'description', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
