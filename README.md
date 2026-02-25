# Online Booking Module

Public online appointment booking page for customers.

## Features

- Customizable public booking page with title, welcome message, logo, and accent color
- Booking status workflow: pending, confirmed, cancelled, completed, no-show
- Auto-generated booking references (BK-00001 format)
- Customer linking to existing customer records when available
- Service and staff selection with optional staff preference
- Configurable required fields (phone, email)
- Booking rules: minimum advance hours, maximum advance days, slot duration, buffer time
- Custom confirmation message and cancellation policy
- Status transition methods (confirm, cancel, complete, mark no-show)
- Cancellation reason tracking with timestamps

## Installation

This module is installed automatically via the ERPlora Marketplace.

**Dependencies**: Requires `customers` module.

## Configuration

Access settings via: **Menu > Online Booking > Settings**

Enable or disable the public booking page, customize its appearance, set required fields, configure booking rules (advance time limits, slot duration, buffer), and define confirmation and cancellation messages.

## Usage

Access via: **Menu > Online Booking**

### Views

| View | URL | Description |
|------|-----|-------------|
| Dashboard | `/m/online_booking/dashboard/` | Overview of booking activity and statistics |
| Bookings | `/m/online_booking/bookings/` | List and manage all online bookings |
| Settings | `/m/online_booking/settings/` | Configure booking page and rules |

## Models

| Model | Description |
|-------|-------------|
| `BookingPageSettings` | Per-hub singleton with page customization, required fields, booking rules, and messages |
| `OnlineBooking` | Individual booking record with customer info, service/staff details, date/time, status, and notes |

## Permissions

| Permission | Description |
|------------|-------------|
| `online_booking.view_booking` | View online bookings |
| `online_booking.change_booking` | Edit booking details |
| `online_booking.delete_booking` | Delete bookings |
| `online_booking.confirm_booking` | Confirm pending bookings |
| `online_booking.manage_settings` | Access and modify booking page settings |

## Integration with Other Modules

- **customers**: Links bookings to existing customer records via `Customer` foreign key. Customer data (name, email, phone) is also stored directly on the booking for resilience.

## License

MIT

## Author

ERPlora Team - support@erplora.com
