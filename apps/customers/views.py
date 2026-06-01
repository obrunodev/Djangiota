from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DebtorForm
from .models import Debtor


@login_required
def debtor_list(request):
    company = request.current_company
    if not company:
        return redirect('users:company_list')

    debtors = company.debtors.all()
    return render(
        request,
        'customers/client_list.html',
        {
            'company': company,
            'debtors': debtors,
        },
    )


@login_required
def debtor_create(request):
    company = request.current_company
    if not company:
        return redirect('users:company_list')

    form = DebtorForm(request.POST or None)
    if form.is_valid():
        debtor = form.save(commit=False)
        debtor.company = company
        debtor.save()
        return redirect('customers:client_list')

    return render(request, 'customers/client_form.html', {'form': form, 'company': company})


@login_required
def debtor_update(request, pk):
    company = request.current_company
    if not company:
        return redirect('users:company_list')

    debtor = get_object_or_404(company.debtors, pk=pk)
    form = DebtorForm(request.POST or None, instance=debtor)
    if form.is_valid():
        form.save()
        return redirect('customers:client_list')

    return render(
        request,
        'customers/client_form.html',
        {'form': form, 'company': company, 'debtor': debtor},
    )


@login_required
def debtor_delete(request, pk):
    company = request.current_company
    if not company:
        return redirect('users:company_list')

    debtor = get_object_or_404(company.debtors, pk=pk)
    if request.method == 'POST':
        debtor.delete()
        return redirect('customers:client_list')

    return render(
        request,
        'customers/client_confirm_delete.html',
        {'company': company, 'debtor': debtor},
    )
