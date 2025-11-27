from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, DriverViewSet, BookingRequestViewSet, AssignmentViewSet, TripLogViewSet

router = DefaultRouter()
router.register('vehicles', VehicleViewSet, basename='vehicle')
router.register('drivers', DriverViewSet, basename='driver')
router.register('bookings', BookingRequestViewSet, basename='booking')
router.register('assignments', AssignmentViewSet, basename='assignment')
router.register('triplogs', TripLogViewSet, basename='triplog')

urlpatterns = router.urls
