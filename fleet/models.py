from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction

class Vehicle(models.Model):
    plate = models.CharField(max_length=10, unique=True)
    make = models.CharField(max_length=50, blank=True)
    capacity = models.PositiveIntegerField(default=4)
    STATUS_AVAILABLE = 'available'
    STATUS_ASSIGNED = 'assigned'
    STATUS_MAINTENANCE = 'maintenance'
    STATUS_OUT = 'out_of_service'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_MAINTENANCE, 'Maintenance'),
        (STATUS_OUT, 'Out of Service'),
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plate} - ({self.capacity})"
    
class Driver(models.Model):
    # Optionally link to User for login; not required.
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class BookingRequest(models.Model):
    PURPOSE_SEMINAR = 'seminar'
    PURPOSE_BOOTCAMP = 'bootcamp'
    PURPOSE_FIELD = 'field_trip'
    PURPOSE_OTHER = 'other'
    PURPOSE_CHOICES = [
        (PURPOSE_SEMINAR, 'Seminar'),
        (PURPOSE_BOOTCAMP, 'Bootcamp'),
        (PURPOSE_FIELD, 'Field Trip'),
        (PURPOSE_OTHER, 'Other'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_ASSIGNED = 'assigned'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    created_by = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    department = models.CharField(max_length=150, blank=True)
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)
    destination = models.CharField(max_length=300)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    passengers = models.PositiveIntegerField(default=1)
    additional_info = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    supervisor = models.ForeignKey(User, null=True, blank=True, related_name='approvals', on_delete=models.SET_NULL)
    supervisor_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_datetime']

    def clean(self):
        if self.start_datetime >= self.end_datetime:
            raise ValidationError("start_datetime must be before end_datetime")
        if self.passengers < 1:
            raise ValidationError("passengers must be at least 1")

    def __str__(self):
        return f"{self.purpose} by {self.created_by} on {self.start_datetime.date()}"

class Assignment(models.Model):
    booking = models.OneToOneField(BookingRequest, related_name='assignment', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT)
    fuel_allocated = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # capacity check
        if self.booking.passengers > self.vehicle.capacity:
            raise ValidationError("Vehicle capacity is smaller than number of passengers.")

        # check vehicle/time overlap
        overlap = Assignment.objects.filter(
            vehicle=self.vehicle,
            booking__start_datetime__lt=self.booking.end_datetime,
            booking__end_datetime__gt=self.booking.start_datetime,
        ).exclude(pk=self.pk)
        if overlap.exists():
            raise ValidationError("Vehicle has a conflicting assignment in that time range.")

        # check driver availability (basic)
        driver_overlap = Assignment.objects.filter(
            driver=self.driver,
            booking__start_datetime__lt=self.booking.end_datetime,
            booking__end_datetime__gt=self.booking.start_datetime,
        ).exclude(pk=self.pk)
        if driver_overlap.exists():
            raise ValidationError("Driver has a conflicting assignment in that time range.")

    def save(self, *args, **kwargs):
        # Run validation in a transaction to reduce race window.
        with transaction.atomic():
            self.full_clean()
            super().save(*args, **kwargs)
            # mark vehicle as assigned (simple)
            self.vehicle.status = Vehicle.STATUS_ASSIGNED
            self.vehicle.save(update_fields=['status'])

    def __str__(self):
        return f"Assignment for booking {self.booking_id}"

class TripLog(models.Model):
    assignment = models.OneToOneField(Assignment, related_name='triplog', on_delete=models.CASCADE)
    odometer_start = models.PositiveIntegerField(null=True, blank=True)
    odometer_end = models.PositiveIntegerField(null=True, blank=True)
    fuel_used = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def mark_completed(self):
        self.completed_at = timezone.now()
        self.save()
        # Optionally free the vehicle
        vehicle = self.assignment.vehicle
        vehicle.status = Vehicle.STATUS_AVAILABLE
        vehicle.save(update_fields=['status'])

    def __str__(self):
        return f"TripLog {self.pk} for assignment {self.assignment_id}"