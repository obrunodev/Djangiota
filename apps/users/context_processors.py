def active_company(request):
    return {
        'current_company': getattr(request, 'current_company', None),
    }
