from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('', views.company_list, name='company_list'),
    path('switch/<int:company_id>/', views.switch_company, name='switch_company'),
]
