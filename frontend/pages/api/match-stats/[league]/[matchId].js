// pages/api/match-stats/[league]/[matchId].js

export default function handler(req, res) {
  const { league, matchId } = req.query;
  const decodedLeague = decodeURIComponent(league);

  // Mock match stats data
  const matchStats = {
    "la liga": {
      101: {
        home_team: 'Real Madrid',
        away_team: 'Barcelona',
        home_ppg: 2.5,
        away_ppg: 1.8,
        head_to_head: 'Real Madrid has won 3 of the last 5 games against Barcelona',
      },
      102: {
        home_team: 'Atletico Madrid',
        away_team: 'Sevilla',
        home_ppg: 2.3,
        away_ppg: 1.6,
        head_to_head: 'Atletico Madrid has won 4 of the last 5 games against Sevilla',
      },
    },
    "premier league": {
      201: {
        home_team: 'Arsenal',
        away_team: 'Manchester United',
        home_ppg: 2.6,
        away_ppg: 1.9,
        head_to_head: 'Arsenal has won 3 of the last 5 games against Manchester United',
      },
      202: {
        home_team: 'Chelsea',
        away_team: 'Liverpool',
        home_ppg: 2.2,
        away_ppg: 2.0,
        head_to_head: 'Chelsea and Liverpool have each won 2 of the last 5 games against each other',
      },
    },
  };

  // Retrieve match data for the league and matchId
  const leagueData = matchStats[decodedLeague.toLowerCase()] || {};
  const matchData = leagueData[matchId] || null;

  if (matchData) {
    res.status(200).json(matchData);
  } else {
    res.status(404).json({ error: 'Match not found' });
  }
}
