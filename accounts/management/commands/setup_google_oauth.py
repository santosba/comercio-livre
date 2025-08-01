from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Create a Google social application for OAuth'

    def handle(self, *args, **options):
        # Get the default site
        site = Site.objects.get_current()
        
        # Check if Google social app already exists
        if SocialApp.objects.filter(provider='google').exists():
            self.stdout.write(
                self.style.WARNING('Google social app already exists.')
            )
            return
        
        # Create Google social app
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth',
            client_id='your-google-client-id',  # Replace with actual client ID
            secret='your-google-client-secret',  # Replace with actual client secret
        )
        
        # Add the site to the app
        google_app.sites.add(site)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created Google social app with ID: {google_app.id}'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                'Remember to update the client_id and secret with your actual Google OAuth credentials!'
            )
        )
