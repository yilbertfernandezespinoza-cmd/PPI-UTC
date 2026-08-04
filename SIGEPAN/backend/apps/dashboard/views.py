from django.shortcuts import render
from django.views import View

from apps.security.mixins import SessionRequiredMixin
from .services import DashboardService


class DashboardView(SessionRequiredMixin, View):

    def get(self, request):
        context = DashboardService.obtener_dashboard(request)
        return render(request, "dashboard/dashboard.html", context)