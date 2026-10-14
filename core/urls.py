from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("applicants/new/", views.applicant_create, name="applicant_create"),
    path("applicants/", views.applicant_list, name="applicant_list"),
    path("applicants/<int:pk>/", views.applicant_result, name="applicant_result"),
    path("applicants/<int:pk>/decision/", views.applicant_decide, name="applicant_decide"),
]
