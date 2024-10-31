export default function handler(req, res) {
    if (req.method === 'GET') {
      // Mock data to simulate predictions stored in the database
      const mockPredictions = [
        {
          id: 1,
          matchId: 1,
          homeTeam: 'Real Madrid',
          awayTeam: 'Barcelona',
          date: '2024-10-22',
          time: '20:00',
          prediction: 'Real Madrid will win',
          predictedAt: '2024-10-20 18:30:00',
          actualOutcome: 'Real Madrid won', // You can later fetch this from your Django backend
        },
        {
          id: 2,
          matchId: 2,
          homeTeam: 'Liverpool',
          awayTeam: 'Manchester City',
          date: '2024-10-22',
          time: '18:00',
          prediction: 'Liverpool and Manchester City will draw',
          predictedAt: '2024-10-20 19:00:00',
          actualOutcome: 'Draw', // Mocking actual result
        },
        {
          id: 3,
          matchId: 3,
          homeTeam: 'Chelsea',
          awayTeam: 'Arsenal',
          date: '2024-10-23',
          time: '19:00',
          prediction: 'Chelsea will win',
          predictedAt: '2024-10-21 10:45:00',
          actualOutcome: 'Chelsea won', // Mocking actual result
        },
      ];
  
      // Return mock data as a JSON response
      return res.status(200).json(mockPredictions);
    } else {
      // Handle unsupported methods
      return res.status(405).json({ message: 'Method Not Allowed' });
    }
  }
  