from django.utils import timezone
from datetime import timedelta
from footstatsapi.models import Fixture

def get_upcoming_games(league_id):
    today = timezone.now()
    seven_days_forward = today + timedelta(days=7)

    # Filter fixtures based on league and date range
    upcoming_games = Fixture.objects.filter(
        league_id=league_id,
        date__range=(today, seven_days_forward)
    ).order_by('date')

    # Format the output as a list of dictionaries
    formatted_games = [
        {
            "matchId": fixture.id,
            "homeTeam": fixture.home_team.name,
            "awayTeam": fixture.away_team.name,
            "date": fixture.date.strftime('%Y-%m-%d'),
            "time": fixture.date.strftime('%H:%M'),
            "league": fixture.league.name,
        }
        for fixture in upcoming_games
    ]

    return formatted_games
