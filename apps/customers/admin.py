from django.contrib import admin

from .models import Debtor


@admin.register(Debtor)
class DebtorAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'whatsapp', 'trust_level']
    list_filter = ['trust_level', 'company']
    search_fields = ['name', 'whatsapp']
