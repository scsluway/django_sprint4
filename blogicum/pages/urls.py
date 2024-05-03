from django.urls import path

from .views import RulesView, AboutView

app_name = 'pages'

urlpatterns = [
    path(
        'about/',
        AboutView.as_view(template_name='pages/about.html'),
        name='about'
    ),
    path(
        'rules/',
        RulesView.as_view(template_name='pages/rules.html'),
        name='rules'
    ),
]
