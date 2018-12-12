from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^tg_admin/', admin.site.urls),
]
