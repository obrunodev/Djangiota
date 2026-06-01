from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.loan_dashboard, name='loan-dashboard'),
    
    # Empréstimos
    path('loans/', views.LoanListView.as_view(), name='loan-list'),
    path('loans/create/', views.LoanCreateView.as_view(), name='loan-create'),
    path('loans/<int:pk>/', views.LoanDetailView.as_view(), name='loan-detail'),
    path('loans/<int:pk>/edit/', views.LoanUpdateView.as_view(), name='loan-update'),
    path('loans/<int:pk>/delete/', views.LoanDeleteView.as_view(), name='loan-delete'),
    
    # Pagamentos
    path('loans/<int:loan_id>/payment/', views.loan_payment_create, name='loan-payment-create'),
]
