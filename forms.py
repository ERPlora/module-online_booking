from django import forms
from django.utils.translation import gettext_lazy as _

from .models import BookingPageSettings, OnlineBooking


class BookingPageSettingsForm(forms.ModelForm):
    """Form for editing the booking page settings."""

    class Meta:
        model = BookingPageSettings
        fields = [
            'is_enabled',
            'page_title', 'welcome_message', 'primary_color', 'logo_url',
            'require_phone', 'require_email',
            'allow_staff_selection', 'allow_notes',
            'min_advance_hours', 'max_advance_days',
            'slot_duration_minutes', 'buffer_minutes',
            'confirmation_message', 'cancellation_policy',
        ]
        widgets = {
            'is_enabled': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'page_title': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Book an Appointment'),
            }),
            'welcome_message': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 3,
                'placeholder': _('Welcome message for your customers...'),
            }),
            'primary_color': forms.TextInput(attrs={
                'class': 'input',
                'type': 'color',
            }),
            'logo_url': forms.URLInput(attrs={
                'class': 'input',
                'placeholder': _('https://example.com/logo.png'),
            }),
            'require_phone': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'require_email': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'allow_staff_selection': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'allow_notes': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'min_advance_hours': forms.NumberInput(attrs={
                'class': 'input',
                'min': '0',
                'max': '168',
                'placeholder': '2',
            }),
            'max_advance_days': forms.NumberInput(attrs={
                'class': 'input',
                'min': '1',
                'max': '365',
                'placeholder': '30',
            }),
            'slot_duration_minutes': forms.NumberInput(attrs={
                'class': 'input',
                'min': '5',
                'max': '480',
                'step': '5',
                'placeholder': '30',
            }),
            'buffer_minutes': forms.NumberInput(attrs={
                'class': 'input',
                'min': '0',
                'max': '120',
                'step': '5',
                'placeholder': '0',
            }),
            'confirmation_message': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 3,
                'placeholder': _('Your appointment has been booked successfully...'),
            }),
            'cancellation_policy': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 3,
                'placeholder': _('Cancellation policy text...'),
            }),
        }


class BookingFilterForm(forms.Form):
    """Form for filtering the bookings list."""

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': _('Search by reference, customer, service...'),
        }),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('All Statuses')),
            ('pending', _('Pending')),
            ('confirmed', _('Confirmed')),
            ('cancelled', _('Cancelled')),
            ('completed', _('Completed')),
            ('no_show', _('No Show')),
        ],
        widget=forms.Select(attrs={
            'class': 'select',
        }),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'input',
            'type': 'date',
        }),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'input',
            'type': 'date',
        }),
    )


class CancelBookingForm(forms.Form):
    """Form for cancelling a booking with a reason."""

    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'textarea',
            'rows': 2,
            'placeholder': _('Reason for cancellation (optional)'),
        }),
    )
