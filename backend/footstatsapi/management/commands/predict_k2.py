from django.core.management.base import BaseCommand
import pandas as pd
from footstatsapi.models import Fixture
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

class Command(BaseCommand):
    help = "Train a model to predict football match outcomes with top-2 predictions"

    def handle(self, *args, **options):
        # Load data from the Fixture model
        data = pd.DataFrame(list(Fixture.objects.all().values(
            "home_team_id", "away_team_id", "goals_home", "goals_away", "date", "league_id", "season"
        )))

        # Create result column
        data["result"] = (data["goals_home"] - data["goals_away"]).apply(lambda x: "H" if x > 0 else "A" if x < 0 else "D")

        # Apply feature engineering
        data = self.feature_engineering(data)
        data = self.calculate_form(data)

        # Define features and target
        features = [
            'home_win_rate', 'away_win_rate', 'total_goals_scored_home', 'total_goals_scored_away',
            'total_goals_conceded_home', 'total_goals_conceded_away', 'home_form', 'away_form'
        ]
        target = data["result"]

        # Split the data into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(data[features], target, test_size=0.2, random_state=42)

        # Output the shape of the train set and any null values
        # self.stdout.write(f"Training set size: {X_train.shape[0]}")
        # self.stdout.write(f"Missing values in X_train:\n{X_train.isnull().sum()}")
        # self.stdout.write(f"Missing values in y_train:\n{y_train.isnull().sum()}")

        # Train the RandomForest model
        model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        model.fit(X_train, y_train)

        y_proba = model.predict_proba(X_test)
        
        top_2_predictions = np.argsort(y_proba, axis=1)[:, -2:]
        
        class_labels = ["A", "D", "H"]
        top_2_class_labels = np.array(class_labels)[top_2_predictions]
        
        for i in range(len(y_test)):
            self.stdout.write(f"Sample {i + 1}: Top-2 predictions: {top_2_class_labels[i]}, Actual: {class_labels[class_labels.index(y_test.iloc[i])]}")

            
        # Predict and evaluate the model
        y_pred = model.predict(X_test)
        self.stdout.write("\nClassification Report (Top-1 prediction):")
        self.stdout.write(classification_report(y_test, y_pred))

    def calculate_form(self, df, num_games=10):
        # Sort the dataframe by date to ensure chronological order for rolling window
        df = df.sort_values(by="date")
        
        # Initialize a column for each team's total form
        df["home_points"] = df.apply(
            lambda row: 3 if row['goals_home'] > row['goals_away'] else (1 if row['goals_home'] == row['goals_away'] else 0),
            axis=1
        )
        df["away_points"] = df.apply(
            lambda row: 3 if row['goals_away'] > row['goals_home'] else (1 if row['goals_away'] == row['goals_home'] else 0),
            axis=1
        )

        # Combine home and away games into a single dataframe for easier rolling form calculation
        home_games = df[["home_team_id", "date", "home_points"]].rename(columns={"home_team_id": "team_id", "home_points": "points"})
        away_games = df[["away_team_id", "date", "away_points"]].rename(columns={"away_team_id": "team_id", "away_points": "points"})

        # Concatenate home and away games
        team_games = pd.concat([home_games, away_games])

        # Sort by date again to ensure chronological order
        team_games = team_games.sort_values(by="date")

        # Calculate rolling form (sum of points over the last `num_games` games)
        team_games["form"] = team_games.groupby("team_id")["points"].transform(lambda x: x.rolling(window=num_games, min_periods=1).sum())

        # Merge the form back to the original dataframe for home and away teams
        df = df.merge(team_games[["team_id", "date", "form"]], left_on=["home_team_id", "date"], right_on=["team_id", "date"], how="left")
        df.rename(columns={"form": "home_form"}, inplace=True)

        df = df.merge(team_games[["team_id", "date", "form"]], left_on=["away_team_id", "date"], right_on=["team_id", "date"], how="left")
        df.rename(columns={"form": "away_form"}, inplace=True)

        # Drop the redundant 'team_id' columns from the merge
        df.drop(columns=["team_id_x", "team_id_y"], inplace=True)
        return df
    
    def feature_engineering(self, df):
        # Creating home and away win rates
        df["home_win_rate"] = df.groupby("home_team_id")["result"].transform(lambda x: (x == "H").mean())
        df["away_win_rate"] = df.groupby("away_team_id")["result"].transform(lambda x: (x == "A").mean())
        
        # Creating home and away goals scored and conceded
        df["total_goals_scored_home"] = df.groupby("home_team_id")["goals_home"].transform("sum")
        df["total_goals_scored_away"] = df.groupby("away_team_id")["goals_away"].transform("sum")
        df["total_goals_conceded_home"] = df.groupby("home_team_id")["goals_away"].transform("sum")
        df["total_goals_conceded_away"] = df.groupby("away_team_id")["goals_home"].transform("sum")
        
        return df
