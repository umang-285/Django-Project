from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from .models import Event

User = get_user_model()


class HomePageView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = Event
    template_name = 'home.html'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            query_set = Event.objects.all()
        else:
            query_set = Event.objects.filter(customer=user.id)
        return query_set


class EventsDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = Event
    template_name = 'event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            query_set = Event.objects.all()
        else:
            query_set = Event.objects.filter(customer=user.id)
        event = self.get_object(queryset=query_set)
        photos = event.event_photos.all()  # Retrieve related photos
        context['breadcrumbs'] = [{'name': 'Events', 'url': '/'}, {'name': event.name, 'url': ''}]
        context['photos'] = photos
        return context
