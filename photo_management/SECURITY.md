# Security Documentation

## Overview
This document outlines the security improvements implemented in the Photo Management application.

## Security Fixes Implemented

### 1. Environment Variables & Configuration

#### Changes Made:
- **Secret Key**: Moved from hardcoded value to environment variable `DJANGO_SECRET_KEY`
- **Debug Mode**: Now controlled by `DJANGO_DEBUG` environment variable (defaults to `False`)
- **Allowed Hosts**: Configurable via `DJANGO_ALLOWED_HOSTS` environment variable

#### Files Modified:
- `photo_management/settings.py` (lines 23-34)

#### Why This Matters:
- Prevents accidental exposure of secret keys in version control
- Ensures debug mode is disabled by default in production
- Restricts which domains can serve your application

#### How to Configure:
1. Copy `.env.example` to `.env`
2. Generate a new secret key:
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```
3. Update `.env` with your settings
4. Never commit `.env` to version control

---

### 2. HTTPS & Security Headers

#### Changes Made:
- **HTTPS Redirection**: All HTTP traffic redirected to HTTPS in production
- **Secure Cookies**: Session and CSRF cookies only sent over HTTPS
- **HSTS**: HTTP Strict Transport Security enabled (1 year)
- **Content Type Protection**: Prevents MIME-sniffing attacks
- **XSS Protection**: Browser XSS filter enabled
- **Clickjacking Protection**: X-Frame-Options set to DENY

#### Files Modified:
- `photo_management/settings.py` (lines 139-163)

#### Why This Matters:
- Protects data in transit from interception
- Prevents common web vulnerabilities (XSS, clickjacking)
- Ensures browsers enforce HTTPS connections

#### Production Requirements:
- Valid SSL/TLS certificate
- Web server (nginx/Apache) configured for HTTPS
- These settings only activate when `DEBUG=False`

---

### 3. Model Security - Fixed Infinite Recursion

#### Changes Made:
- Rewrote `Photo.save()` method to use `.update()` instead of nested `.save()` calls
- Removed buggy `Event.save()` method
- Ensured at least one photo is always marked as thumbnail

#### Files Modified:
- `photogallery/models.py` (lines 15-54)

#### Why This Matters:
- Prevents application crashes from infinite recursion
- Ensures data integrity (always has a thumbnail)
- Improves performance by using direct database updates

#### Technical Details:
- Using `queryset.update()` modifies database directly without triggering save signals
- Prevents recursive save() calls that could crash the application

---

### 4. Authorization & Access Control

#### Changes Made:
- Added `get_queryset()` to filter events by ownership
- Implemented `get_object()` with permission checking
- Raises `PermissionDenied` (HTTP 403) for unauthorized access

#### Files Modified:
- `photogallery/views.py` (lines 31-52)

#### Why This Matters:
- **Critical Security Fix**: Users can no longer view other users' private events
- Prevents horizontal privilege escalation
- Implements defense in depth (multiple layers of checks)

#### How It Works:
1. `get_queryset()`: Filters database query to only user's events
2. `get_object()`: Double-checks ownership before displaying
3. Superusers can view all events (administrative access)

---

### 5. Authentication Security

#### Changes Made:

**Login Security (`UserLoginView`):**
- Rate limiting: 5 attempts per IP per 15 minutes
- Input validation and sanitization
- Generic error messages (prevents username enumeration)
- Active user check
- IP address tracking with proxy support

**Registration Security (`UserRegisterView`):**
- Rate limiting: 3 registrations per IP per hour
- Password strength validation (min 8 chars, letters + numbers)
- Username format validation (alphanumeric + underscore/hyphen/dot)
- Case-insensitive duplicate username check
- Password confirmation matching
- All fields required validation

#### Files Modified:
- `photo_management/views.py` (completely rewritten)
- `photo_management/settings.py` (added CACHES configuration, lines 94-101)

#### Why This Matters:
- **Brute Force Protection**: Rate limiting prevents password guessing attacks
- **Account Enumeration Prevention**: Generic error messages don't reveal if username exists
- **Password Security**: Strong password requirements reduce account compromise risk
- **Spam Prevention**: Registration rate limiting prevents bot account creation

#### Technical Details:
- Uses Django's cache framework for rate limiting
- IP tracking handles X-Forwarded-For headers (proxy/load balancer support)
- LocMemCache for development; use Redis in production

---

## Security Checklist for Production

### Before Deploying:

- [ ] Generate unique `DJANGO_SECRET_KEY` (never use development key)
- [ ] Set `DJANGO_DEBUG=False`
- [ ] Configure `DJANGO_ALLOWED_HOSTS` with your domain(s)
- [ ] Set up SSL/TLS certificate (Let's Encrypt recommended)
- [ ] Change cache backend to Redis or Memcached
- [ ] Configure web server (nginx/Apache) for HTTPS
- [ ] Enable firewall and restrict ports
- [ ] Set up regular database backups
- [ ] Configure logging and monitoring
- [ ] Review and update `AUTH_PASSWORD_VALIDATORS` if needed
- [ ] Consider adding django-axes for advanced rate limiting
- [ ] Set up Content Security Policy (CSP) headers
- [ ] Enable database connection encryption

### Recommended Additional Security:

1. **Two-Factor Authentication (2FA)**
   - Consider adding django-two-factor-auth

2. **Security Monitoring**
   - Django security middleware logging
   - Failed login attempt monitoring
   - Unusual access pattern detection

3. **Database Security**
   - Use PostgreSQL instead of SQLite in production
   - Enable database connection encryption
   - Regular security updates

4. **File Upload Security**
   - Validate image file types
   - Scan uploads for malware
   - Limit file sizes (add to settings.py)

5. **Dependency Security**
   - Regularly update Django and dependencies
   - Use `pip-audit` or `safety` to check for vulnerabilities

---

## Security Headers Reference

| Header | Value | Purpose |
|--------|-------|---------|
| Strict-Transport-Security | max-age=31536000 | Forces HTTPS for 1 year |
| X-Content-Type-Options | nosniff | Prevents MIME-sniffing |
| X-XSS-Protection | 1; mode=block | Enables XSS filter |
| X-Frame-Options | DENY | Prevents clickjacking |

---

## Rate Limiting Configuration

| Endpoint | Limit | Window | Purpose |
|----------|-------|--------|---------|
| /login/ | 5 attempts | 15 minutes | Brute force protection |
| /signup/ | 3 attempts | 1 hour | Spam prevention |

---

## Reporting Security Issues

If you discover a security vulnerability, please email security@example.com (update with your email).

Do NOT open public GitHub issues for security vulnerabilities.

---

## Compliance Notes

### GDPR Considerations:
- User data stored: name, username, photos
- Implement data export/deletion endpoints
- Add privacy policy and terms of service

### OWASP Top 10 Coverage:
- ✅ A01: Broken Access Control - Fixed with permission checks
- ✅ A02: Cryptographic Failures - HTTPS enforced, secure cookies
- ✅ A03: Injection - Input validation added
- ✅ A05: Security Misconfiguration - Secure defaults, environment vars
- ✅ A07: Authentication Failures - Rate limiting, strong passwords

---

## Changelog

### 2025-12-29: Security Hardening Release
- Added environment variable configuration
- Implemented HTTPS and security headers
- Fixed model infinite recursion vulnerability
- Added authorization checks to event views
- Implemented rate limiting and input validation
- Created security documentation

---

## Testing Security

### Manual Testing:
1. Try accessing another user's event (should get 403)
2. Attempt 6 failed logins (should be rate limited)
3. Try weak password during registration (should be rejected)
4. Verify HTTPS redirect in production

### Automated Testing:
```bash
# Check for security issues
python manage.py check --deploy

# Run tests
python manage.py test
```

---

## Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/4.1/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/)
