from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Company


@login_required
def company_list(request):
    companies = request.user.get_companies()
    return render(
        request,
        'users/company_list.html',
        {
            'companies': companies,
            'current_company': getattr(request, 'current_company', None),
        },
    )


@login_required
def switch_company(request, company_id):
    company = request.user.get_companies().filter(pk=company_id).first()
    if company:
        request.session['current_company_id'] = company.id
    return redirect('users:company_list')
