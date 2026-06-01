from django.utils.functional import SimpleLazyObject


def get_current_company(request):
    if not request.user.is_authenticated:
        return None

    company_id = request.session.get('current_company_id')
    if company_id:
        company = request.user.companies.filter(pk=company_id).first()
        if company:
            return company

    first_company = request.user.companies.first()
    if first_company:
        request.session['current_company_id'] = first_company.id
    return first_company


class CurrentCompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.current_company = SimpleLazyObject(lambda: get_current_company(request))
        response = self.get_response(request)
        return response
