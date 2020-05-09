from django.contrib import admin
from cloud_user.models import Account, ServerAccountZone, ZoneCode, AccountZone
# Register your models here.

admin.site.register(Account)
admin.site.register(ZoneCode)
admin.site.register(AccountZone)
admin.site.register(ServerAccountZone)
