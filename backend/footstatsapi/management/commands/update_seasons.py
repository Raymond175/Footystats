from django.core.management.base import BaseCommand
from django.db import transaction
from footstatsapi.models import League, Team, Fixture


class Command(BaseCommand):
    help = 'Updates the season field for fixtures baseed on game dates for August to May leagues'
    
    def handle(self, *args, **options):
        with transaction.atomic():
            leagues = League.objects.filter(name__in=['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1', 'Eredivisie', 'Primeira Liga', 'Süper Lig', 'Jupiler Pro League', 'Championship', 'UEFA Champions League', 'UEFA Europa League'])
            
            for league in leagues:
                fixtures = Fixture.objects.filter(league=league)
                
                for fixture in fixtures:
                    season = fixture.date.year
                    if fixture.date.month < 8:
                        season -= 1
                    fixture.season = f"{season}-{season + 1}"
                    fixture.save()
                    
                    self.stdout.write(self.style.SUCCESS(f'Updated season for fixture: {fixture}'))
                    
        self.stdout.write(self.style.SUCCESS('All fixtures updated successfully'))