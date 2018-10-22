"""Registered and customize models and their fields with dajngo admin."""

from django.contrib import admin
from .forms import OrderPreferenceSelect2WidgetForm


class OrderPreferenceAdmin(admin.ModelAdmin):
    """Register Order Preferences model."""

    list_display = ['order_number', 'created', 'user', 'course', 'fee_paid', 'get_author']
    search_fields = ['course__title']
    filter_horizontal = ('tutor_suggestion',)
    form = OrderPreferenceSelect2WidgetForm

    def has_add_permission(self, request, obj=None):
        """Restrict add order preference as this record created by the user's request only."""
        return False

    class Media:
        """Add extra static files."""

        js = ('js/jquery.min.js',)
        css = {
            'all': ('css/admin_custom.css',)
        }
