from django.db import models
from django.utils import timezone


class Debtor(models.Model):
    TRUST_LEVEL_LOW = 'low'
    TRUST_LEVEL_MEDIUM = 'medium'
    TRUST_LEVEL_HIGH = 'high'

    TRUST_LEVEL_CHOICES = [
        (TRUST_LEVEL_LOW, 'Baixo'),
        (TRUST_LEVEL_MEDIUM, 'Médio'),
        (TRUST_LEVEL_HIGH, 'Alto'),
    ]

    company = models.ForeignKey(
        'users.Company',
        on_delete=models.CASCADE,
        related_name='debtors',
    )
    name = models.CharField(max_length=200)
    whatsapp = models.CharField(max_length=50, blank=True)
    trust_level = models.CharField(
        max_length=10,
        choices=TRUST_LEVEL_CHOICES,
        default=TRUST_LEVEL_MEDIUM,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Debtors'

    def __str__(self):
        return self.name
