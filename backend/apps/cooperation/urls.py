from django.urls import path

from . import views

urlpatterns = [
    path("countries/", views.CountryListView.as_view(), name="country-list"),
    path("partners/", views.PartnerListView.as_view(), name="partner-list"),
    path("projects/", views.ProjectListView.as_view(), name="project-list"),
    path("projects/<str:slug>/", views.ProjectDetailView.as_view(), name="project-detail"),
]
