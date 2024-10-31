# fetch_data.py
from django.core.management.base import BaseCommand
import requests
from footstatsapi.models import League, Team, Fixture
from backend.settings import API_KEY, API_URL

class Command(BaseCommand):
    help = 'Fetches data from an API and stores it in the database'
    # https://github.com/xjxckk/BetLink-bet365-place-bet-api-service/blob/master/sample_usage.py
    def handle(self, *args, **options):
        self.fetch_and_save_fixtures()

    def fetch_and_save_fixtures(self):
        leagues = {
        'Belgian Pro League': 144,  # Belgium Pro League
        'MLS': 253,            # USA Major League Soccer
        'Brasileirao Série A': 71,    # Brazil Serie A
        'Championship': 40,    # England Championship
        'Champions League': 2, # UEFA Champions League
        'Europa League': 3,    # UEFA Europa League
        }

        seasons = range(2014, 2025)  # From 2013 to 2023
        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": API_URL  # Ensure this is the correct host for the API
        }
        
        total_fixtures_loaded = 0
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        for league_name, league_id in leagues.items():
            for season in seasons:
                params = {"league": league_id, "season": season}
                try:
                    response = requests.get(url, headers=headers, params=params)
                    data = response.json()

                    for item in data['response']:
                        self.process_fixture(item)

                    total_fixtures_loaded += len(data['response'])
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error fetching data: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Total fixtures loaded: {total_fixtures_loaded}'))

    
    def process_fixture(self, item):
        league_data = item['league']
        home_team_data = item['teams']['home']
        away_team_data = item['teams']['away']
        fixture_data = item['fixture']
        score_data = item['score']

        # Create or update the League
        league, _ = League.objects.update_or_create(
            id=league_data['id'],
            defaults={
                'name': league_data['name'],
                'country': league_data['country'],
                'logo': league_data['logo'],
                'flag': league_data['flag'],
            }
        )

        # Create or update the Home Team
        home_team, _ = Team.objects.update_or_create(
            id=home_team_data['id'],
            defaults={
                'name': home_team_data['name'],
                'logo': home_team_data['logo'],
            }
        )

        # Create or update the Away Team
        away_team, _ = Team.objects.update_or_create(
            id=away_team_data['id'],
            defaults={
                'name': away_team_data['name'],
                'logo': away_team_data['logo'],
            }
        )

        # Handle missing values for scores and goals using get method to return None if the key is missing
        fixture, created = Fixture.objects.update_or_create(
            id=fixture_data['id'],
            defaults={
                'league': league,
                'home_team': home_team,
                'away_team': away_team,
                'date': fixture_data['date'],
                'referee': fixture_data.get('referee', None),  # Use None if referee is missing
                'venue_name': fixture_data['venue'].get('name', None),  # Handle missing venue name
                'venue_city': fixture_data['venue'].get('city', None),  # Handle missing venue city
                'status_long': fixture_data['status']['long'],
                'status_short': fixture_data['status']['short'],
                'status_elapsed': fixture_data.get('status', {}).get('elapsed', None),  # Use None if elapsed time is missing
                'goals_home': item['goals'].get('home', None),  # Allow None for upcoming fixtures
                'goals_away': item['goals'].get('away', None),  # Allow None for upcoming fixtures
                'score_halftime_home': score_data.get('halftime', {}).get('home', None),  # Handle missing halftime score
                'score_halftime_away': score_data.get('halftime', {}).get('away', None),
                'score_fulltime_home': score_data.get('fulltime', {}).get('home', None),  # Handle missing fulltime score
                'score_fulltime_away': score_data.get('fulltime', {}).get('away', None),
                'season': fixture_data.get('season', None),  # Handle missing season
            }
        )

