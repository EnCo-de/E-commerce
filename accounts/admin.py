from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Account, UserProfile

# Register your models here.
class AccountAdmin(UserAdmin):
        list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
        list_display_links = ('email', 'first_name', 'last_name', 'username')
        ordering = ('-date_joined',)
        readonly_fields = ['last_login', 'date_joined']

        filter_horizontal = []
        list_filter = []
        fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
        def thumbnail(self, object):
                return format_html('<img src="{}" style="width: 30px; border-radius: 50%;">', object.profile_picture.url)
        thumbnail.short_description = 'Profile picture'
        list_display = ['thumbnail', 'account', 'country', 'city']

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
