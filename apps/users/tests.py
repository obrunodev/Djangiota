from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Company, CompanyMembership


User = get_user_model()


class CompanySwitchingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='password')
        self.company_a = Company.objects.create(name='Alpha')
        self.company_b = Company.objects.create(name='Beta')
        CompanyMembership.objects.create(user=self.user, company=self.company_a)
        CompanyMembership.objects.create(user=self.user, company=self.company_b)
        self.client = Client()
        self.client.login(username='alice', password='password')

    def test_company_list_shows_assigned_companies(self):
        response = self.client.get(reverse('users:company_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alpha')
        self.assertContains(response, 'Beta')

    def test_switch_company_updates_session(self):
        response = self.client.get(reverse('users:switch_company', args=(self.company_b.id,)))
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(session.get('current_company_id'), self.company_b.id)

    def test_current_company_context_processor(self):
        session = self.client.session
        session['current_company_id'] = self.company_a.id
        session.save()

        response = self.client.get(reverse('users:company_list'))
        self.assertEqual(response.context['current_company'], self.company_a)
