from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps

class Command(BaseCommand):
    help = "Assign permissions to KALRO groups"

    def handle(self, *args, **kwargs):
        # Models
        BookingRequest = apps.get_model("fleet", "BookingRequest")
        Vehicle = apps.get_model("fleet", "Vehicle")
        Assignment = apps.get_model("fleet", "Assignment")
        Driver = apps.get_model("fleet", "Driver")

        # Groups
        employees = Group.objects.get(name="Employees")
        supervisors = Group.objects.get(name="Supervisors")
        transport_officers = Group.objects.get(name="TransportOfficers")
        drivers = Group.objects.get(name="Drivers")
        admins = Group.objects.get(name="Admins")

        # Helper to assign permissions
        def assign(group, perms):
            for perm in perms:
                group.permissions.add(perm)
            self.stdout.write(self.style.SUCCESS(f"Assigned permissions to {group.name}"))

        # Fetch permissions by model
        booking_perms = Permission.objects.filter(content_type__app_label="fleet", content_type__model="bookingrequest")
        vehicle_perms = Permission.objects.filter(content_type__app_label="fleet", content_type__model="vehicle")
        assignment_perms = Permission.objects.filter(content_type__app_label="fleet", content_type__model="assignment")
        driver_perms = Permission.objects.filter(content_type__app_label="fleet", content_type__model="driver")

        # Assign permissions
        assign(employees, booking_perms)  # Employees can create/view bookings
        assign(supervisors, booking_perms)  # Supervisors can approve/reject bookings
        assign(transport_officers, booking_perms | vehicle_perms | assignment_perms | driver_perms)  # Manage fleet & assignments
        assign(drivers, assignment_perms)  # View/complete assignments
        admins.permissions.set(Permission.objects.all())  # Full access

        self.stdout.write(self.style.SUCCESS("Permissions assigned successfully!"))
