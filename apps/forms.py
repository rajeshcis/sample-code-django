"""Django forms."""

from django import forms
from django_select2.forms import ModelSelect2Widget
from orders.models import OrderPreference
from ghana_location_api.models import Regions
from user_profile.models import CustomUser


# These widgets for the admin to implement select 2 in all choice fields.

class RegionWidget(ModelSelect2Widget):
    """User select2 dropdown widget for django admin."""

    model = Regions
    search_fields = [
        'region__icontains',
        'code__icontains',
    ]


class CustomUserWidget(ModelSelect2Widget):
    """User select2 dropdown widget for django admin."""

    model = CustomUser
    search_fields = [
        'first_name__icontains',
        'last_name__icontains',
        'email__icontains',
        'street__icontains',
        'city__icontains',
        'region__icontains',
        'phone_number__icontains',
        'professional_skills__professional_skills__icontains',
    ]

    def label_from_instance(self, obj):
        """Return name instead of email by default."""
        if obj.first_name and obj.last_name:
            return (str(obj.first_name) + " " + str(obj.last_name)).upper()
        elif obj.first_name:
            return str(obj.first_name).upper()
        elif obj.last_name:
            return str(obj.last_name).upper()
        else:
            return str(obj.email).upper()


class OrderPreferenceSelect2WidgetForm(forms.ModelForm):
    """OrderPreference select2 choice widget form for django admin."""

    class Meta:
        """Override choice fields with select2."""

        model = OrderPreference
        exclude = ('suburb', "paymnt_done_mail_send", "is_tutor_alloted")
        widgets = {
            "region": RegionWidget(),
            "user": CustomUserWidget(),
        }
