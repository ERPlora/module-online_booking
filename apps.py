from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OnlineBookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'online_booking'
    label = 'online_booking'
    verbose_name = _('Online Booking')

    def ready(self):
        pass
