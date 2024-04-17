from django.urls import path
from .views import HomePageView, EventsDetailView

urlpatterns = [
    path('', HomePageView.as_view(), name='event_home'),
    path('event/<int:pk>/', EventsDetailView.as_view(), name='event_detail'),
]
