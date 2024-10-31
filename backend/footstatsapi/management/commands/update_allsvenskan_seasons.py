from django.core.management.base import BaseCommand
from django.db import transaction
from footstatsapi.models import League, Team, Fixture

class Command(BaseCommand):
    help = 'Sets the season for Allsvenskan fixtures based on the year of the game date'
    
    def handle(self, *args, **options):
        with transaction.atomic():
            allsvenskan_league = League.objects.get(name='Allsvenskan')
            fixtures = Fixture.objects.filter(league=allsvenskan_league)
            
            for fixture in fixtures:
                season = fixture.date.year
                fixture.season = season
                fixture.save()
                
                self.stdout.write(self.style.SUCCESS(f'Updated season for fixture: {fixture}'))