"""
Online Booking Module Views

Admin views for managing online bookings and booking page settings.
The public-facing booking page will be built separately.
"""

from datetime import date, timedelta

from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render as django_render
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.accounts.decorators import login_required, permission_required
from apps.core.htmx import htmx_view
from apps.modules_runtime.navigation import with_module_nav

from .models import BookingPageSettings, OnlineBooking
from .forms import BookingPageSettingsForm, CancelBookingForm


# ============================================================================
# Constants
# ============================================================================

BOOKING_SORT_FIELDS = {
    'reference': 'booking_reference',
    'customer': 'customer_name',
    'service': 'service_name',
    'date': 'booking_date',
    'status': 'status',
    'created': 'created_at',
}

PER_PAGE_CHOICES = [10, 25, 50, 100]


def _hub_id(request):
    return request.session.get('hub_id')


def _render_bookings_list(request, hub_id, per_page=10):
    """Re-render the bookings list partial after a mutation."""
    bookings = OnlineBooking.objects.filter(
        hub_id=hub_id, is_deleted=False,
    ).order_by('-booking_date', '-booking_time')
    paginator = Paginator(bookings, per_page)
    page_obj = paginator.get_page(1)
    return django_render(request, 'online_booking/partials/bookings_list.html', {
        'bookings': page_obj,
        'page_obj': page_obj,
        'search_query': '',
        'sort_field': 'date',
        'sort_dir': 'desc',
        'status_filter': '',
        'date_from': '',
        'date_to': '',
        'per_page': per_page,
    })


# ============================================================================
# Dashboard
# ============================================================================

@login_required
@with_module_nav('online_booking', 'dashboard')
@htmx_view('online_booking/pages/dashboard.html', 'online_booking/partials/dashboard_content.html')
def dashboard(request):
    """Online Booking dashboard with stats and upcoming bookings."""
    hub = _hub_id(request)
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    settings = BookingPageSettings.get_settings(hub)

    # Stats
    all_bookings = OnlineBooking.objects.filter(hub_id=hub, is_deleted=False)
    pending_count = all_bookings.filter(status=OnlineBooking.Status.PENDING).count()
    confirmed_today = all_bookings.filter(
        status=OnlineBooking.Status.CONFIRMED,
        booking_date=today,
    ).count()
    total_this_week = all_bookings.filter(
        booking_date__gte=week_start,
        booking_date__lte=week_end,
    ).count()

    # No-show rate calculation
    completed_and_noshow = all_bookings.filter(
        status__in=[OnlineBooking.Status.COMPLETED, OnlineBooking.Status.NO_SHOW],
    )
    total_finished = completed_and_noshow.count()
    no_show_count = completed_and_noshow.filter(status=OnlineBooking.Status.NO_SHOW).count()
    no_show_rate = round((no_show_count / total_finished * 100), 1) if total_finished > 0 else 0

    # Upcoming bookings (next 7 days, pending or confirmed)
    upcoming_bookings = all_bookings.filter(
        booking_date__gte=today,
        booking_date__lte=today + timedelta(days=7),
        status__in=[OnlineBooking.Status.PENDING, OnlineBooking.Status.CONFIRMED],
    ).order_by('booking_date', 'booking_time')[:10]

    return {
        'settings': settings,
        'pending_count': pending_count,
        'confirmed_today': confirmed_today,
        'total_this_week': total_this_week,
        'no_show_rate': no_show_rate,
        'no_show_count': no_show_count,
        'upcoming_bookings': upcoming_bookings,
    }


# ============================================================================
# Bookings List (Datatable)
# ============================================================================

@login_required
@with_module_nav('online_booking', 'bookings')
@htmx_view('online_booking/pages/bookings.html', 'online_booking/partials/bookings_content.html')
def bookings_list(request):
    """Bookings list with search, sort, filter, pagination."""
    hub = _hub_id(request)
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'date')
    sort_dir = request.GET.get('dir', 'desc')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    per_page = int(request.GET.get('per_page', 10))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 10

    bookings = OnlineBooking.objects.filter(hub_id=hub, is_deleted=False)

    # Status filter
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    # Date range filter
    if date_from:
        bookings = bookings.filter(booking_date__gte=date_from)
    if date_to:
        bookings = bookings.filter(booking_date__lte=date_to)

    # Search
    if search_query:
        bookings = bookings.filter(
            Q(booking_reference__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(service_name__icontains=search_query) |
            Q(customer_email__icontains=search_query) |
            Q(customer_phone__icontains=search_query) |
            Q(staff_name__icontains=search_query)
        )

    # Sort
    order_by = BOOKING_SORT_FIELDS.get(sort_field, 'booking_date')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    bookings = bookings.order_by(order_by)

    # Pagination
    paginator = Paginator(bookings, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'bookings': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_field': sort_field,
        'sort_dir': sort_dir,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'per_page': per_page,
    }

    # HTMX partial: swap only datatable body
    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'online_booking/partials/bookings_list.html', context)

    return context


# ============================================================================
# Booking Actions
# ============================================================================

