from django.contrib import admin
from config.models import Version, AddVersion, Pattern, RunCompany, Plat
# Register your models here.

admin.site.register(Version)
admin.site.register(AddVersion)
admin.site.register(Pattern)
admin.site.register(RunCompany)
admin.site.register(Plat)