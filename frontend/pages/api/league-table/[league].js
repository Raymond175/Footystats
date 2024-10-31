// pages/api/league-table/[league].js

export default function handler(req, res) {
  const { league } = req.query;
  const decodedLeague = decodeURIComponent(league); // Decode the league name

  // Mock data for league tables
  const leagueTables = {
    "premier league": [
      { position: 1, team: 'Arsenal', points: 47 },
      { position: 2, team: 'Manchester United', points: 46 },
      { position: 3, team: 'Chelsea', points: 40 },
    ],
    "la liga": [
      { position: 1, team: 'Real Madrid', points: 55 },
      { position: 2, team: 'Barcelona', points: 52 },
      { position: 3, team: 'Atletico Madrid', points: 49 },
    ],
  };

  const leagueTable = leagueTables[decodedLeague.toLowerCase()] || [];

  res.status(200).json(leagueTable);
}
