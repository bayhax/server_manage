from django.contrib import admin
from server_list.models import ServerList, ServerListUpdate
from server_list.models import CommandLog, ServerPid, InsType,ServerNameRule

# Register your models here.
admin.site.register(ServerList)
admin.site.register(ServerListUpdate)
admin.site.register(CommandLog)
admin.site.register(ServerPid)
admin.site.register(InsType)
admin.site.register(ServerNameRule)


