import pandas as pd
import numpy as np
from footstatsapi.models import Fixture, Prediction
import joblib
from django.utils import timezone
from django.db.models import Q
import os
from django.conf import settings
import logging

MODEL_PATH = os.path.join(settings.BASE_DIR, 'model', 'match_prediction_model.pkl')
logger = logging.getLogger(__name__)
def calculate_form(df, num_games=5):
    """
    Calculate the form of each team based on the last 5 games.
    """
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

def feature_engineering(df):
    """
    Perform feature engineering on the dataset.
    """
   # Creating home and away win rates
    df["home_win_rate"] = df.groupby("home_team_id")["result"].transform(lambda x: (x == "H").mean())
    df["away_win_rate"] = df.groupby("away_team_id")["result"].transform(lambda x: (x == "A").mean())
    
    # Creating home and away goals scored and conceded
    df["total_goals_scored_home"] = df.groupby("home_team_id")["goals_home"].transform("sum")
    df["total_goals_scored_away"] = df.groupby("away_team_id")["goals_away"].transform("sum")
    df["total_goals_conceded_home"] = df.groupby("home_team_id")["goals_away"].transform("sum")
    df["total_goals_conceded_away"] = df.groupby("away_team_id")["goals_home"].transform("sum")
    
    return df

def predict_outcomes(home_team_id, away_team_id):
    logger.info(f"Predicting outcome for home_team_id={home_team_id}, away_team_id={away_team_id}")
    # Load the trained model
    try:
        model = joblib.load('model/match_prediction_model.pkl')
    except FileNotFoundError as e:
        logger.error(f"Model not found. {e}")
        raise Exception("Trained model not found. Please ensure the model is trained and saved.")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise
    # Get recent matches to compute features
    N = 10  # Number of past games to consider (adjust as needed)

    # Fetch past matches for home team
    home_matches = pd.DataFrame(list(Fixture.objects.filter(
        Q(home_team_id=home_team_id) | Q(away_team_id=home_team_id),
        status_long="Match Finished",
        date__lt=timezone.now()
    ).order_by('-date').values(
        'home_team_id', 'away_team_id', 'goals_home', 'goals_away', 'date'
    )[:N]))

    # Fetch past matches for away team
    away_matches = pd.DataFrame(list(Fixture.objects.filter(
        Q(home_team_id=away_team_id) | Q(away_team_id=away_team_id),
        status_long="Match Finished",
        date__lt=timezone.now()
    ).order_by('-date').values(
        'home_team_id', 'away_team_id', 'goals_home', 'goals_away', 'date'
    )[:N]))

    try:
        # Combine and preprocess data
        recent_matches = pd.concat([home_matches, away_matches])
        if recent_matches.empty:
            raise Exception("Not enough data to make a prediction.")

        recent_matches["result"] = (recent_matches["goals_home"] - recent_matches["goals_away"]).apply(
            lambda x: "H" if x > 0 else ("A" if x < 0 else "D")
        )
    except Exception as e:
        logger.error(f"Error fetching recent matches: {e}")
        raise
    
    recent_matches = feature_engineering(recent_matches)
    recent_matches = calculate_form(recent_matches)

    
    # Calculate features for the home team
    home_stats = recent_matches[(recent_matches['home_team_id'] == home_team_id) | (recent_matches['away_team_id'] == home_team_id)]
    if home_stats.empty:
        home_win_rate = 0
        total_goals_scored_home = 0
        total_goals_conceded_home = 0
        home_form = 0
    else:
        home_win_rate = (home_stats['result'] == 'H').mean()
        total_goals_scored_home = home_stats.apply(
            lambda row: row['goals_home'] if row['home_team_id'] == home_team_id else row['goals_away'], axis=1
        ).sum()
        total_goals_conceded_home = home_stats.apply(
            lambda row: row['goals_away'] if row['home_team_id'] == home_team_id else row['goals_home'], axis=1
        ).sum()
        # Ensure the DataFrame is sorted by date
        home_stats = home_stats.sort_values(by='date')
        # Get the latest form for the home team
        last_match = home_stats.iloc[-1]
        if last_match['home_team_id'] == home_team_id:
            home_form = last_match['home_form']
        else:
            home_form = last_match['away_form']

    # Calculate features for the away team
    away_stats = recent_matches[(recent_matches['home_team_id'] == away_team_id) | (recent_matches['away_team_id'] == away_team_id)]
    if away_stats.empty:
        away_win_rate = 0
        total_goals_scored_away = 0
        total_goals_conceded_away = 0
        away_form = 0
    else:
        away_win_rate = (away_stats['result'] == 'A').mean()
        total_goals_scored_away = away_stats.apply(
            lambda row: row['goals_home'] if row['home_team_id'] == away_team_id else row['goals_away'], axis=1
        ).sum()
        total_goals_conceded_away = away_stats.apply(
            lambda row: row['goals_away'] if row['home_team_id'] == away_team_id else row['goals_home'], axis=1
        ).sum()
        # Ensure the DataFrame is sorted by date
        away_stats = away_stats.sort_values(by='date')
        # Get the latest form for the away team
        last_match = away_stats.iloc[-1]
        if last_match['home_team_id'] == away_team_id:
            away_form = last_match['home_form']
        else:
            away_form = last_match['away_form']

    # Prepare the feature vector
    match_features = {
        'home_win_rate': home_win_rate if not np.isnan(home_win_rate) else 0,
        'away_win_rate': away_win_rate if not np.isnan(away_win_rate) else 0,
        'total_goals_scored_home': total_goals_scored_home,
        'total_goals_scored_away': total_goals_scored_away,
        'total_goals_conceded_home': total_goals_conceded_home,
        'total_goals_conceded_away': total_goals_conceded_away,
        'home_form': home_form,
        'away_form': away_form,
    }

    # Ensure all features are present
    features = [
        'home_win_rate', 'away_win_rate', 'total_goals_scored_home', 'total_goals_scored_away',
        'total_goals_conceded_home', 'total_goals_conceded_away', 'home_form', 'away_form'
    ]
    X_new = pd.DataFrame([match_features], columns=features)

    # Handle missing values
    X_new = X_new.fillna(0)

    try:
        # Make prediction
        prediction = model.predict(X_new)[0]
        probabilities = model.predict_proba(X_new)[0]
        class_probabilities = dict(zip(model.classes_, probabilities))
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise
    
    match = Fixture.objects.filter(
        Q(home_team_id=home_team_id, away_team_id=away_team_id) |
        Q(home_team_id=away_team_id, away_team_id=home_team_id),
        date__gte=timezone.now()
    ).order_by('date').first()

    if not match:
        raise Exception("Match not found in upcoming fixtures.")

    # Extract date and time from match_datetime
    match_date = match.date.date()
    match_time = match.date.time()
    
    # **Extract team names**
    home_team_name = match.home_team.name  
    away_team_name = match.away_team.name
    
    # Map prediction codes to readable text
    prediction_text = {
        'H': f"{home_team_name} will win",
        'D': f"{home_team_name} and {away_team_name} will draw",
        'A': f"{away_team_name} will win"
    }.get(prediction, "Unknown prediction")

    # Save the prediction to the database
    prediction_instance = Prediction.objects.create(
        match=match,
        home_team=home_team_name,
        away_team=away_team_name,
        date=match_date,
        time=match_time,
        prediction=prediction_text,
    )

    return {
        'prediction': prediction,
        'probabilities': class_probabilities,
        'prediction_id': prediction_instance.id  # Return the ID if needed
    }