from django.db import models
from django.utils import timezone
from decimal import Decimal


class Loan(models.Model):
    """
    Modelo para controlar empréstimos
    """
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('paid', 'Pago'),
        ('overdue', 'Atrasado'),
        ('cancelled', 'Cancelado'),
    ]

    debtor = models.ForeignKey(
        'customers.Debtor',
        on_delete=models.CASCADE,
        related_name='loans'
    )
    company = models.ForeignKey(
        'users.Company',
        on_delete=models.CASCADE,
        related_name='loans',
    )
    
    # Informações básicas do empréstimo
    amount_borrowed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor inicial emprestado"
    )
    loan_date = models.DateField(
        default=timezone.now,
        help_text="Data do empréstimo"
    )
    due_date = models.DateField(
        help_text="Data combinada para pagamento"
    )
    
    # Configuração de juros
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Taxa de juros em percentual (ex: 5.00 para 5%)"
    )
    
    # Configuração de parcelamento
    num_installments = models.IntegerField(
        default=1,
        help_text="Número de parcelas"
    )
    first_payment_date = models.DateField(
        help_text="Data do primeiro pagamento"
    )
    
    # Campos calculados
    final_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        help_text="Valor final com juros"
    )
    installment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        help_text="Valor de cada parcela"
    )
    total_interest = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        help_text="Total de juros a pagar"
    )
    
    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    notes = models.TextField(
        blank=True,
        help_text="Notas adicionais sobre o empréstimo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-loan_date']
        verbose_name_plural = 'Loans'

    def __str__(self):
        return f"Empréstimo de {self.debtor.name} - R$ {self.amount_borrowed}"

    def save(self, *args, **kwargs):
        """Calcula os juros e as parcelas antes de salvar"""
        self.calculate_interest_and_installments()
        super().save(*args, **kwargs)

    def calculate_interest_and_installments(self):
        """
        Calcula juros simples com ajustes por:
        1. Número de parcelas (quanto mais parcelas, maior o juro)
        2. Dias até o primeiro pagamento (quanto mais distante, maior o juro)
        """
        base_rate = Decimal(str(self.interest_rate))
        
        # Ajuste por número de parcelas
        # A cada parcela adicional, aumenta 0.5% na taxa
        installment_adjustment = Decimal(str(max(0, self.num_installments - 1) * 0.5))
        
        # Ajuste por dias até o primeiro pagamento
        # A cada 30 dias, aumenta 1% na taxa
        days_to_first_payment = (self.first_payment_date - self.loan_date).days
        payment_delay_adjustment = Decimal(str(days_to_first_payment / 30))
        
        # Taxa final = taxa base + ajustes
        final_rate = base_rate + installment_adjustment + payment_delay_adjustment
        
        # Cálculo de juros simples: J = C * i * t
        # Onde C é capital, i é taxa (em decimal), t é tempo em períodos
        # Usando anos como período base
        time_in_years = Decimal(str((self.due_date - self.loan_date).days / 365))
        
        interest = self.amount_borrowed * (final_rate / Decimal('100')) * time_in_years
        
        # Arredonda para 2 casas decimais
        self.total_interest = interest.quantize(Decimal('0.01'))
        self.final_amount = (self.amount_borrowed + self.total_interest).quantize(Decimal('0.01'))
        self.installment_amount = (self.final_amount / Decimal(str(self.num_installments))).quantize(Decimal('0.01'))

    def get_paid_amount(self):
        """Retorna o valor total já pago"""
        return sum(payment.amount for payment in self.payments.filter(status='paid'))

    def get_remaining_amount(self):
        """Retorna o valor restante a pagar"""
        return self.final_amount - self.get_paid_amount()

    def get_paid_installments(self):
        """Retorna o número de parcelas já pagas"""
        return self.payments.filter(status='paid').count()

    def get_pending_installments(self):
        """Retorna o número de parcelas pendentes"""
        return self.payments.filter(status='pending').count()


class LoanPayment(models.Model):
    """
    Modelo para controlar parcelas/pagamentos do empréstimo
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('overdue', 'Atrasado'),
    ]

    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    # Informações da parcela
    installment_number = models.IntegerField(
        help_text="Número da parcela (1, 2, 3...)"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor da parcela"
    )
    due_date = models.DateField(
        help_text="Data prevista para pagamento"
    )
    
    # Status do pagamento
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    paid_date = models.DateField(
        null=True,
        blank=True,
        help_text="Data em que foi realmente pago"
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor que foi efetivamente pago (em caso de variação)"
    )
    
    # Extras
    notes = models.TextField(
        blank=True,
        help_text="Notas sobre o pagamento"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['loan', 'installment_number']
        unique_together = ('loan', 'installment_number')
        verbose_name_plural = 'Loan Payments'

    def __str__(self):
        return f"Parcela {self.installment_number} - {self.loan.debtor.name}"
