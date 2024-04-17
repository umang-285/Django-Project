from django.contrib import admin

from .models import Photo, Event


class EventImageInline(admin.TabularInline):
    model = Photo
    extra = 1


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    pass

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = [ EventImageInline, ]
