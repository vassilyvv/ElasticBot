from django.contrib import admin

# Register your models here.
from mptt.admin import MPTTModelAdmin

from project.tgbot.models import BotCommand, QueryParameter, LastCommand, PostParam, SavedUrlParameter, SavedPostParameter


class UrlParamInline(admin.TabularInline):
    fields = ['name', 'key', 'value', 'is_header']
    model = QueryParameter


class PostParamInline(admin.TabularInline):
    fields = ['name', 'key', 'value', 'regex']
    model = PostParam


class BotCommandAdmin(MPTTModelAdmin):
    inlines = [UrlParamInline, PostParamInline]


admin.site.register(BotCommand, BotCommandAdmin)
admin.site.register(LastCommand)
admin.site.register(SavedUrlParameter)
admin.site.register(SavedPostParameter)

