from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Event(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_events')
    name = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self) -> str:
        return self.name
    
    @property
    def thumbnail(self):
        # Fetch the thumbnail photo associated with this event
        thumbnail_photo = self.event_photos.filter(is_thumbnail=True).first()
        if thumbnail_photo:
            return thumbnail_photo.image.url
        return None


class Photo(models.Model):
    def image_upload_path(instance, filename):
        customer_id = instance.event.customer.id
        event_name = instance.event.name
        folder_path = f'{customer_id}/{event_name}'
        return f'{folder_path}/{filename}'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_photos')
    image = models.ImageField(upload_to=image_upload_path)
    description = models.TextField()
    is_thumbnail = models.BooleanField(default=False, editable=True)

    def save(self, *args, **kwargs):
        # If this photo is being marked as the thumbnail, unmark all other photos
        if self.is_thumbnail:
            # Use update() to avoid triggering save() on other photos (prevents recursion)
            self.event.event_photos.exclude(pk=self.pk).update(is_thumbnail=False)

        # Save the current photo
        super().save(*args, **kwargs)

        # After saving, ensure at least one photo is marked as thumbnail
        # Only check if this photo is NOT a thumbnail
        if not self.is_thumbnail:
            has_thumbnail = self.event.event_photos.filter(is_thumbnail=True).exists()
            if not has_thumbnail:
                # No thumbnail exists, make the first photo the thumbnail
                # Use update() to avoid infinite recursion
                first_photo = self.event.event_photos.first()
                if first_photo:
                    self.event.event_photos.filter(pk=first_photo.pk).update(is_thumbnail=True)
