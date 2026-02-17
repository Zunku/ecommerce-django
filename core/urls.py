from django.views.generic import TemplateView
from django.urls import path

# Special variable that storge urls patterns objects
# URL conf module, each app can have it's own
urlpatterns = [
    # path('URL/', view function)
    # All our routes must end with /
    # Templates has namespace, so is better to create unique namespace for each template, an easy way is using directories
    path('', TemplateView.as_view(template_name='core/index.html')),
]