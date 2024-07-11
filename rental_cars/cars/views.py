from django.shortcuts import render

from cars.models import Car, CarImage


# Create your views here.
# class CarView()
def cars_list(request):
    cars = Car.objects.filter(availability=True)
    data = {}
    for car in cars:
        for img in CarImage.objects.filter(car=car.id):
            if not data.get(str(car.id), False):
                data[str(car.id)] = [img.image]
            else:
                data[str(car.id)].append(img.image)
    return render(request, 'cars.html', context={'cars': cars, "car_images": data})
