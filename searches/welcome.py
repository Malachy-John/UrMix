from django.views.generic import TemplateView
from searches.models import Genre


class Welcome(TemplateView):
    template_name: str = "base2.html"
