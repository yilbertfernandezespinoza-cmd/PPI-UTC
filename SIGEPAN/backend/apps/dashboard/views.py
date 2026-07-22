from django.shortcuts import render
from django.views import View

from .services import DashboardService


class DashboardView(View):

    def get(self, request):

        context = DashboardService.obtener_dashboard(request)

        return render(
            request,
            "dashboard/dashboard.html",
            context
        )