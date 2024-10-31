from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('league-stats/<str:league_name>/<str:season>/', views.league_stats_view, name='league-stats'), 
    path("todays_games/", views.TodayFixtureView.as_view(), name="todays_games"),
    path("predict_outcomes/", views.MatchPredictionView.as_view(), name="predict_outcomes"),
    path("predictions/", views.PredictionListView.as_view(), name="predictions"),
    path("league-table/<int:league_id>/<str:season>/", views.LeagueTableView.as_view(), name="league-table"),
    path("<str:league_name>/<int:match_id>/", views.MatchStatsView.as_view(), name="match-stats"),
    path("upcoming-games/<int:league_id>/", views.get_upcoming_league_games, name="upcoming-games"),
    path("leagues/", views.get_all_leagues, name="leagues"),
]