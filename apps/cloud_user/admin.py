from django.contrib import admin
from cloud_user.models import Account, AccountZone, ZoneCode, ServerAccountZone
# Register your models here.

admin.site.register(Account)
admin.site.register(AccountZone)
admin.site.register(ZoneCode)
admin.site.register(ServerAccountZone)
