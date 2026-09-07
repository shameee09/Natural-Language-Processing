"""
upload_project URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # App URLs
    path(
        '',
        include(('app_uplaod.urls', 'app_uplaod'), namespace='app_uplaod')
    ),

]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )