from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

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
    company = get_object_or_404(request.user.get_companies(), pk=company_id)
    request.session['current_company_id'] = company.id
    next_url = request.GET.get('next') or reverse('users:company_list')
    return redirect(next_url)