@login_required
@require_POST
def booking_confirm(request, booking_id):
    """Confirm a pending booking."""
    hub = _hub_id(request)
    booking = get_object_or_404(
        OnlineBooking, id=booking_id, hub_id=hub, is_deleted=False,
    )

    if booking.status != OnlineBooking.Status.PENDING:
        messages.error(request, _('Only pending bookings can be confirmed.'))
        return _render_bookings_list(request, hub)

    booking.confirm()
    messages.success(request, _('Booking %(ref)s confirmed successfully.') % {'ref': booking.booking_reference})
    return _render_bookings_list(request, hub)


@login_required
@require_POST
def booking_cancel(request, booking_id):
    """Cancel a booking."""
    hub = _hub_id(request)
    booking = get_object_or_404(
        OnlineBooking, id=booking_id, hub_id=hub, is_deleted=False,
    )

    if booking.status in [OnlineBooking.Status.CANCELLED, OnlineBooking.Status.COMPLETED]:
        messages.error(request, _('This booking cannot be cancelled.'))
        return _render_bookings_list(request, hub)

    reason = request.POST.get('reason', '').strip()
    booking.cancel(reason=reason)
    messages.success(request, _('Booking %(ref)s cancelled.') % {'ref': booking.booking_reference})
    return _render_bookings_list(request, hub)


@login_required
@require_POST
def booking_complete(request, booking_id):
    """Mark a booking as completed."""
    hub = _hub_id(request)
    booking = get_object_or_404(
        OnlineBooking, id=booking_id, hub_id=hub, is_deleted=False,
    )

    if booking.status != OnlineBooking.Status.CONFIRMED:
        messages.error(request, _('Only confirmed bookings can be marked as completed.'))
        return _render_bookings_list(request, hub)

    booking.complete()
    messages.success(request, _('Booking %(ref)s completed.') % {'ref': booking.booking_reference})
    return _render_bookings_list(request, hub)


@login_required
@require_POST
def booking_no_show(request, booking_id):
    """Mark a booking as no-show."""
    hub = _hub_id(request)
    booking = get_object_or_404(
        OnlineBooking, id=booking_id, hub_id=hub, is_deleted=False,
    )

    if booking.status != OnlineBooking.Status.CONFIRMED:
        messages.error(request, _('Only confirmed bookings can be marked as no-show.'))
        return _render_bookings_list(request, hub)

    booking.mark_no_show()
    messages.success(request, _('Booking %(ref)s marked as no-show.') % {'ref': booking.booking_reference})
    return _render_bookings_list(request, hub)


@login_required
@require_POST
def booking_delete(request, booking_id):
    """Soft delete a booking."""
    hub = _hub_id(request)
    booking = get_object_or_404(
        OnlineBooking, id=booking_id, hub_id=hub, is_deleted=False,
    )

    booking.is_deleted = True
    booking.deleted_at = timezone.now()
    booking.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    messages.success(request, _('Booking %(ref)s deleted.') % {'ref': booking.booking_reference})
    return _render_bookings_list(request, hub)


@login_required
@require_POST
def booking_bulk_action(request):
    """Bulk confirm, cancel, or delete bookings."""
    hub = _hub_id(request)
    ids_str = request.POST.get('ids', '')
    action = request.POST.get('action', '')

    if not ids_str or not action:
        return _render_bookings_list(request, hub)

    ids = [uid.strip() for uid in ids_str.split(',') if uid.strip()]
    bookings = OnlineBooking.objects.filter(hub_id=hub, id__in=ids, is_deleted=False)
    count = bookings.count()

    if action == 'confirm':
        updated = bookings.filter(status=OnlineBooking.Status.PENDING).update(
            status=OnlineBooking.Status.CONFIRMED,
            confirmed_at=timezone.now(),
        )
        messages.success(request, _('%(count)d bookings confirmed.') % {'count': updated})
    elif action == 'cancel':
        updated = bookings.exclude(
            status__in=[OnlineBooking.Status.CANCELLED, OnlineBooking.Status.COMPLETED],
        ).update(
            status=OnlineBooking.Status.CANCELLED,
            cancelled_at=timezone.now(),
        )
        messages.success(request, _('%(count)d bookings cancelled.') % {'count': updated})
    elif action == 'delete':
        bookings.update(is_deleted=True, deleted_at=timezone.now())
        messages.success(request, _('%(count)d bookings deleted.') % {'count': count})

    return _render_bookings_list(request, hub)


# ============================================================================
# Settings
# ============================================================================

@login_required
@permission_required('online_booking.manage_settings')
@with_module_nav('online_booking', 'settings')
@htmx_view('online_booking/pages/settings.html', 'online_booking/partials/settings_content.html')
def settings_view(request):
    """Booking page settings management."""
    hub = _hub_id(request)
    settings = BookingPageSettings.get_settings(hub)

    if request.method == 'POST':
        form = BookingPageSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, _('Booking page settings saved successfully.'))
            # Re-fetch to ensure fresh data
            settings = BookingPageSettings.get_settings(hub)
            form = BookingPageSettingsForm(instance=settings)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = BookingPageSettingsForm(instance=settings)

    # Stats for the settings page
    total_bookings = OnlineBooking.objects.filter(hub_id=hub, is_deleted=False).count()
    pending_bookings = OnlineBooking.objects.filter(
        hub_id=hub, is_deleted=False, status=OnlineBooking.Status.PENDING,
    ).count()

    return {
        'settings': settings,
        'form': form,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
    }
