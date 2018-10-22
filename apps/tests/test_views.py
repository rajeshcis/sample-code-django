# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse

from .constants import group_permissions
from post.models import Plan
from .base_testcases import PostAppWebTest
from .factories import PlanFactory, StaffFactory, give_permission, AdminFactory


def _plan_data():
    """Initial data for a plan test."""
    return {'plan_name': 'organization_test',
            'plan_location': 'HK', 'plan_status': 'AC'}


def _primary_contact_data():
    """Initial data for a contact test."""
    return {
        'salutation': 'Mr',
        'first_name': 'first_test',
        'last_name': 'last_test',
        'phone_number_idd': '+852',
        'phone_area_code': '456',
        'phone_number': '3698574123',
        'fax_number_idd': '+852',
        'fax_area_code': '123',
        'fax_number': '123456789',
        'address_line1': 'test address1',
        'address_line2': 'test address2',
        'address_line3': 'test address2',
        'email': 'test@test.com,test1@test.com',
    }


class PostTestBaseView(PostAppWebTest):
    """Base class to perform common and basic tests."""

    def setUp(self):
        """Setup initial data for the test."""
        self.plan = PlanFactory()
        self.url = reverse('apps.post.plan', args=())

    def test_user_login(self):
        """Test user login."""
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login/?next=', response['Location'])

    def test_get_without_post_management_permission(self):
        """
        Test without the post management permission.

        Test for Melco post enable is added by default.
        with permission check.
        """
        user = StaffFactory()
        response = self.app.get(self.url, user=user, expect_errors=True)
        self.assertEqual(response.status_code, 403)

    def test_get_with_post_management_permission(self):
        """
        Test with the post management permission.

        Test for Melco post enable is added by default.
        with permission check.
        """
        user = StaffFactory()
        settings.MELCO_post_ENABLED = True
        give_permission(user, group_permissions.TRAVEL_plan_MANAGE_ALL)
        response = self.app.get(self.url, user=user, expect_errors=True)
        self.assertEqual(response.status_code, 200)


class PlanListViewTest(PostTestBaseView):
    """Test plan list views."""

    def test_get(self):
        """Test get method for post view."""
        response = self.app.get(self.url, user=AdminFactory())
        self.assertEqual(response.status_code, 200)
        self.assertIn('Organization', response)

    def test_organization_filter(self):
        """Test list view with plan filter."""
        user = StaffFactory()
        give_permission(user, group_permissions.TRAVEL_plan_MANAGE_ALL)
        PlanFactory(plan_name='organization_test2', plan_location='HK')
        response = self.app.get(self.url + '?plan_name=&plan_location=', user=user, expect_errors=True)
        self.assertIn('organization_test2', response)

    def test_organization_filter_with_partial_name(self):
        """Test list view filter with partial organization name."""
        user = StaffFactory()
        give_permission(user, group_permissions.TRAVEL_plan_MANAGE_ALL)
        PlanFactory(plan_name='organization_test2', plan_location='HK')
        PlanFactory(plan_name='different_name', plan_location='HK')
        response = self.app.get(self.url + '?plan_name=organization&plan_location=', user=user, expect_errors=True)
        self.assertIn('organization_test2', response)
        self.assertNotIn('different_name', response)


class PlanCreateViewTest(PostTestBaseView):
    """Test plan create views."""

    csrf_checks = False

    def setUp(self):
        """Override Setup method for this test."""
        self.url = reverse('apps.post.plan.create', args=())

    def test_post_method_without_primary_contact(self):
        """Test Organization creation without primary contact."""
        response = self.app.post(self.url, user=AdminFactory(), params=_plan_data())
        self.assertEqual(response.status_code, 200)
        self.assertIn('Please enter all the required fields.', response)
        queryset = Plan.objects.all()
        self.assertEqual(len(queryset), 0)

    def test_post_method_with_primary_contact(self):
        """Test organization create with primary contact creation."""
        user = StaffFactory()
        give_permission(user, group_permissions.TRAVEL_plan_MANAGE_ALL)
        response = self.app.get(self.url, user=user)
        form = response.forms[0]
        form['plan_name'] = 'test_organization'
        form['plan_status'] = 'AC'
        form['plan_location'] = 'HK'
        form['salutation'] = 'Mr'
        form['first_name'] = 'test'
        form['last_name'] = 'test'
        form['email'] = 'test@test.com'
        response = form.submit('submit', user=user)
        self.assertEqual(response.status_code, 302)
        queryset = Plan.objects.all()
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].plan_contacts.count(), 1)
        self.assertIn(reverse('apps.post.plan', args=()), response['location'])

    def test_duplicate_plan_creation(self):
        """Test creation of the duplicate plan."""
        PlanFactory(plan_name='test_organization')
        user = StaffFactory()
        give_permission(user, group_permissions.TRAVEL_plan_MANAGE_ALL)
        response = self.app.get(self.url, user=user)
        form = response.forms[0]
        form['plan_name'] = 'test_organization'
        form['plan_status'] = 'AC'
        form['plan_location'] = 'HK'
        form['salutation'] = 'Mr'
        form['first_name'] = 'test'
        form['last_name'] = 'test'
        form['email'] = 'test@test.com'
        response = form.submit('submit', user=user)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Organization with this Organization Name already exists.', response)
        queryset = Plan.objects.all()
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].plan_contacts.count(), 0)
