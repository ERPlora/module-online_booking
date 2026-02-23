from django.utils.translation import gettext_lazy as _

MODULE_ID = 'online_booking'
MODULE_NAME = _('Online Booking')
MODULE_VERSION = '1.0.0'
MODULE_ICON = 'globe-outline'
MODULE_DESCRIPTION = _('Public online appointment booking page for customers')
MODULE_AUTHOR = 'ERPlora'
MODULE_CATEGORY = 'services'

MENU = {
    'label': _('Online Booking'),
    'icon': 'globe-outline',
    'order': 45,
}

NAVIGATION = [
    {'label': _('Dashboard'), 'icon': 'speedometer-outline', 'id': 'dashboard'},
    {'label': _('Bookings'), 'icon': 'calendar-outline', 'id': 'bookings'},
    {'label': _('Settings'), 'icon': 'settings-outline', 'id': 'settings'},
]

DEPENDENCIES = ['customers']

PERMISSIONS = [
    'online_booking.view_booking',
    'online_booking.change_booking',
    'online_booking.delete_booking',
    'online_booking.confirm_booking',
    'online_booking.manage_settings',
]
