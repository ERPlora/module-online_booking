# Online Booking

## Overview

| Property | Value |
|----------|-------|
| **Module ID** | `online_booking` |
| **Version** | `1.0.0` |
| **Icon** | `globe-outline` |
| **Dependencies** | `customers` |

## Dependencies

This module requires the following modules to be installed:

- `customers`

## Models

### `BookingPageSettings`

Configuration for the public online booking page.
One record per hub (singleton pattern via unique_together on hub_id).

| Field | Type | Details |
|-------|------|---------|
| `is_enabled` | BooleanField |  |
| `page_title` | CharField | max_length=255 |
| `welcome_message` | TextField | optional |
| `primary_color` | CharField | max_length=20 |
| `logo_url` | CharField | max_length=500, optional |
| `require_phone` | BooleanField |  |
| `require_email` | BooleanField |  |
| `allow_staff_selection` | BooleanField |  |
| `allow_notes` | BooleanField |  |
| `min_advance_hours` | IntegerField |  |
| `max_advance_days` | IntegerField |  |
| `slot_duration_minutes` | IntegerField |  |
| `buffer_minutes` | IntegerField |  |
| `confirmation_message` | TextField | optional |
| `cancellation_policy` | TextField | optional |

**Methods:**

- `get_settings()` — Get or create the settings singleton for a hub.
Returns the BookingPageSettings instance.

### `OnlineBooking`

An individual booking record submitted via the public booking page
or created manually from the admin panel.

| Field | Type | Details |
|-------|------|---------|
| `booking_reference` | CharField | max_length=20 |
| `customer` | ForeignKey | → `customers.Customer`, on_delete=SET_NULL, optional |
| `customer_name` | CharField | max_length=255 |
| `customer_email` | EmailField | max_length=254, optional |
| `customer_phone` | CharField | max_length=50, optional |
| `service_id` | UUIDField | max_length=32, optional |
| `service_name` | CharField | max_length=255 |
| `staff_id` | UUIDField | max_length=32, optional |
| `staff_name` | CharField | max_length=255, optional |
| `booking_date` | DateField |  |
| `booking_time` | TimeField |  |
| `duration_minutes` | IntegerField |  |
| `status` | CharField | max_length=20, choices: pending, confirmed, cancelled, completed, no_show |
| `notes` | TextField | optional |
| `confirmed_at` | DateTimeField | optional |
| `cancelled_at` | DateTimeField | optional |
| `cancellation_reason` | TextField | optional |

**Methods:**

- `confirm()` — Confirm a pending booking.
- `cancel()` — Cancel a booking.
- `complete()` — Mark a booking as completed.
- `mark_no_show()` — Mark a booking as no-show.

**Properties:**

- `booking_datetime` — Combine booking_date and booking_time into a datetime.
- `is_past` — Check if the booking date/time is in the past.

## Cross-Module Relationships

| From | Field | To | on_delete | Nullable |
|------|-------|----|-----------|----------|
| `OnlineBooking` | `customer` | `customers.Customer` | SET_NULL | Yes |

## URL Endpoints

Base path: `/m/online_booking/`

| Path | Name | Method |
|------|------|--------|
| `(root)` | `dashboard` | GET |
| `bookings/` | `bookings` | GET |
| `bookings/<uuid:booking_id>/confirm/` | `confirm` | GET |
| `bookings/<uuid:booking_id>/cancel/` | `cancel` | GET |
| `bookings/<uuid:booking_id>/complete/` | `complete` | GET |
| `bookings/<uuid:booking_id>/no-show/` | `no_show` | GET |
| `bookings/<uuid:booking_id>/delete/` | `delete` | GET/POST |
| `bookings/bulk/` | `bulk_action` | GET/POST |
| `settings/` | `settings` | GET |

## Permissions

| Permission | Description |
|------------|-------------|
| `online_booking.view_booking` | View Booking |
| `online_booking.change_booking` | Change Booking |
| `online_booking.delete_booking` | Delete Booking |
| `online_booking.confirm_booking` | Confirm Booking |
| `online_booking.manage_settings` | Manage Settings |

**Role assignments:**

- **admin**: All permissions
- **manager**: `change_booking`, `confirm_booking`, `view_booking`
- **employee**: `view_booking`

## Navigation

| View | Icon | ID | Fullpage |
|------|------|----|----------|
| Dashboard | `speedometer-outline` | `dashboard` | No |
| Bookings | `calendar-outline` | `bookings` | No |
| Settings | `settings-outline` | `settings` | No |

## AI Tools

Tools available for the AI assistant:

### `list_online_bookings`

List online bookings with optional filters.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter: pending, confirmed, cancelled, completed, no_show |
| `date` | string | No | Filter by date (YYYY-MM-DD) |
| `limit` | integer | No | Max results (default 20) |

### `get_booking_page_settings`

Get the online booking page configuration.

### `get_online_booking`

Get details of a specific online booking.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `booking_id` | string | Yes | Booking ID |

### `update_booking_status`

Update booking status: confirm (pending→confirmed), cancel, complete, no_show. Uses model methods for safe transitions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `booking_id` | string | Yes | Booking ID |
| `action` | string | Yes | Action: confirm, cancel, complete, no_show |
| `reason` | string | No | Cancellation reason (for cancel action) |

### `create_online_booking`

Manually create an online booking.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_name` | string | Yes | Customer name |
| `customer_email` | string | No | Customer email |
| `customer_phone` | string | No | Customer phone |
| `service_name` | string | Yes | Service name |
| `staff_name` | string | No | Staff member name |
| `booking_date` | string | Yes | Date (YYYY-MM-DD) |
| `booking_time` | string | Yes | Time (HH:MM) |
| `duration_minutes` | integer | No | Duration in minutes |
| `notes` | string | No | Booking notes |

## File Structure

```
README.md
__init__.py
admin.py
ai_tools.py
apps.py
forms.py
locale/
  en/
    LC_MESSAGES/
      django.po
  es/
    LC_MESSAGES/
      django.po
migrations/
  0001_initial.py
  __init__.py
models.py
module.py
static/
  online_booking/
    css/
      booking.css
templates/
  online_booking/
    pages/
      bookings.html
      dashboard.html
      settings.html
    partials/
      bookings_content.html
      bookings_list.html
      dashboard_content.html
      settings_content.html
urls.py
views.py
```
