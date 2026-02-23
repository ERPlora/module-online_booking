from django.urls import path
from . import views

app_name = 'online_booking'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Bookings list
    path('bookings/', views.bookings_list, name='bookings'),

    # Booking actions
    path('bookings/<uuid:booking_id>/confirm/', views.booking_confirm, name='confirm'),
    path('bookings/<uuid:booking_id>/cancel/', views.booking_cancel, name='cancel'),
    path('bookings/<uuid:booking_id>/complete/', views.booking_complete, name='complete'),
    path('bookings/<uuid:booking_id>/no-show/', views.booking_no_show, name='no_show'),
    path('bookings/<uuid:booking_id>/delete/', views.booking_delete, name='delete'),

    # Bulk actions
    path('bookings/bulk/', views.booking_bulk_action, name='bulk_action'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]
