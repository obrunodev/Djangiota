from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class User(AbstractUser):
    companies = models.ManyToManyField(
        Company,
        through='CompanyMembership',
        related_name='users',
        blank=True,
    )

    def is_member_of(self, company):
        return self.companies.filter(pk=company.pk).exists()

    def get_companies(self):
        return self.companies.all()


class CompanyMembership(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='company_memberships')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=50, blank=True, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'company')
        ordering = ['company__name']

    def __str__(self):
        return f'{self.user.username} @ {self.company.name}'
