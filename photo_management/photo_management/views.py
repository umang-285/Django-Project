from django.shortcuts import HttpResponseRedirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
import time


class UserLoginView(TemplateView):
    template_name = 'registration/login.html'

    def post(self, request):
        # Rate limiting: Allow max 5 login attempts per IP per 15 minutes
        ip_address = self.get_client_ip(request)
        rate_limit_key = f'login_attempts_{ip_address}'
        attempts = cache.get(rate_limit_key, 0)

        if attempts >= 5:
            return self.render_to_response({
                'error': 'Too many login attempts. Please try again in 15 minutes.'
            })

        # Input validation
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Validate inputs are not empty
        if not username or not password:
            return self.render_to_response({
                'error': 'Username and password are required.'
            })

        # Sanitize username (alphanumeric, underscore, hyphen, dot only)
        if not re.match(r'^[\w.-]+$', username):
            return self.render_to_response({
                'error': 'Invalid username format.'
            })

        # Limit username length
        if len(username) > 150:
            return self.render_to_response({
                'error': 'Username is too long.'
            })

        # Authenticate user
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            # Clear rate limiting on successful login
            cache.delete(rate_limit_key)
            return HttpResponseRedirect("/")
        else:
            # Increment failed attempts
            cache.set(rate_limit_key, attempts + 1, 900)  # 900 seconds = 15 minutes
            # Generic error message (don't reveal if username exists)
            return self.render_to_response({
                'error': 'Invalid credentials. Please try again.'
            })

    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserRegisterView(TemplateView):
    model = User
    template_name = 'registration/signup.html'

    def post(self, request):
        # Rate limiting: Allow max 3 registrations per IP per hour
        ip_address = self.get_client_ip(request)
        rate_limit_key = f'register_attempts_{ip_address}'
        attempts = cache.get(rate_limit_key, 0)

        if attempts >= 3:
            return self.render_to_response({
                'error_message': 'Too many registration attempts. Please try again in 1 hour.'
            })

        # Get and sanitize input data
        data = request.POST
        first_name = data.get('firstname', '').strip()
        last_name = data.get('lastname', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')

        # Validate all required fields are present
        if not all([first_name, last_name, username, password]):
            return self.render_to_response({
                'error_message': 'All fields are required.'
            })

        # Validate password match
        if password != confirm_password:
            return self.render_to_response({
                'error_message': 'Passwords do not match.'
            })

        # Validate username format (alphanumeric, underscore, hyphen, dot only)
        if not re.match(r'^[\w.-]+$', username):
            return self.render_to_response({
                'error_message': 'Username can only contain letters, numbers, underscore, hyphen, and dot.'
            })

        # Validate username length
        if len(username) < 3 or len(username) > 150:
            return self.render_to_response({
                'error_message': 'Username must be between 3 and 150 characters.'
            })

        # Validate password strength
        if len(password) < 8:
            return self.render_to_response({
                'error_message': 'Password must be at least 8 characters long.'
            })

        # Check password complexity (at least one letter and one number)
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            return self.render_to_response({
                'error_message': 'Password must contain at least one letter and one number.'
            })

        # Validate name lengths
        if len(first_name) > 150 or len(last_name) > 150:
            return self.render_to_response({
                'error_message': 'Names are too long.'
            })

        # Check if username already exists
        if User.objects.filter(username__iexact=username).exists():
            return self.render_to_response({
                'error_message': 'Username already exists. Please choose another.'
            })

        try:
            # Create the user
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=password,
            )

            # Increment registration attempts
            cache.set(rate_limit_key, attempts + 1, 3600)  # 3600 seconds = 1 hour

            # Redirect to login page on successful registration
            return HttpResponseRedirect(reverse('login'))

        except Exception as e:
            # Log the error in production (don't expose to user)
            return self.render_to_response({
                'error_message': 'Registration failed. Please try again.'
            })

    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
