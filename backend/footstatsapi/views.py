from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from django.utils import timezone
from .models import Fixture, League, Prediction
from .serializers import FootballGameSerializer, LeagueStatsSerializer, FixtureSerializer, PredictionSerializer
from django.db.models import Sum, Count
from rest_framework.views import APIView
from .service.prediction_service import predict_outcomes
from .service.league_table_service import get_league_table
from .service.upcoming_games_service import get_upcoming_games
from .service.get_match_stats_service import get_match_stats
from .service.get_league_name_service import get_league_id_from_name
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def get_league_stats(league_name, season):
    """
    Get average goals stats for any league, with specific handling for Allsvenskan
    since it does not span across two years (e.g., "2024" instead of "2023-2024").
    """
    try:
        
        # Get league based on name
        league = League.objects.get(name=league_name)
        
        # Check if league is Allsvenskan and adjust season accordingly
        if league_name == "Allsvenskan":
            fixtures = Fixture.objects.filter(league=league, date__year=season, goals_home__isnull=False, goals_away__isnull=False)
        else:
            fixtures = Fixture.objects.filter(league=league, season=season, goals_home__isnull=False, goals_away__isnull=False)
        
        total_data = fixtures.aggregate(Sum('goals_home'), Sum('goals_away'), Count('id'))
        
        total_goals = (total_data['goals_home__sum'] or 0) + (total_data['goals_away__sum'] or 0)
        total_games = total_data['total_games'] or 1 
        
        average_goals_per_game = total_goals / total_games
        average_home_goals = (total_data['goals_home__sum'] or 0) / total_games if total_games > 0 else 0
        average_away_goals = (total_data['goals_away__sum'] or 0) / total_games if total_games > 0 else 0
        
        return {
            "league": league_name,
            "season": season,
            "average_goals_per_game": average_goals_per_game,
            "average_home_team_goals": average_home_goals,
            "average_away_team_goals": average_away_goals
        }
    except League.DoesNotExist:
        return {"error": f"League {league_name} does not exist."}
    
@api_view(['GET'])
def league_stats_view(request, league_name, season):
    """
    View to get league stats for a specific league and season.
    """
    try:
        if league_name != "Allsvenskan":
            if not validate_season_format(season):
                return Response({"error": "Invalid season format. Expected 'YYYY-YYYY'."}, status=400)
        
        stats = get_league_stats(league_name, season)
        
        if "error" in stats:
            logger.error(stats[f"Error fetching stats: {stats['error']}"])
            return Response(stats, status=404)

        serialzer = LeagueStatsSerializer(stats)
        if serialzer.is_valid():
            return Response(serialzer.data, status=200)
        else:
            return Response(serialzer.errors, status=400)
            
    
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return Response({"error": "An error occurred while fetching stats."}, status=500)
    
def validate_season_format(season):
    """
    Validates the season format (YYYY-YYYY) for leagues other than Allsvenskan.
    Returns True if valid, False otherwise.
    """
    if len(season) == 9 and season[4] == "-" and season[:4].isdigit() and season[5:].isdigit():
        return True
    return False

class TodayFixtureView(generics.ListAPIView):
    serializer_class = FixtureSerializer
    
    def get_queryset(self):
        today = timezone.now().date()
        return Fixture.objects.filter(date__date=today)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"error": "No fixtures scheduled today."}, status=404)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)

class MatchPredictionView(APIView):
    def post(self, request):
        try:
            home_team_id = request.data.get("home_team_id")
            away_team_id = request.data.get("away_team_id")

            if not home_team_id or not away_team_id:
                return Response({"error": "home_team_id and away_team_id are required"}, status=400)

            result = predict_outcomes(home_team_id, away_team_id)
            return Response(result, status=200)
        except Exception as e:
            logger.exception("Error in MatchPredictionView\n")
            return Response({"error": str(e)}, status=500)

class PredictOutcomesView(APIView):
    queryset = Prediction.objects.all().order_by('-predicted_at')
    serializer_class = PredictionSerializer
    
class PredictionListView(generics.ListAPIView):
    queryset = Prediction.objects.all().order_by('-predicted_at')
    serializer_class = PredictionSerializer

class LeagueTableView(APIView):
    def get(self, request, *args, **kwargs):
        league_id = kwargs.get('league_id')
        season = kwargs.get('season')
        
        try:
            league_table = get_league_table(league_id, season)
            return Response(league_table, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class UpcomingGamesView(APIView):
    def get(self, request, league_id):
        upcoming_games = get_upcoming_games(league_id)
        return Response(upcoming_games, status=200)
    
class MatchStatsView(APIView):
    def get(self, request, league_name, match_id):
        try:
            # Assume `league_name` can be mapped to league_id; you might need a lookup here.
            league_id = get_league_id_from_name(league_name)  # Custom function to map league names to IDs
            stats = get_match_stats(league_id, match_id)
            return Response({league_name: {match_id: stats}}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
@api_view(['GET'])
def get_all_leagues(request):
    try:
        leagues = League.objects.all()
        if not leagues.exists():
            return JsonResponse({"error": "No leagues found."}, status=404)
        leagues_data = [
            {
                "id": league.id,
                "name": league.name,
                "logo": league.logo
            }
            for league in leagues
        ]
        return JsonResponse(leagues_data, safe=False)
    except Exception as e:
        return JsonResponse({"error": "An unexpected error occurred."}, status=400)

@api_view(['GET'])
def get_upcoming_league_games(request, league_id):
   try:
        # Set the date range for the next 7 days
        today = datetime.now().date()
        print(today)
        next_week = today + timedelta(days=7)
        print(next_week)
        logger.info(f"Request received for league {league_id} from {today} to {next_week}")

        # Verify the league exists
        league = get_object_or_404(League, id=league_id)
        logger.info(f"League found: {league.name}")

        # Retrieve fixtures in the league for the next 7 days with upcoming status
        upcoming_games = Fixture.objects.filter(
            league=league,
            date__date__range=(today, next_week),
            status_long="Not Started"
        ).order_by('date')
        
        # Check if there are upcoming games
        if not upcoming_games.exists():
            logger.info("No upcoming games found for this league in the next 7 days.")
            return JsonResponse({"error": "No upcoming games found for this league in the next 7 days."}, status=404)

        # Format the response data
        games_data = [
            {
                "id": game.id,
                "home_team": game.home_team.name,
                "away_team": game.away_team.name,
                "date": game.date.strftime('%Y-%m-%d'),
                "time": game.date.strftime('%H:%M')
            }
            for game in upcoming_games
        ]

        # Return the response as JSON
        return JsonResponse(games_data, safe=False)
   except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred."}, status=400)