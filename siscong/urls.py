from django.conf.urls import include, url
from django.contrib import admin
from secretario import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^home/', include('secretario.urls')),
]
