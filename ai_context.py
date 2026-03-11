"""
AI context for the Online Booking module.
Loaded into the assistant system prompt when this module's tools are active.
"""

CONTEXT = """
## Module Knowledge: Online Booking

### Models

**BookingPageSettings** (singleton per hub)
- `is_enabled` (BooleanField) — whether the public booking page is live
- `page_title`, `welcome_message`, `primary_color`, `logo_url` — page customization
- `require_phone`, `require_email` (BooleanField) — required customer fields
- `allow_staff_selection`, `allow_notes` (BooleanField) — booking options
- `min_advance_hours` (default 2), `max_advance_days` (default 30) — booking window rules
- `slot_duration_minutes` (default 30), `buffer_minutes` (default 0) — scheduling config
- `confirmation_message`, `cancellation_policy` — text shown to customers
- Use `BookingPageSettings.get_settings(hub_id)` to get or create

**OnlineBooking**
- `booking_reference` (CharField) — auto-generated format: BK-00001, BK-00002, ...
- `customer` (FK → customers.Customer, nullable) — linked if an existing customer is found
- `customer_name`, `customer_email`, `customer_phone` — raw form data always stored
- `service_id` (UUIDField, nullable), `service_name` (CharField) — booked service
- `staff_id` (UUIDField, nullable), `staff_name` (CharField) — assigned staff
- `booking_date` (DateField), `booking_time` (TimeField), `duration_minutes` (default 30)
- `status` — choices: pending, confirmed, cancelled, completed, no_show
- `notes` — customer notes
- `confirmed_at`, `cancelled_at`, `cancellation_reason` — status timestamps

### Key flows

1. **New booking**: Create OnlineBooking with customer info, service, date/time, and status='pending'. Reference is auto-generated.
2. **Confirm**: Call `.confirm()` → sets status='confirmed' and records `confirmed_at`.
3. **Cancel**: Call `.cancel(reason='...')` → sets status='cancelled', records `cancelled_at` and reason.
4. **Complete**: Call `.complete()` → sets status='completed'.
5. **No-show**: Call `.mark_no_show()` → sets status='no_show'.
6. **Link to customer**: If customer exists in the customers module, set the `customer` FK; always keep the raw name/email/phone fields.

### Relationships
- `customer` FK → customers.Customer (SET_NULL on delete)
- `service_id` / `staff_id` are UUID references stored as plain fields (not FKs) for resilience
- `online_payments` module can request a deposit via PaymentTransaction linked to this booking
"""
