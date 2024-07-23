from django.contrib import admin

from . models import Cart

from . models import Payment,Order_table

admin.site.register(Cart)

admin.site.register(Payment)

admin.site.register(Order_table)
