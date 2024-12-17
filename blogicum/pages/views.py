from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponseServerError, HttpResponseForbidden


class AboutView(TemplateView):
    template_name = "pages/about.html"


class RulesView(TemplateView):
    template_name = "pages/rules.html"


def page_not_found_view(request, exception=None):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=""):
    return HttpResponseForbidden(
        render(request, "pages/403csrf.html", {"reason": reason})
    )


def internal_server_error(request):
    return HttpResponseServerError(render(request, "pages/500.html"))
