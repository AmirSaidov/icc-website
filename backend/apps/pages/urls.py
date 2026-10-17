from django.urls import path

from . import views

urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path("pages/", views.PageMenuListView.as_view(), name="page-list"),
    path("pages/<str:key_or_slug>/", views.PageDetailView.as_view(), name="page-detail"),
    path("directions/", views.DirectionListView.as_view(), name="direction-list"),
    path("directions/<str:slug>/", views.DirectionDetailView.as_view(), name="direction-detail"),
    path("services/", views.ServiceListView.as_view(), name="service-list"),
    path("services/<str:slug>/", views.ServiceDetailView.as_view(), name="service-detail"),
]
