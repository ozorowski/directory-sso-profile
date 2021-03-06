from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import RedirectView, TemplateView

from profile.eig_apps import constants


class LandingPageView(RedirectView):
    pattern_name = 'about'


class AboutView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self):
        return {
            'about_tab_classes': 'active'
        }

    def get(self, *args, **kwargs):
        session_key = constants.HAS_VISITED_ABOUT_PAGE_SESSION_KEY
        self.request.session[session_key] = 'true'
        return super().get(*args, **kwargs)


class RedirectToAboutPageMixin:
    def dispatch(self, request, *args, **kwargs):
        has_visited = constants.HAS_VISITED_ABOUT_PAGE_SESSION_KEY
        if has_visited not in request.session:
            return redirect(reverse('about'))
        return super().dispatch(request, *args, **kwargs)
