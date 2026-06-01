from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Loan, LoanPayment
from .forms import LoanForm, LoanPaymentForm, LoanPaymentFormSet


class LoanListView(LoginRequiredMixin, ListView):
    """Lista todos os empréstimos da empresa"""
    model = Loan
    template_name = 'loans/loan_list.html'
    context_object_name = 'loans'
    paginate_by = 20

    def get_queryset(self):
        company = self.request.current_company
        queryset = Loan.objects.filter(company=company).select_related('debtor')
        
        # Filtro por status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtro por devedor
        debtor = self.request.GET.get('debtor')
        if debtor:
            queryset = queryset.filter(debtor_id=debtor)
        
        # Busca por nome do devedor
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(debtor__name__icontains=search) |
                Q(notes__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.current_company
        
        # Estatísticas
        context['total_borrowed'] = Loan.objects.filter(company=company).aggregate(
            total=Sum('amount_borrowed')
        )['total'] or Decimal('0.00')
        
        context['total_with_interest'] = Loan.objects.filter(company=company).aggregate(
            total=Sum('final_amount')
        )['total'] or Decimal('0.00')
        
        context['total_paid'] = LoanPayment.objects.filter(
            loan__company=company,
            status='paid'
        ).aggregate(
            total=Sum('paid_amount')
        )['total'] or Decimal('0.00')
        
        context['active_loans'] = Loan.objects.filter(
            company=company,
            status='active'
        ).count()
        
        # Status choices para filtro
        context['status_choices'] = Loan.STATUS_CHOICES
        
        return context


class LoanDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de um empréstimo"""
    model = Loan
    template_name = 'loans/loan_detail.html'
    context_object_name = 'loan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loan = self.get_object()
        
        # Informações de pagamentos
        context['payments'] = loan.payments.all().order_by('installment_number')
        context['paid_amount'] = loan.get_paid_amount()
        context['remaining_amount'] = loan.get_remaining_amount()
        context['paid_installments'] = loan.get_paid_installments()
        context['pending_installments'] = loan.get_pending_installments()
        
        return context


class LoanCreateView(LoginRequiredMixin, CreateView):
    """Criar novo empréstimo"""
    model = Loan
    form_class = LoanForm
    template_name = 'loans/loan_form.html'
    success_url = reverse_lazy('loan-list')

    def form_valid(self, form):
        form.instance.company = self.request.current_company
        response = super().form_valid(form)
        
        # Cria as parcelas automaticamente
        self.create_installments()
        
        return response

    def create_installments(self):
        """Cria as parcelas baseado nas configurações do empréstimo"""
        loan = self.object
        days_between = (loan.due_date - loan.first_payment_date).days
        
        for i in range(1, loan.num_installments + 1):
            # Calcula a data de cada parcela
            if loan.num_installments == 1:
                payment_date = loan.first_payment_date
            else:
                days_per_installment = days_between // (loan.num_installments - 1) if loan.num_installments > 1 else 0
                payment_date = loan.first_payment_date + timedelta(days=days_per_installment * (i - 1))
            
            LoanPayment.objects.create(
                loan=loan,
                installment_number=i,
                amount=loan.installment_amount,
                due_date=payment_date,
                status='pending'
            )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.current_company
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Novo Empréstimo'
        return context


class LoanUpdateView(LoginRequiredMixin, UpdateView):
    """Editar empréstimo existente"""
    model = Loan
    form_class = LoanForm
    template_name = 'loans/loan_form.html'
    success_url = reverse_lazy('loan-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.current_company
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Empréstimo'
        return context


class LoanDeleteView(LoginRequiredMixin, DeleteView):
    """Deletar empréstimo"""
    model = Loan
    template_name = 'loans/loan_confirm_delete.html'
    success_url = reverse_lazy('loan-list')


def loan_payment_create(request, loan_id):
    """Registrar pagamento de uma parcela"""
    loan = get_object_or_404(Loan, id=loan_id, company=request.current_company)
    
    # Pega as parcelas pendentes
    pending_payments = loan.payments.filter(status='pending').order_by('installment_number')
    
    if request.method == 'POST':
        form = LoanPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.loan = loan
            
            # Se não especificou a parcela, usa a primeira pendente
            if not hasattr(payment, 'installment_number') or not payment.installment_number:
                if pending_payments.exists():
                    payment.installment_number = pending_payments.first().installment_number
                    payment.amount = pending_payments.first().amount
            
            payment.save()
            return redirect('loan-detail', pk=loan.id)
    else:
        form = LoanPaymentForm()
    
    return render(request, 'loans/loan_payment_form.html', {
        'form': form,
        'loan': loan,
        'pending_payments': pending_payments,
    })


def loan_dashboard(request):
    """Dashboard com resumo dos empréstimos"""
    company = request.current_company
    
    # Empréstimos ativos
    active_loans = Loan.objects.filter(company=company, status='active')
    
    # Estatísticas
    stats = {
        'total_active_loans': active_loans.count(),
        'total_borrowed': active_loans.aggregate(Sum('amount_borrowed'))['amount_borrowed__sum'] or Decimal('0.00'),
        'total_with_interest': active_loans.aggregate(Sum('final_amount'))['final_amount__sum'] or Decimal('0.00'),
        'total_paid': LoanPayment.objects.filter(
            loan__company=company,
            status='paid'
        ).aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00'),
    }
    
    # Empréstimos vencidos
    overdue_loans = Loan.objects.filter(
        company=company,
        status='active',
        due_date__lt=datetime.now().date()
    )
    
    # Próximos pagamentos
    upcoming_payments = LoanPayment.objects.filter(
        loan__company=company,
        status='pending',
        due_date__gte=datetime.now().date()
    ).select_related('loan').order_by('due_date')[:10]
    
    context = {
        'stats': stats,
        'active_loans': active_loans[:5],
        'overdue_loans': overdue_loans,
        'upcoming_payments': upcoming_payments,
    }
    
    return render(request, 'loans/loan_dashboard.html', context)
