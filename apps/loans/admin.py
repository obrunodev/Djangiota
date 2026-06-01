from django.contrib import admin
from django.utils.html import format_html
from .models import Loan, LoanPayment


class LoanPaymentInline(admin.TabularInline):
    """Inline para mostrar pagamentos dentro do empréstimo"""
    model = LoanPayment
    extra = 1
    fields = ('installment_number', 'amount', 'due_date', 'status', 'paid_date', 'paid_amount', 'notes')
    readonly_fields = ('installment_number', 'amount')


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """Admin para gerenciar empréstimos"""
    list_display = (
        'id',
        'debtor',
        'amount_display',
        'interest_rate_display',
        'final_amount_display',
        'status_display',
        'loan_date',
        'due_date',
    )
    list_filter = ('status', 'loan_date', 'company', 'interest_rate')
    search_fields = ('debtor__name', 'notes')
    readonly_fields = (
        'final_amount',
        'total_interest',
        'installment_amount',
        'created_at',
        'updated_at',
    )
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('debtor', 'company', 'status')
        }),
        ('Detalhes do Empréstimo', {
            'fields': (
                'amount_borrowed',
                'loan_date',
                'due_date',
                'notes',
            )
        }),
        ('Configuração de Juros e Parcelamento', {
            'fields': (
                'interest_rate',
                'num_installments',
                'first_payment_date',
            )
        }),
        ('Cálculos', {
            'fields': (
                'total_interest',
                'final_amount',
                'installment_amount',
            ),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [LoanPaymentInline]
    date_hierarchy = 'loan_date'

    def amount_display(self, obj):
        return f"R$ {obj.amount_borrowed:,.2f}"
    amount_display.short_description = "Valor Emprestado"

    def interest_rate_display(self, obj):
        return f"{obj.interest_rate}%"
    interest_rate_display.short_description = "Taxa de Juros"

    def final_amount_display(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">R$ {}</span>',
            'green' if obj.final_amount == obj.amount_borrowed else 'red',
            f"{obj.final_amount:,.2f}"
        )
    final_amount_display.short_description = "Valor Final"

    def status_display(self, obj):
        colors = {
            'active': '#007bff',
            'paid': '#28a745',
            'overdue': '#dc3545',
            'cancelled': '#6c757d',
        }
        color = colors.get(obj.status, '#007bff')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = "Status"


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    """Admin para gerenciar pagamentos/parcelas"""
    list_display = (
        'id',
        'loan_display',
        'installment_number',
        'amount_display',
        'due_date',
        'status_display',
        'paid_date',
    )
    list_filter = ('status', 'due_date', 'loan__company')
    search_fields = ('loan__debtor__name', 'notes')
    readonly_fields = ('loan', 'installment_number', 'amount', 'created_at', 'updated_at')
    fieldsets = (
        ('Informações da Parcela', {
            'fields': ('loan', 'installment_number', 'amount', 'due_date')
        }),
        ('Pagamento', {
            'fields': ('status', 'paid_date', 'paid_amount', 'notes')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'due_date'

    def loan_display(self, obj):
        return f"{obj.loan.debtor.name}"
    loan_display.short_description = "Empréstimo"

    def amount_display(self, obj):
        return f"R$ {obj.amount:,.2f}"
    amount_display.short_description = "Valor"

    def status_display(self, obj):
        colors = {
            'pending': '#ffc107',
            'paid': '#28a745',
            'overdue': '#dc3545',
        }
        color = colors.get(obj.status, '#007bff')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = "Status"
