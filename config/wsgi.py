import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()

# Auto-migrate and create admin superuser
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    
    from accounts.models import User
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@expensetracker.np',
            password='AdminPassword123!'
        )
        admin_user.is_email_verified = True
        admin_user.save()
        print('Superuser admin created successfully!')
except Exception as e:
    print('Startup notice:', e)
