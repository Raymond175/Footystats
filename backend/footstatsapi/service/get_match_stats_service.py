from django.db.models import Avg, Q, Count, Case, When, IntegerField, F
from footstatsapi.models import Fixture, Team

def get_match_stats(league_id, match_id):
    # Get the specific fixture and related team info
    fixture = Fixture.objects.select_related('home_team', 'away_team', 'league').get(id=match_id, league_id=league_id)
    home_team = fixture.home_team
    away_team = fixture.away_team

    # Calculate Points Per Game (PPG) for the home and away teams
    home_ppg = (
        Fixture.objects.filter(Q(home_team=home_team) | Q(away_team=home_team))
        .annotate(points=Case(
            When(home_team=home_team, goals_home__gt=F('goals_away'), then=3),
            When(away_team=home_team, goals_away__gt=F('goals_home'), then=3),
            When(goals_home=F('goals_away'), then=1),
            default=0,
            output_field=IntegerField()
        ))
        .aggregate(ppg=Avg('points'))['ppg']
    ) or 0  # Defaults to 0 if no data

    away_ppg = (
        Fixture.objects.filter(Q(home_team=away_team) | Q(away_team=away_team))
        .annotate(points=Case(
            When(home_team=away_team, goals_home__gt=F('goals_away'), then=3),
            When(away_team=away_team, goals_away__gt=F('goals_home'), then=3),
            When(goals_home=F('goals_away'), then=1),
            default=0,
            output_field=IntegerField()
        ))
        .aggregate(ppg=Avg('points'))['ppg']
    ) or 0

    # Head-to-head: Get last 5 matches between home and away team
    head_to_head_matches = Fixture.objects.filter(
        Q(home_team=home_team, away_team=away_team) |
        Q(home_team=away_team, away_team=home_team)
    ).order_by('-date')[:5]

    # Calculate head-to-head results summary
    home_wins = head_to_head_matches.filter(home_team=home_team, goals_home__gt=F('goals_away')).count()
    away_wins = head_to_head_matches.filter(home_team=away_team, goals_away__gt=F('goals_home')).count()
    draws = head_to_head_matches.filter(goals_home=F('goals_away')).count()

    if home_wins > away_wins:
        head_to_head_summary = f"{home_team.name} has won {home_wins} of the last 5 games against {away_team.name}"
    elif away_wins > home_wins:
        head_to_head_summary = f"{away_team.name} has won {away_wins} of the last 5 games against {home_team.name}"
    else:
        head_to_head_summary = f"{home_team.name} and {away_team.name} have each won {draws} of the last 5 games against each other"

    # Structure the match stats in the desired format
    match_stats = {
        "league": fixture.league.name.lower(),
        "match_id": match_id,
        "home_team": home_team.name,
        "away_team": away_team.name,
        "home_ppg": round(home_ppg, 2),
        "away_ppg": round(away_ppg, 2),
        "head_to_head": head_to_head_summary,
    }

    return match_stats
