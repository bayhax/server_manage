from django.contrib import admin
from cloud_user.models import Account, ServerAccountZone
# Register your models here.

admin.site.register(Account)
admin.site.register(ServerAccountZone)
