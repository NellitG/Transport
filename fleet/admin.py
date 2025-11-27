from django.contrib import admin
from .models import Vehicle, Driver, BookingRequest, Assignment, TripLog

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate','make','capacity','status')
    search_fields = ('plate','make')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name','phone','license_number','is_active')
    search_fields = ('name','license_number')

@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('purpose','created_by','start_datetime','end_datetime','status')
    list_filter = ('status','purpose')
    search_fields = ('destination','created_by__username')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('booking','vehicle','driver','assigned_at')

@admin.register(TripLog)
class TripLogAdmin(admin.ModelAdmin):
    list_display = ('assignment','odometer_start','odometer_end','completed_at')

