from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .models import Vehicle, Driver, BookingRequest, Assignment, TripLog
from .serializers import VehicleSerializer, DriverSerializer, BookingRequestSerializer, AssignmentSerializer, TripLogSerializer
from .permissions import IsSupervisor, IsTransportOfficer

class BookingRequestViewSet(viewsets.ModelViewSet):
    queryset = BookingRequest.objects.all()
    serializer_class = BookingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Employees see their own; officers/admins may see more
        if user.is_staff:
            return BookingRequest.objects.all()
        return BookingRequest.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsSupervisor])
    def approve(self, request, pk=None):
        booking = self.get_object()
        if booking.status != BookingRequest.STATUS_PENDING:
            return Response({'detail': 'Booking is not pending.'}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = BookingRequest.STATUS_APPROVED
        booking.supervisor = request.user
        booking.supervisor_comment = request.data.get('comment', '')
        booking.save()
        # TODO: notify transport officers
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsSupervisor])
    def reject(self, request, pk=None):
        booking = self.get_object()
        if booking.status != BookingRequest.STATUS_PENDING:
            return Response({'detail': 'Booking is not pending.'}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = BookingRequest.STATUS_REJECTED
        booking.supervisor = request.user
        booking.supervisor_comment = request.data.get('comment', '')
        booking.save()
        return Response({'status': 'rejected'})

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('booking','vehicle','driver').all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsTransportOfficer]

    def create(self, request, *args, **kwargs):
        # Use a transaction and select_for_update on Vehicle and Driver to reduce races
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking_id = serializer.validated_data['booking'].pk
        vehicle_id = serializer.validated_data['vehicle'].pk
        driver_id = serializer.validated_data['driver'].pk

        with transaction.atomic():
            # lock vehicle row
            from django.db import connection
            # select_for_update on the vehicle and driver instances
            from .models import Vehicle, Driver
            Vehicle.objects.select_for_update().filter(pk=vehicle_id)
            Driver.objects.select_for_update().filter(pk=driver_id)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            # mark booking as assigned
            booking = BookingRequest.objects.get(pk=booking_id)
            booking.status = BookingRequest.STATUS_ASSIGNED
            booking.save(update_fields=['status'])
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAdminUser]

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAdminUser]

class TripLogViewSet(viewsets.ModelViewSet):
    queryset = TripLog.objects.select_related('assignment__booking').all()
    serializer_class = TripLogSerializer
    permission_classes = [permissions.IsAuthenticated]  # ideally restrict to driver/admin
