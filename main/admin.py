from django.contrib import admin
from .models import scientist
from .models import news


admin.site.register(scientist)
admin.site.register(news)
