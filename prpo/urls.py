from django.urls import path
from . import views

urlpatterns = [
    path('pr/create/', views.pr_create, name='create_pr'),
    path('po/create/', views.po_create, name='create_po'),
    path('pr/list/', views.pr_list, name='list_pr'),
    path('po/list/', views.po_list, name='list_po'),
    path('bulk_upload/', views.bulk_upload, name='bulk_upload'),

    path('', views.home, name='home'),   # add home route
]

