from django.contrib import admin
from django.urls import path
from django.urls import include
from rango import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('rango/', include('rango.urls')),
    # The above maps any URLs starting with rango/ to be handled by rango.
    path('admin/', admin.site.urls),

]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)