from django.urls import path

from . import views

urlpatterns = [
    path("news-categories/", views.NewsCategoryListView.as_view(), name="news-category-list"),
    path("news/", views.NewsListView.as_view(), name="news-list"),
    path("news/<str:slug>/", views.NewsDetailView.as_view(), name="news-detail"),
    path("events/", views.EventListView.as_view(), name="event-list"),
    path("events/<str:slug>/", views.EventDetailView.as_view(), name="event-detail"),
    path("event-types/", views.EventTypeListView.as_view(), name="event-type-list"),
]
