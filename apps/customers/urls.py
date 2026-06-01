from django.urls import path

from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.debtor_list, name='client_list'),
    path('novo/', views.debtor_create, name='client_create'),
    path('<int:pk>/editar/', views.debtor_update, name='client_update'),
    path('<int:pk>/excluir/', views.debtor_delete, name='client_delete'),
]
