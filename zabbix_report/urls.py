"""zabbix_report URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from zabbix_items import views, cmdb

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^zabbix_report/', views.zabbix_report, name="zabbix_report"),
    url(r'^web_scenaris/', views.web_scenaris, name="web_scenaris"),
    url(r'^zichan_guanli/', cmdb.zichan_guanli, name="zichan_guanli"),

]
