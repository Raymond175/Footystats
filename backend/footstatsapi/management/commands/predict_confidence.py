import numpy as np
from django.core.management.base import BaseCommand
import pandas as pd
from footstatsapi.models import Fixture
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
import matplotlib.pyplot as plt
import joblib

class Command(BaseCommand):
    help = "Train a model to predict football match outcomes with a confidence threshold"

    def handle(self, *args, **options):
        # Load data and perform preprocessing (same as before)
        data = pd.DataFrame(list(Fixture.objects.all().values(
            "home_team_id", "away_team_id", "goals_home", "goals_away", "date", "league_id", "season"
        )))
        data["result"] = (data["goals_home"] - data["goals_away"]).apply(lambda x: "H" if x > 0 else "A" if x < 0 else "D")

        # Feature engineering (same as before)
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

        # Train the RandomForest model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Predict probabilities for each class
        y_proba = model.predict_proba(X_test)

        # Confidence threshold for making a single prediction
        confidence_threshold = 0.53  # You can adjust this value
        
        thresholds = np.arange(0.4, 0.7, 0.05)
        top_1_accurcies = []
        top_2_accuracies = []
        
        class_labels = ['A', 'D', 'H']  # Adjust based on your target encoding
        
        for threshold in thresholds: 
            correct_top_1 = 0
            correct_top_2 = 0
        
        # Output predictions based on confidence
        
            for i in range(len(y_test)):
                top_1_pred = np.argmax(y_proba[i])
                top_1_prob = y_proba[i][top_1_pred]

                # Get the actual class label
                true_label = class_labels.index(y_test.iloc[i])
                
                if top_1_pred == true_label:
                    correct_top_1 += 1
                    
                top_2_predictions = np.argsort(y_proba[i])[-2:]
                top_2_class_labels = [class_labels[idx] for idx in top_2_predictions]
                
                if true_label in top_2_predictions:
                    correct_top_2 += 1
                    
                
                if top_1_prob >= confidence_threshold:
                    # Model is confident enough to make a single prediction
                    self.stdout.write(f"Sample {i + 1}: Confident Prediction: {class_labels[top_1_pred]}, Probability: {top_1_prob:.2f}, Actual: {class_labels[class_labels.index(y_test.iloc[i])]}")
                else:
                    # Model is not confident, provide top-2 predictions
                    self.stdout.write(f"Sample {i + 1}: Uncertain, Top-2 Predictions: {top_2_class_labels}, Actual: {class_labels[class_labels.index(y_test.iloc[i])]}")
            
            top_1_accuracy = correct_top_1 / len(y_test)
            top_2_accuracy = correct_top_2 / len(y_test)
            
            self.stdout.write(f"\nTop-1 Prediction Accuracy: {top_1_accuracy:.2f}")
            self.stdout.write(f"Top-2 Prediction Accuracy: {top_2_accuracy:.2f}")
            
            top_1_accurcies.append(top_1_accuracy)
            top_2_accuracies.append(top_2_accuracy)
            
        
        joblib.dump(model, "match_prediction_model.pkl")
        # Evaluate top-1 predictions (for comparison)
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
