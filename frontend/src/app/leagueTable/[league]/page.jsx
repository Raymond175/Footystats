"use client";

import { useRouter, useParams } from "next/navigation";
import React, { useEffect, useState } from "react";

export default function LeaguePage() {
  const { league } = useParams(); // Get the league from the path
  const decodedLeague = decodeURIComponent(league);
  const [leagueTable, setLeagueTable] = useState([]);
  const [upcomingGames, setUpcomingGames] = useState([]);
  const [Loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeagueData = async () => {
      setLoading(true);
  
      try {
        // Fetch league table
        const leagueTableResponse = await fetch(`http://127.0.0.1:8000/footstatsapi/league-table/${decodedLeague}/2024-2025/`);
        const leagueTableData = await leagueTableResponse.json();
  
        // Fetch upcoming games
        const upcomingGamesResponse = await fetch(`/api/upcoming-games/${decodedLeague}`);
        const upcomingGamesData = await upcomingGamesResponse.json();
  
        setLeagueTable(leagueTableData);
        setUpcomingGames(upcomingGamesData);
      } catch (error) {
        console.error('Error fetching league data:', error);
      } finally {
        setLoading(false);
      }
    };
  
    fetchLeagueData();
  }, [decodedLeague]);

  const router = useRouter();

  // Navigate to the match stats page for each game
  const viewMatchStats = (matchId) => {
    router.push(`/leagueTable/${league}/${matchId}`);
  };

  if (Loading) return <p>Loading league data...</p>;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
  <div className="max-w-4xl mx-auto bg-white text-gray-800 p-6 rounded-lg shadow-lg overflow-hidden">
    <h1 className="text-center text-3xl font-bold mb-4">League Table</h1>

    {/* League Table */}
    <div className="overflow-x-auto">
      <table className="table-fixed w-full mb-8">
        <thead>
          <tr className="bg-gray-200">
            <th className="px-2 py-1 w-8">Pos</th>
            <th className="px-2 py-1 w-24">Team</th>
            <th className="px-2 py-1 w-8">MP</th>
            <th className="px-2 py-1 w-8">W</th>
            <th className="px-2 py-1 w-8">D</th>
            <th className="px-2 py-1 w-8">L</th>
            <th className="px-2 py-1 w-8">GS</th>
            <th className="px-2 py-1 w-8">GA</th>
            <th className="px-2 py-1 w-8">GD</th>
            <th className="px-2 py-1 w-24">Form</th>
            <th className="px-2 py-1 w-12">PPG</th>
            <th className="px-2 py-1 w-12">CS%</th>
            <th className="px-2 py-1 w-12">FTS%</th>
          </tr>
        </thead>
        <tbody>
          {leagueTable.map((team, index) => (
            <tr key={index} className="text-center">
              <td className="border px-2 py-1 text-sm">{team.position}</td>
              <td className="border px-2 py-1 text-sm">{team.team}</td>
              <td className="border px-2 py-1 text-sm">{team.matches_played}</td>
              <td className="border px-2 py-1 text-sm">{team.wins}</td>
              <td className="border px-2 py-1 text-sm">{team.draws}</td>
              <td className="border px-2 py-1 text-sm">{team.losses}</td>
              <td className="border px-2 py-1 text-sm">{team.goals_scored}</td>
              <td className="border px-2 py-1 text-sm">{team.goals_conceded}</td>
              <td className="border px-2 py-1 text-sm">{team.goal_difference}</td>
              <td className="border px-2 py-1 text-sm">
                {team.form.map((result, idx) => (
                  <span
                    key={idx}
                    className={`inline-block w-4 h-4 mx-0.5 rounded-full ${
                      result === 'W' ? 'bg-green-500' : result === 'D' ? 'bg-gray-500' : 'bg-red-500'
                    }`}
                  ></span>
                ))}
              </td>
              <td className="border px-2 py-1 text-sm">{team.ppg}</td>
              <td className="border px-2 py-1 text-sm">{team.clean_sheets_percentage}%</td>
              <td className="border px-2 py-1 text-sm">{team.failed_to_score_percentage}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>

    {/* Upcoming Games */}
    <h2 className="text-center text-2xl font-bold mb-4">Upcoming Games</h2>
    {upcomingGames.length > 0 ? (
      upcomingGames.map((game) => (
        <div key={game.id} className="mb-4 border-b border-gray-300 pb-4">
          <h3 className="text-xl font-bold">
            {game.home_team} vs {game.away_team}
          </h3>
          <p>
            <strong>Date:</strong> {game.date} | <strong>Kick-off:</strong> {game.time} CET
          </p>
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-4"
            onClick={() => viewMatchStats(game.id)}
          >
            View Match Stats
          </button>
        </div>
      ))
    ) : (
      <p className="text-center text-xl text-red-700">
        No upcoming games in the next 7 days.
      </p>
    )}
  </div>
</div>

  );
}
