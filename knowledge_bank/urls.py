# ==============================================
# 1. MAIN PROJECT URLs - knowledge_bank/urls.py
# ==============================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_acts(request):
    return redirect('/acts/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # Apps with unique prefixes
    path('acts/', include('acts.urls')),
    path('bulletins/', include('bulletins.urls')),
    path('utilities/', include('utilities.urls')),
    path('links/', include('links.urls')),
    path('rules/', include('rules.urls')),
    path('forms/', include('forms.urls')),
    path('', redirect_to_acts, name='home_redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)