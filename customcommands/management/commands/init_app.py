import os
import subprocess
from django.core.management.base import BaseCommand, CommandParser
from django.core.management import call_command
from django.core.management.commands.migrate import Command as MigrateCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Initialize the application, run migrations, collect static files and create a superuser'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            '--start-server',
            action='store_true',
            dest='start_server',
            help='Start the server after initialization'
        )

    def handle(self, *args, **options):
        # Collect static files
        self.stdout.write('Collecting static files...')
        call_command('collectstatic', '--no-input')

        # Run the migrations
        self.stdout.write('Running migrations...')
        call_command('migrate')

        # Create a superuser using environment data
        self.stdout.write('Creating superuser...')

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not email or not password:
            self.stdout.write(self.style.ERROR('Error: Superuser data is not configured in the environment.'))
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_superuser': True,
                'is_staff': True,
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS('The superuser has been created successfully.'))
        else:
            self.stdout.write('Superuser already exists. Skipping superuser creation.')

        if options['start_server']:
            self.stdout.write('Starting the server...')

            # running gunicorn
            try:
                subprocess.run(['gunicorn', 'school_app.wsgi:application', '--bind', '0.0.0.0:5000'])
            except subprocess.CalledProcessError as e:
                self.stdout.write(self.style.ERROR(f'Error: Failed to start the server. {e}'))

            self.stdout.write(self.style.SUCCESS('The application has been successfully initialized.'))
