"""
Online Booking Module Models

BookingPageSettings: Singleton configuration for the public booking page.
OnlineBooking: Individual booking records submitted by customers.
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models.base import HubBaseModel


# ============================================================================
# Booking Page Settings (singleton per hub)
# ============================================================================

class BookingPageSettings(HubBaseModel):
    """
    Configuration for the public online booking page.
    One record per hub (singleton pattern via unique_together on hub_id).
    """

    # Page status
    is_enabled = models.BooleanField(
        default=False,
        help_text=_('Whether the public booking page is active'),
    )

    # Page customization
    page_title = models.CharField(
        max_length=255,
        default=_('Book an Appointment'),
        help_text=_('Title displayed on the booking page'),
    )
    welcome_message = models.TextField(
        blank=True,
        help_text=_('Welcome message shown to customers'),
    )
    primary_color = models.CharField(
        max_length=20,
        default='#6366f1',
        help_text=_('Primary accent color for the booking page'),
    )
    logo_url = models.CharField(
        max_length=500,
        blank=True,
        help_text=_('URL to the logo displayed on the booking page'),
    )

    # Required fields
    require_phone = models.BooleanField(
        default=True,
        help_text=_('Require customer phone number'),
    )
    require_email = models.BooleanField(
        default=True,
        help_text=_('Require customer email address'),
    )

    # Booking options
    allow_staff_selection = models.BooleanField(
        default=True,
        help_text=_('Allow customers to choose their preferred staff member'),
    )
    allow_notes = models.BooleanField(
        default=True,
        help_text=_('Allow customers to add notes to their booking'),
    )

    # Booking rules
    min_advance_hours = models.IntegerField(
        default=2,
        help_text=_('Minimum hours in advance a booking can be made'),
    )
    max_advance_days = models.IntegerField(
        default=30,
        help_text=_('Maximum days in advance a booking can be made'),
    )
    slot_duration_minutes = models.IntegerField(
        default=30,
        help_text=_('Default time slot duration in minutes'),
    )
    buffer_minutes = models.IntegerField(
        default=0,
        help_text=_('Buffer time between appointments in minutes'),
    )

    # Messages
    confirmation_message = models.TextField(
        blank=True,
        default=_('Your appointment has been booked successfully. We will confirm it shortly.'),
        help_text=_('Message shown after a booking is submitted'),
    )
    cancellation_policy = models.TextField(
        blank=True,
        help_text=_('Cancellation policy text displayed to customers'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'online_booking_settings'
        unique_together = [('hub_id',)]
        verbose_name = _('Booking Page Settings')
        verbose_name_plural = _('Booking Page Settings')

    def __str__(self):
        return f'BookingPageSettings (hub={self.hub_id})'

    @classmethod
    def get_settings(cls, hub_id):
        """
        Get or create the settings singleton for a hub.
        Returns the BookingPageSettings instance.
        """
        settings, _ = cls.objects.get_or_create(hub_id=hub_id)
        return settings


# ============================================================================
# Online Booking
# ============================================================================

class OnlineBooking(HubBaseModel):
    """
    An individual booking record submitted via the public booking page
    or created manually from the admin panel.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        CONFIRMED = 'confirmed', _('Confirmed')
        CANCELLED = 'cancelled', _('Cancelled')
        COMPLETED = 'completed', _('Completed')
        NO_SHOW = 'no_show', _('No Show')

    # Reference
    booking_reference = models.CharField(
        max_length=20,
        help_text=_('Auto-generated booking reference (e.g. BK-00001)'),
    )

    # Customer info (linked if found, otherwise stored as text)
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='online_bookings',
        help_text=_('Linked customer record (if found)'),
    )
    customer_name = models.CharField(
        max_length=255,
        help_text=_('Customer name as entered in the booking form'),
    )
    customer_email = models.EmailField(
        blank=True,
        help_text=_('Customer email'),
    )
    customer_phone = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Customer phone number'),
    )

    # Service info (stored as text + UUID for resilience)
    service_id = models.UUIDField(
        null=True,
        blank=True,
        help_text=_('UUID of the booked service'),
    )
    service_name = models.CharField(
        max_length=255,
        help_text=_('Name of the booked service'),
    )

    # Staff info (stored as text + UUID for resilience)
    staff_id = models.UUIDField(
        null=True,
        blank=True,
        help_text=_('UUID of the assigned staff member'),
    )
    staff_name = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Name of the assigned staff member'),
    )

    # Date and time
    booking_date = models.DateField(
        help_text=_('Date of the appointment'),
    )
    booking_time = models.TimeField(
        help_text=_('Start time of the appointment'),
    )
    duration_minutes = models.IntegerField(
        default=30,
        help_text=_('Duration of the appointment in minutes'),
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Notes
    notes = models.TextField(
        blank=True,
        help_text=_('Customer notes or special requests'),
    )

    # Status timestamps
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When the booking was confirmed'),
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When the booking was cancelled'),
    )
    cancellation_reason = models.TextField(
        blank=True,
        help_text=_('Reason for cancellation'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'online_booking_booking'
        ordering = ['-booking_date', '-booking_time']
        indexes = [
            models.Index(fields=['hub_id', 'status']),
            models.Index(fields=['hub_id', 'booking_date']),
            models.Index(fields=['hub_id', 'booking_reference']),
            models.Index(fields=['hub_id', 'customer_email']),
        ]
        verbose_name = _('Online Booking')
        verbose_name_plural = _('Online Bookings')

    def __str__(self):
        return f'{self.booking_reference} - {self.customer_name} ({self.booking_date})'

    # --- Properties ---

    @property
    def booking_datetime(self):
        """Combine booking_date and booking_time into a datetime."""
        from datetime import datetime
        return datetime.combine(self.booking_date, self.booking_time)

    @property
    def is_past(self):
        """Check if the booking date/time is in the past."""
        from datetime import datetime
        now = timezone.localtime(timezone.now())
        booking_dt = datetime.combine(self.booking_date, self.booking_time)
        return timezone.make_aware(booking_dt) < now if timezone.is_naive(booking_dt) else booking_dt < now

    # --- Status transition methods ---

    def confirm(self):
        """Confirm a pending booking."""
        self.status = self.Status.CONFIRMED
        self.confirmed_at = timezone.now()
        self.save(update_fields=['status', 'confirmed_at', 'updated_at'])

    def cancel(self, reason=''):
        """Cancel a booking."""
        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.save(update_fields=['status', 'cancelled_at', 'cancellation_reason', 'updated_at'])

    def complete(self):
        """Mark a booking as completed."""
        self.status = self.Status.COMPLETED
        self.save(update_fields=['status', 'updated_at'])

    def mark_no_show(self):
        """Mark a booking as no-show."""
        self.status = self.Status.NO_SHOW
        self.save(update_fields=['status', 'updated_at'])

    # --- Reference generation ---

    def save(self, *args, **kwargs):
        """Auto-generate booking reference on first save."""
        if not self.booking_reference:
            self.booking_reference = self._generate_reference()
        super().save(*args, **kwargs)

    def _generate_reference(self):
        """Generate the next booking reference like BK-00001."""
        last = OnlineBooking.all_objects.filter(
            hub_id=self.hub_id,
        ).order_by('-booking_reference').first()

        if last and last.booking_reference.startswith('BK-'):
            try:
                last_num = int(last.booking_reference.split('-')[1])
                return f'BK-{last_num + 1:05d}'
            except (ValueError, IndexError):
                pass

        return 'BK-00001'
