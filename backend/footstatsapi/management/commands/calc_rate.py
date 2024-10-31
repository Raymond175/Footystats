from footstatsapi.models import Fixture
from django.db.models import F
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Calculate the win rates for home, away, and draw outcomes"

    def handle(self, *args, **options):
        # 1. Calculate the total number of matches
        total_matches = Fixture.objects.count()

        # 2. Calculate the number of home wins, away wins, and draws
        home_wins = Fixture.objects.filter(goals_home__gt=F('goals_away')).count()
        away_wins = Fixture.objects.filter(goals_away__gt=F('goals_home')).count()
        draws = Fixture.objects.filter(goals_home=F('goals_away')).count()

        # 3. Calculate the percentages
        home_win_percentage = (home_wins / total_matches) * 100 if total_matches > 0 else 0
        away_win_percentage = (away_wins / total_matches) * 100 if total_matches > 0 else 0
        draw_percentage = (draws / total_matches) * 100 if total_matches > 0 else 0

        print(f"H: {round(home_win_percentage, 2)}%, D: {round(draw_percentage, 2)}%, A: {round(away_win_percentage, 2)}%")
