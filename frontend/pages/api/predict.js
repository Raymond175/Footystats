export default function predictionHandler(req, res) {
  console.log('Request method:', req.method);
  
  if (req.method === 'POST') {
    const { matchId } = req.body;
    console.log('Received matchId:', matchId);

    if (!matchId) {
      console.error('No matchId provided');
      return res.status(400).json({ error: 'Match ID is required' });
    }

    const mockPredictions = {
      1: 'Real Madrid will win',
      2: 'Liverpool and Manchester City will draw',
      3: 'Chelsea will win',
    };

    const prediction = mockPredictions[matchId] || 'No prediction available';
    return res.status(200).json({ prediction });
  }

  console.error('Method not allowed');
  return res.status(405).json({ error: 'Method Not Allowed' });
}
