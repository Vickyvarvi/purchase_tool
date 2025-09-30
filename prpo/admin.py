from django.contrib import admin
from .models import PurchaseRequest, PurchaseOrder


admin.site.register(PurchaseRequest)
admin.site.register(PurchaseOrder)

# Register your models here.
