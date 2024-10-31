from django.db import models
from django.core.exceptions import ValidationError

class League(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    logo = models.URLField(null=True, blank=True)
    flag = models.URLField(null=True, blank=True)

class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    logo = models.URLField()
    
    def __str__(self):
        return self.name

class Fixture(models.Model):
    id = models.IntegerField(primary_key=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, related_name='home_fixtures', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_fixtures', on_delete=models.CASCADE)
    date = models.DateTimeField(null=True, blank=True)
    season = models.CharField(max_length=9, null=True, blank=True)
    referee = models.CharField(max_length=100, null=True, blank=True)
    venue_name = models.CharField(max_length=100, null=True, blank=True)
    venue_city = models.CharField(max_length=100, null=True, blank=True)
    status_long = models.CharField(max_length=100, null=True, blank=True)
    status_short = models.CharField(max_length=20, null=True, blank=True)
    status_elapsed = models.IntegerField(null=True, blank=True)
    goals_home = models.IntegerField(null=True, blank=True)
    goals_away = models.IntegerField(null=True, blank=True)
    score_halftime_home = models.IntegerField(null=True, blank=True)
    score_halftime_away = models.IntegerField(null=True, blank=True)
    score_fulltime_home = models.IntegerField(null=True, blank=True)
    score_fulltime_away = models.IntegerField(null=True, blank=True)

    def clean(self):
        if self.status_long == "Match Finished":
            if self.goals_home is None or self.goals_away is None:
                raise ValidationError("Match Finished but no score provided")
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)     
                
    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} on {self.date.strftime('%Y-%m-%d')}"

class Prediction(models.Model):
    match = models.ForeignKey('Fixture', on_delete=models.CASCADE)
    home_team = models.CharField(max_length=100, null=True, blank=True)
    away_team = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    prediction = models.CharField(max_length=255)
    predicted_at = models.DateTimeField(auto_now_add=True)
    actual_outcome = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Prediction for Match {self.match.id}: {self.prediction}"