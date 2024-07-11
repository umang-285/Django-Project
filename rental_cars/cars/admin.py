from django.contrib import admin
from cars.models import Car, Driver, CarImage

# Register your models here.
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    empty_value_display = "--empty--"
    list_display = ['brand', 'model', 'year', 'availability']


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    empty_value_display = "--empty--"
    list_display = ['first_name', 'last_name', 'email', 'phone_number', 'car']

admin.site.register(CarImage)
