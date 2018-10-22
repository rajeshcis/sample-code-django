
from .forms import PlanCreateForm, PlanContactCreateForm
from .tests.test_views import _primary_contact_data
from apps.models import Plan, PlanContact
from .base_testcases import PostAppDjangoTest
from .factories import PlanFactory


class PlanCreateFormTest(PostAppDjangoTest):

    def test_valid_form(self):
        """Test the form valid."""
        form = PlanCreateForm({'plan_name': 'test',
                               'plan_status': 'AC',
                               'plan_location': 'HK'})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(len(Plan.objects.all()), 1)

    def test_invalid_form(self):
        """Test the form invalid and errors."""
        form = PlanCreateForm({'plan_status': 'AC',
                               'plan_location': 'HK'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['plan_name'],
                         ['This field is required.'])

    def test_for_duplicate_value(self):
        """Test the errors for duplicate entry."""
        PlanFactory(plan_name='test')
        form = PlanCreateForm({'plan_name': 'test',
                               'plan_status': 'AC',
                               'plan_location': 'HK'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['plan_name'],
                         ['Organization with this Organization Name already exists.'
                          ])


class PlanContactCreateFormTest(PostAppDjangoTest):

    def test_valid_form(self):
        """Test the form valid."""
        form = PlanContactCreateForm(_primary_contact_data())
        self.assertTrue(form.is_valid())
        contact = form.save(commit=False)
        contact.plan = PlanFactory()
        contact.save()
        self.assertTrue(len(PlanContact.objects.all()), 1)

    def test_invalid_form(self):
        """Test the form invalid and errors."""
        data = _primary_contact_data()
        data.pop('email')
        form = PlanContactCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'],
                         ['This field is required.'])
        self.assertEqual(len(PlanContact.objects.all()), 0)

    def test_invalid_email_address(self):
        """Test the invalid email address."""
        data = _primary_contact_data()
        data['email'] = 'wronogformate.com,test@test.com'
        form = PlanContactCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'],
                         ['Please enter correct email addresses'])
        self.assertEqual(len(PlanContact.objects.all()), 0)

    def test_email_address_without_comma_separator(self):
        """Test the invalid email address."""
        data = _primary_contact_data()
        data['email'] = 'test2@test.com test@test.com / test3@test.com'
        form = PlanContactCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'],
                         ['Please enter correct email addresses'])
        self.assertEqual(len(PlanContact.objects.all()), 0)
