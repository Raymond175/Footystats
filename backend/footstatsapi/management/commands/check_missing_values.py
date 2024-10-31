from django.core.management.base import BaseCommand
import pandas as pd
from footstatsapi.models import Fixture

class Command(BaseCommand):
    help = "Check for missing values in the Fixture table"
    
    def handle(self, *args, **kwargs):
        # Load the data from the Fixture table
        
        data = pd.DataFrame(list(Fixture.objects.all().values("home_team_id", "away_team_id", "goals_home", "goals_away", "date", "league_id", "season")))
        
        # Check for missing values
        
        missing_values = data.isnull().sum()
        self.stdout.write(self.style.SUCCESS("Missing values in each column:"))
        self.stdout.write(str(missing_values))
        
        # Print the rows with missing values
        self.stdout.write(self.style.SUCCESS("\nRows with missing values:"))
        self.stdout.write(str(data[data.isnull().any(axis=1)]))
        