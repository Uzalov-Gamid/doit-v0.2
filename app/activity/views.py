from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import render

from .models import ActionLog

LOGS_PER_PAGE = 20


@login_required
def action_log_list(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('Доступ к журналу действий разрешен только администратору.')

    logs = ActionLog.objects.select_related('user')
    action_type = request.GET.get('action_type', '').strip()

    if action_type in dict(ActionLog.ACTION_CHOICES):
        logs = logs.filter(action_type=action_type)

    paginator = Paginator(logs, LOGS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    page_query_params = request.GET.copy()
    page_query_params.pop('page', None)

    context = {
        'logs': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_query': page_query_params.urlencode(),
        'action_choices': ActionLog.ACTION_CHOICES,
        'selected_action_type': action_type,
    }
    return render(request, 'activity/action_log_list.html', context)
