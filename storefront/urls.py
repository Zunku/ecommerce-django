"""
URL configuration for storefront project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# include: Include urls from another app
from django.urls import path, include
import debug_toolbar

# Changing the admin interface header
admin.site.site_header = 'Storefront Admin'
# Chaning the index_title
admin.site.index_title = 'Admin'

# A spacial variable that stores URLs, receives requests and directs them to their correspondant apps
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Any url that starts with playground will be routed to our playground app
    path('playground/', include('playground.urls')),
    
    path('store/', include('store.urls')),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    path('__debug__/', include(debug_toolbar.urls))
]