from django.urls import path

from . import views

urlpatterns = [
    path("countries/", views.CountryListView.as_view(), name="country-list"),
    path("partners/", views.PartnerListView.as_view(), name="partner-list"),
    path("projects/", views.ProjectListView.as_view(), name="project-list"),
    path("projects/<str:slug>/", views.ProjectDetailView.as_view(), name="project-detail"),
    path("sectors/", views.SectorListView.as_view(), name="sector-list"),
    path("presentations/", views.PresentationListView.as_view(), name="presentation-list"),
    path("presentations/<str:slug>/", views.PresentationDetailView.as_view(), name="presentation-detail"),
]
