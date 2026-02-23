from django.contrib import admin

from .models import BookingPageSettings, OnlineBooking


@admin.register(BookingPageSettings)
class BookingPageSettingsAdmin(admin.ModelAdmin):
    list_display = ('hub_id', 'is_enabled', 'page_title', 'updated_at')
    readonly_fields = ('id', 'hub_id', 'created_at', 'updated_at')


@admin.register(OnlineBooking)
class OnlineBookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_reference', 'customer_name', 'service_name',
        'booking_date', 'booking_time', 'status', 'created_at',
    )
    list_filter = ('status', 'booking_date')
    search_fields = ('booking_reference', 'customer_name', 'customer_email', 'service_name')
    readonly_fields = ('id', 'hub_id', 'booking_reference', 'created_at', 'updated_at')
    ordering = ('-booking_date', '-booking_time')
