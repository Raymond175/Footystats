from footstatsapi.models import League
def get_league_id_from_name(league_name):
    """
    Get league ID from league name.
    """
    try:
        league = League.objects.get(name=league_name)
        return league.id
    except League.DoesNotExist:
        return None