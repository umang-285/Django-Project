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
            return thumbnail_photo.image.url  # Assuming 'image' is the field storing the image path
        return None
    
    def save(self, *args, **kwargs):
        # If this photo is being marked as the thumbnail, unmark all other photos as not thumbnail
        photo = self.event_photos
        default_thumbnail = photo.filter(is_thumbnail=True)
        if not default_thumbnail.exists():
            default_photo = photo.first()
            if default_photo:
                default_photo.is_thumbnail = True
                default_photo.save()  # Save the changes to the default thumbnail
        return super().save(*args, **kwargs)


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
        # If this photo is being marked as the thumbnail, unmark all other photos as not thumbnail
        if self.is_thumbnail:
            self.event.event_photos.exclude(pk=self.pk).update(is_thumbnail=False)
        else:
            first_photo = self.event.event_photos.first()
            if first_photo:
                first_photo.is_thumbnail = True
                first_photo.save()
        return super().save(*args, **kwargs)
