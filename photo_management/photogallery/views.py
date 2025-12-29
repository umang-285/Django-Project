from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
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

    def get_queryset(self):
        """
        Restrict queryset to only events owned by the user.
        Superusers can see all events.
        """
        user = self.request.user
        if user.is_superuser:
            return Event.objects.all()
        return Event.objects.filter(customer=user)

    def get_object(self, queryset=None):
        """
        Override to add explicit permission checking.
        Returns 403 Forbidden if user tries to access someone else's event.
        """
        obj = super().get_object(queryset=queryset)

        # Double-check permissions (defense in depth)
        if not self.request.user.is_superuser and obj.customer != self.request.user:
            raise PermissionDenied("You don't have permission to view this event.")

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        photos = event.event_photos.all()
        context['breadcrumbs'] = [
            {'name': 'Events', 'url': '/'},
            {'name': event.name, 'url': ''}
        ]
        context['photos'] = photos
        return context
