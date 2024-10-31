// pages/api/upcoming-games/[league].js

export default function handler(req, res) {
  const { league } = req.query;
  const decodedLeague = decodeURIComponent(league);

  const upcomingGames = {
    "premier league": [
      {
        id: 201,
        home_team: 'Arsenal',
        away_team: 'Manchester United',
        date: '2024-10-25',
        time: '18:00',
      },
    ],
    "la liga": [
      {
        id: 101,
        home_team: 'Real Madrid',
        away_team: 'Barcelona',
        date: '2024-11-01',
        time: '20:00',
      },
    ],
  };

  const games = upcomingGames[decodedLeague.toLowerCase()] || [];

  res.status(200).json(games);
}
