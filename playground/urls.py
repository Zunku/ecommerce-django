
# Object to define URLS
from django.urls import path
# Our views module
from . import views

# Special variable that storge urls patterns objects
# URL conf module, each app can have it's own
urlpatterns = [
    # 'URL', view functions
    # All our routes must end with /
    path('hello/', views.render_say_hello),
    path('filtering/', views.filtering),
    path('sort-limit/', views.sort_limit)
]