"use client";

import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function MatchStatsPage() {
  const { league, matchId } = useParams();
  const decodedLeague = decodeURIComponent(league); // Decode the URL-encoded league name
  const [matchStats, setMatchStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMatchStats = async () => {
      setLoading(true);
      try {
        // Replace with your actual Django API endpoint
        const response = await fetch(`/api/match-stats/${decodedLeague}/${matchId}`);
        const data = await response.json();
        setMatchStats(data);
      } catch (error) {
        console.error('Error fetching match stats:', error);
      }
      setLoading(false);
    };

    fetchMatchStats();
  }, [decodedLeague, matchId]);

  if (loading) return <p>Loading match stats...</p>;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto bg-gray-100 text-gray-800 p-6 rounded-lg shadow-lg">
        <h1 className="text-center text-3xl font-bold mb-4">
          {decodedLeague}: {matchStats?.home_team} vs {matchStats?.away_team}
        </h1>
        <p><strong>Home PPG:</strong> {matchStats?.home_ppg}</p>
        <p><strong>Away PPG:</strong> {matchStats?.away_ppg}</p>
        <p><strong>Head-to-Head:</strong> {matchStats?.head_to_head}</p>
      </div>
    </div>
  );
}
