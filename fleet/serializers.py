from rest_framework import serializers
from .models import Vehicle, Driver, BookingRequest, Assignment, TripLog
from django.db.models import Q

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = ('created_at',)

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'

class BookingRequestSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = BookingRequest
        read_only_fields = ('status','created_by','created_at')
        fields = '__all__'

    def validate(self, data):
        start = data.get('start_datetime') or getattr(self.instance, 'start_datetime', None)
        end = data.get('end_datetime') or getattr(self.instance, 'end_datetime', None)
        if start and end and start >= end:
            raise serializers.ValidationError("Start datetime must be before end datetime.")
        passengers = data.get('passengers', getattr(self.instance, 'passengers', 1))
        if passengers < 1:
            raise serializers.ValidationError("Passengers must be at least 1.")
        return data

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ('assigned_at',)

    def validate(self, data):
        booking = data.get('booking') or getattr(self.instance, 'booking', None)
        vehicle = data.get('vehicle') or getattr(self.instance, 'vehicle', None)
        driver = data.get('driver') or getattr(self.instance, 'driver', None)
        if booking is None or vehicle is None or driver is None:
            raise serializers.ValidationError("booking, vehicle and driver are required.")

        if booking.passengers > vehicle.capacity:
            raise serializers.ValidationError("Vehicle capacity too small for the booking passengers.")

        # overlap check
        overlapping = Assignment.objects.filter(
            vehicle=vehicle,
            booking__start_datetime__lt=booking.end_datetime,
            booking__end_datetime__gt=booking.start_datetime,
        ).exclude(pk=getattr(self.instance, 'pk', None))
        if overlapping.exists():
            raise serializers.ValidationError("Vehicle has a conflicting assignment in that time range.")

        driver_overlap = Assignment.objects.filter(
            driver=driver,
            booking__start_datetime__lt=booking.end_datetime,
            booking__end_datetime__gt=booking.start_datetime,
        ).exclude(pk=getattr(self.instance, 'pk', None))
        if driver_overlap.exists():
            raise serializers.ValidationError("Driver has a conflicting assignment in that time range.")

        return data

class TripLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripLog
        fields = '__all__'
        read_only_fields = ('completed_at',)
