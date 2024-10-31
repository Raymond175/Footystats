from rest_framework import serializers
from .models import Team, Fixture, League, Prediction
from django.utils import timezone


class FootballGameSerializer(serializers.ModelSerializer):
  class Meta:
    model = Fixture
    fields = ['home_team', 'away_team', 'date', 'league_id']

class LeagueStatsSerializer(serializers.Serializer):
  league = serializers.CharField()
  season = serializers.CharField()
  average_goals_per_game = serializers.FloatField(allow_null=True)
  average_home_team_goals = serializers.FloatField(allow_null=True)
  average_away_team_goals = serializers.FloatField(allow_null=True)
    
class FixtureSerializer(serializers.ModelSerializer):
  homeTeam = serializers.CharField(source='home_team.name', read_only=True)
  awayTeam = serializers.CharField(source='away_team.name', read_only=True)
  homeTeamLogo = serializers.CharField(source='home_team.logo', read_only=True)
  awayTeamLogo = serializers.CharField(source='away_team.logo', read_only=True)
  league = serializers.CharField(source='league.name', read_only=True)
  leagueLogo = serializers.CharField(source='league.logo', read_only=True)
  date = serializers.SerializerMethodField()
  time = serializers.SerializerMethodField()
  
  class Meta:
    model = Fixture
    fields = '__all__'
  
  def get_date(self, obj):
    return obj.date.strftime('%Y-%m-%d') if obj.date else None

  def get_time(self, obj):
    return obj.date.strftime('%H:%M') if obj.date else None

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = '__all__'