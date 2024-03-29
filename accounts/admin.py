from django.contrib import admin
from cuser.admin import UserAdmin

# Register your models here.
from .models import User, Address


class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone_no', 'town',
                    'estate', 'apartment', 'primary')


admin.site.register(User, UserAdmin)
admin.site.register(Address,AddressAdmin)
