from django.db.models import Sum, Count, Case, When, IntegerField, F, Q, Value
from footstatsapi.models import Team, Fixture
from django.db.models.functions import Coalesce

def get_league_table(league_id, season):
    # Calculate home stats for each team
    home_stats = Team.objects.filter(
        home_fixtures__league_id=league_id,
        home_fixtures__season=season,
        home_fixtures__status_long="Match Finished"
    ).annotate(
        matches_played=Count('home_fixtures'),
        wins=Count('home_fixtures', filter=Q(home_fixtures__goals_home__gt=F('home_fixtures__goals_away'))),
        draws=Count('home_fixtures', filter=Q(home_fixtures__goals_home=F('home_fixtures__goals_away'))),
        clean_sheets=Count('home_fixtures', filter=Q(home_fixtures__goals_away=0)),
        failed_to_score=Count('home_fixtures', filter=Q(home_fixtures__goals_home=0)),
        goals_scored=Coalesce(Sum('home_fixtures__goals_home'), Value(0)),
        goals_conceded=Coalesce(Sum('home_fixtures__goals_away'), Value(0))
    )

    # Calculate away stats for each team
    away_stats = Team.objects.filter(
        away_fixtures__league_id=league_id,
        away_fixtures__season=season,
        away_fixtures__status_long="Match Finished"
    ).annotate(
        matches_played=Count('away_fixtures'),
        wins=Count('away_fixtures', filter=Q(away_fixtures__goals_away__gt=F('away_fixtures__goals_home'))),
        draws=Count('away_fixtures', filter=Q(away_fixtures__goals_away=F('away_fixtures__goals_home'))),
        clean_sheets=Count('away_fixtures', filter=Q(away_fixtures__goals_home=0)),
        failed_to_score=Count('away_fixtures', filter=Q(away_fixtures__goals_away=0)),
        goals_scored=Coalesce(Sum('away_fixtures__goals_away'), Value(0)),
        goals_conceded=Coalesce(Sum('away_fixtures__goals_home'), Value(0))
    )

    # Combine home and away stats
    league_table = []
    for team in Team.objects.all():
        home = home_stats.filter(id=team.id).first()
        away = away_stats.filter(id=team.id).first()

        # Aggregate stats from home and away games
        matches_played = (home.matches_played if home else 0) + (away.matches_played if away else 0)
        wins = (home.wins if home else 0) + (away.wins if away else 0)
        draws = (home.draws if home else 0) + (away.draws if away else 0)
        losses = matches_played - wins - draws
        points = wins * 3 + draws
        goals_scored = (home.goals_scored if home else 0) + (away.goals_scored if away else 0)
        goals_conceded = (home.goals_conceded if home else 0) + (away.goals_conceded if away else 0)
        goal_difference = goals_scored - goals_conceded

        # Additional statistics
        ppg = points / matches_played if matches_played > 0 else 0
        clean_sheets = (home.clean_sheets if home else 0) + (away.clean_sheets if away else 0)
        failed_to_score = (home.failed_to_score if home else 0) + (away.failed_to_score if away else 0)
        cs_percentage = (clean_sheets / matches_played * 100) if matches_played > 0 else 0
        fts_percentage = (failed_to_score / matches_played * 100) if matches_played > 0 else 0

        # Form (last 5 games)
        last_five_games = Fixture.objects.filter(
            Q(home_team=team) | Q(away_team=team),
            league_id=league_id,
            season=season,
            status_long="Match Finished"
        ).order_by('-date')[:5]

        form = []
        for game in last_five_games:
            if game.home_team == team:
                if game.goals_home > game.goals_away:
                    form.append("W")
                elif game.goals_home == game.goals_away:
                    form.append("D")
                else:
                    form.append("L")
            else:
                if game.goals_away > game.goals_home:
                    form.append("W")
                elif game.goals_away == game.goals_home:
                    form.append("D")
                else:
                    form.append("L")
        
        # Only add teams that have played matches
        if matches_played > 0:
            league_table.append({
                "team": team.name,
                "matches_played": matches_played,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "points": points,
                "ppg": round(ppg, 2),
                "goals_scored": goals_scored,
                "goals_conceded": goals_conceded,
                "goal_difference": goal_difference,
                "clean_sheets_percentage": round(cs_percentage),
                "failed_to_score_percentage": round(fts_percentage),
                "form": form
            })

    # Sort the league table by points and goal difference
    league_table = sorted(league_table, key=lambda x: (-x['points'], -x['goal_difference']))

    # Add position field
    for idx, team in enumerate(league_table):
        team["position"] = idx + 1

    return league_table
