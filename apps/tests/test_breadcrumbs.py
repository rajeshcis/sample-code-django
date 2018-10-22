# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from .breadcrumbs import get_post_breadcrumbs
from .base_testcases import BaseAppDjangoTest
from .factories import PlanFactory, PlanContactFactory


class GetOtaBreadcrumbsTest(BaseAppDjangoTest):
    @classmethod
    def setUpTestData(cls):
        cls.a = PlanFactory(plan_name='plan')
        cls.ac = PlanContactFactory(plan=cls.a, salutation='Dr', first_name='∏eople', last_name='∏erson')

    def _compare(self, bc, text, url):
        self.assertEqual(unicode(bc.text), text)
        self.assertEqual(bc.url, url)

    def test_returns_basic(self):
        bc = get_post_breadcrumbs()

        self.assertEqual(len(bc), 2)
        self._compare(bc[0], 'Post', '')
        self._compare(bc[1], 'Employer', reverse('apps.post.plan'))

    def test_returns_plan_string(self):
        bc = get_post_breadcrumbs(plan='åbcde')

        self.assertEqual(len(bc), 3)
        self._compare(bc[0], 'Post', '')
        self._compare(bc[1], 'Employer', reverse('apps.post.plan'))
        self._compare(bc[2], 'åbcde', '')

    def test_returns_plan_object(self):
        bc = get_post_breadcrumbs(plan=self.a)

        self.assertEqual(len(bc), 3)
        self._compare(bc[0], 'Post', '')
        self._compare(bc[1], 'Employer', reverse('apps.post.plan'))
        self._compare(bc[2], 'plan', reverse('apps.post.plan.details', args=(self.a.id,)))

    def test_return_contact_string(self):
        bc = get_post_breadcrumbs(contact='çdefg')

        self.assertEqual(len(bc), 4)
        self._compare(bc[0], 'Post', '')
        self._compare(bc[1], 'Employer', reverse('apps.post.plan'))
        self._compare(bc[2], 'Contacts', '')
        self._compare(bc[3], 'çdefg', '')
