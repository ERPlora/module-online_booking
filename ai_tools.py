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


@register_tool
class GetOnlineBooking(AssistantTool):
    name = "get_online_booking"
    description = "Get details of a specific online booking."
    module_id = "online_booking"
    required_permission = "online_booking.view_onlinebooking"
    parameters = {
        "type": "object",
        "properties": {"booking_id": {"type": "string", "description": "Booking ID"}},
        "required": ["booking_id"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from online_booking.models import OnlineBooking
        b = OnlineBooking.objects.get(id=args['booking_id'])
        return {
            "id": str(b.id), "booking_reference": b.booking_reference,
            "customer_name": b.customer_name, "customer_email": b.customer_email,
            "customer_phone": b.customer_phone,
            "service_name": b.service_name, "staff_name": b.staff_name,
            "booking_date": str(b.booking_date), "booking_time": str(b.booking_time),
            "duration_minutes": b.duration_minutes, "status": b.status,
            "notes": b.notes,
            "confirmed_at": b.confirmed_at.isoformat() if b.confirmed_at else None,
            "cancelled_at": b.cancelled_at.isoformat() if b.cancelled_at else None,
            "cancellation_reason": b.cancellation_reason,
        }


@register_tool
class UpdateBookingStatus(AssistantTool):
    name = "update_booking_status"
    description = "Update booking status: confirm (pending→confirmed), cancel, complete, no_show. Uses model methods for safe transitions."
    module_id = "online_booking"
    required_permission = "online_booking.change_onlinebooking"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "booking_id": {"type": "string", "description": "Booking ID"},
            "action": {"type": "string", "description": "Action: confirm, cancel, complete, no_show"},
            "reason": {"type": "string", "description": "Cancellation reason (for cancel action)"},
        },
        "required": ["booking_id", "action"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from online_booking.models import OnlineBooking
        b = OnlineBooking.objects.get(id=args['booking_id'])
        action = args['action']
        try:
            if action == 'confirm':
                b.confirm()
            elif action == 'cancel':
                b.cancel(reason=args.get('reason', ''))
            elif action == 'complete':
                b.complete()
            elif action == 'no_show':
                b.mark_no_show()
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": str(e)}
        return {"id": str(b.id), "booking_reference": b.booking_reference, "status": b.status}


@register_tool
class CreateOnlineBooking(AssistantTool):
    name = "create_online_booking"
    description = "Manually create an online booking."
    module_id = "online_booking"
    required_permission = "online_booking.add_onlinebooking"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "customer_name": {"type": "string", "description": "Customer name"},
            "customer_email": {"type": "string", "description": "Customer email"},
            "customer_phone": {"type": "string", "description": "Customer phone"},
            "service_name": {"type": "string", "description": "Service name"},
            "staff_name": {"type": "string", "description": "Staff member name"},
            "booking_date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
            "booking_time": {"type": "string", "description": "Time (HH:MM)"},
            "duration_minutes": {"type": "integer", "description": "Duration in minutes"},
            "notes": {"type": "string", "description": "Booking notes"},
        },
        "required": ["customer_name", "service_name", "booking_date", "booking_time"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from online_booking.models import OnlineBooking
        b = OnlineBooking.objects.create(
            customer_name=args['customer_name'],
            customer_email=args.get('customer_email', ''),
            customer_phone=args.get('customer_phone', ''),
            service_name=args['service_name'],
            staff_name=args.get('staff_name', ''),
            booking_date=args['booking_date'],
            booking_time=args['booking_time'],
            duration_minutes=args.get('duration_minutes', 60),
            notes=args.get('notes', ''),
            status='pending',
        )
        return {"id": str(b.id), "booking_reference": b.booking_reference, "status": "pending", "created": True}
