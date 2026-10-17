from django.urls import path

from . import views

urlpatterns = [
    path("contacts/", views.ContactInfoView.as_view(), name="contacts"),
    path("settings/", views.SiteSettingsView.as_view(), name="settings"),
    path("documents/", views.DocumentListView.as_view(), name="document-list"),
]
