from django.shortcuts import HttpResponseRedirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


class UserLoginView(TemplateView):
    template_name = 'registration/login.html'

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        if request.POST:
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect("/")
            else:
                return self.render_to_response({'error': 'Username or Password is not Valid. Please check it'})


class UserRegisterView(TemplateView):
    model = User
    template_name = 'registration/signup.html'
    
    def post(self, request):
        data = request.POST
        first_name = data.get('firstname')
        last_name = data.get('lastname')
        username = data.get('username')
        password = data.get('password')
        if User.objects.filter(username=username).exists():
            # Handle username already exists error
            return self.render_to_response({'error_message': 'Username already exists'})
        
        # Create the user
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
        )
        if user:
            # Redirect to login page on successful registration
            return HttpResponseRedirect(reverse('login'))
        else:
            # Handle user creation failure
            return self.render_to_response({'error_message': 'Failed to create user'})
