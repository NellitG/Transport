from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Vehicle, Driver, BookingRequest, Assignment, TripLog
from .serializers import (VehicleSerializer, DriverSerializer, BookingRequestSerializer, AssignmentSerializer, TripLogSerializer)
from .permissions import IsSupervisor, IsTransportOfficer

#  BOOKING REQUESTS
class BookingRequestViewSet(viewsets.ModelViewSet):
    queryset = BookingRequest.objects.all()
    serializer_class = BookingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # staff see everything, others see only their own
        if user.is_staff:
            return BookingRequest.objects.all()
        return BookingRequest.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # OPTIONAL: block normal users from editing approved/assigned bookings
    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        if booking.status != BookingRequest.STATUS_PENDING:
            return Response(
                {'detail': 'Only pending bookings can be edited.'},
                status=400
            )
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsSupervisor])
    def approve(self, request, pk=None):
        booking = self.get_object()

        if booking.status != BookingRequest.STATUS_PENDING:
            return Response({'detail': 'Booking is not pending.'}, status=400)

        booking.status = BookingRequest.STATUS_APPROVED
        booking.supervisor = request.user
        booking.supervisor_comment = request.data.get('comment', '')
        booking.save()

        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsSupervisor])
    def reject(self, request, pk=None):
        booking = self.get_object()

        if booking.status != BookingRequest.STATUS_PENDING:
            return Response({'detail': 'Booking is not pending.'}, status=400)

        booking.status = BookingRequest.STATUS_REJECTED
        booking.supervisor = request.user
        booking.supervisor_comment = request.data.get('comment', '')
        booking.save()

        return Response({'status': 'rejected'})
    
#  ASSIGNMENTS (Transport Officers only)
class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('booking', 'vehicle', 'driver')
    serializer_class = AssignmentSerializer
    permission_classes = [IsTransportOfficer]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = serializer.validated_data["booking"]
        vehicle = serializer.validated_data["vehicle"]
        driver = serializer.validated_data["driver"]

        if booking.status != BookingRequest.STATUS_APPROVED:
            return Response(
                {"detail": "Booking must be approved before assignment."},
                status=400
            )

        # Real locking (your previous version did nothing)
        with transaction.atomic():
            locked_vehicle = Vehicle.objects.select_for_update().get(pk=vehicle.pk)
            locked_driver = Driver.objects.select_for_update().get(pk=driver.pk)

            # OPTIONAL: Prevent double booking vehicle/driver
            if Assignment.objects.filter(vehicle=locked_vehicle, status="active").exists():
                return Response({"detail": "Vehicle is already assigned."}, status=400)

            if Assignment.objects.filter(driver=locked_driver, status="active").exists():
                return Response({"detail": "Driver is already assigned."}, status=400)

            self.perform_create(serializer)

            # Set booking status
            booking.status = BookingRequest.STATUS_ASSIGNED
            booking.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, 201, headers=headers)

    # Optional manual control over updates
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

#  VEHICLES (Admins only)
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAdminUser]

#  DRIVERS (Admins only)
class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAdminUser]

#  TRIP LOGS
class TripLogViewSet(viewsets.ModelViewSet):
    queryset = TripLog.objects.select_related("assignment__booking")
    serializer_class = TripLogSerializer

    def get_permissions(self):
        # Drivers can only create/update logs for their trip
        if self.action in ["create", "update", "partial_update"]:
            return [permissions.IsAuthenticated()]
        # Admins can delete/view all
        return [permissions.IsAdminUser()]

    def update(self, request, *args, **kwargs):
        triplog = self.get_object()
        if triplog.status == "completed":
            return Response({"detail": "Completed logs cannot be edited."}, status=400)
        return super().update(request, *args, **kwargs)

