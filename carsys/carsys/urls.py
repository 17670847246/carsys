"""carsys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include

from carsys import settings
from search.views import search_records, show_index, handle_record, delete_record, export_excel, export_exce, \
    get_bar_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', show_index),
    path('search/', search_records),
    path('handle/', handle_record),
    path('delete/', delete_record),
    path('export/', export_excel),
    path('expor/', export_exce),
    path('bardata/', get_bar_data),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.insert(0, path('__debug__/', include(debug_toolbar.urls)))


