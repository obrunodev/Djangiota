from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from .models import User, Company, CompanyMembership

admin.site.unregister(Group)

class CompanyMembershipInline(admin.TabularInline):
    model = CompanyMembership
    extra = 1
    autocomplete_fields = ['company']

@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    inlines = [CompanyMembershipInline]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
