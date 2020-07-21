from django.contrib import admin
from zabbix_items.models import Hostip, Hostinfomation
# Register your models here.
admin.site.register(Hostip)
admin.site.register(Hostinfomation)
