"""AI tools for the Online Booking module."""
from assistant.tools import AssistantTool, register_tool


@register_tool
class ListOnlineBookings(AssistantTool):
    name = "list_online_bookings"
    description = "List online bookings with optional filters."
    module_id = "online_booking"
    required_permission = "online_booking.view_onlinebooking"
    parameters = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "Filter: pending, confirmed, cancelled, completed, no_show"},
            "date": {"type": "string", "description": "Filter by date (YYYY-MM-DD)"},
            "limit": {"type": "integer", "description": "Max results (default 20)"},
        },
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from online_booking.models import OnlineBooking
        qs = OnlineBooking.objects.all().order_by('-booking_date', '-booking_time')
        if args.get('status'):
            qs = qs.filter(status=args['status'])
        if args.get('date'):
            qs = qs.filter(booking_date=args['date'])
        limit = args.get('limit', 20)
        return {
            "bookings": [
                {
                    "id": str(b.id),
                    "booking_reference": b.booking_reference,
                    "customer_name": b.customer_name,
                    "service_name": b.service_name,
                    "staff_name": b.staff_name,
                    "booking_date": str(b.booking_date),
                    "booking_time": str(b.booking_time),
                    "duration_minutes": b.duration_minutes,
                    "status": b.status,
                }
                for b in qs[:limit]
            ],
            "total": qs.count(),
        }


@register_tool
class GetBookingPageSettings(AssistantTool):
    name = "get_booking_page_settings"
    description = "Get the online booking page configuration."
    module_id = "online_booking"
    required_permission = "online_booking.view_onlinebooking"
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from online_booking.models import BookingPageSettings
        try:
            s = BookingPageSettings.objects.first()
            if not s:
                return {"is_enabled": False, "message": "Booking page not configured"}
            return {
                "is_enabled": s.is_enabled,
                "page_title": s.page_title,
                "min_advance_hours": s.min_advance_hours,
                "max_advance_days": s.max_advance_days,
                "slot_duration_minutes": s.slot_duration_minutes,
                "buffer_minutes": s.buffer_minutes,
                "allow_staff_selection": s.allow_staff_selection,
            }
        except Exception:
            return {"is_enabled": False, "message": "Booking page not configured"}
