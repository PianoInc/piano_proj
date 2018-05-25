"""piano_proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import include, url
from .views import main
from .views import piano_note

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^$', main, name='main'),
    url(r'^outsourcing_crawler/', include('outsourcing_crawler.urls')),
    url(r'^money_crawler/', include('money_crawler.urls')),
    url(r'^appstore_crawler/', include('appstore_crawler.urls')),
    url(r'^piano_note/$',piano_note, name='piano_note'),
]
