"use client"; // Ensure this component runs on the client

import React, { useState, useEffect } from "react";

export default function Menu() {
  const [matches, setMatches] = useState([]);

  useEffect(() => {
    const fetchMatches = async () => {
      setLoading(true);
      try {
        // Replace with your actual Django API endpoint
        const response = await fetch(
          `http://127.0.0.1:8000/footstatsapi/todays_games/`
        );
        const data = await response.json();
        setMatches(data);
      } catch (error) {
        console.error("Error fetching match stats:", error);
      }
      setLoading(false);
    };

    fetchMatches();
  }, []);

  const [predictions, setPredictions] = useState({});
  const [loading, setLoading] = useState({});

  // Helper function to group matches by league
  const groupMatchesByLeague = (matches) => {
    return matches.reduce((groups, match) => {
      const league = match.league;
      if (!groups[league]) {
        groups[league] = [];
      }
      groups[league].push(match);
      return groups;
    }, {});
  };

  const getPrediction = async (match) => {
    setLoading((prev) => ({ ...prev, [match.id]: true }));
    
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/footstatsapi/predict_outcomes/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },  
          body: JSON.stringify({
            home_team_id: match.home_team,
            away_team_id: match.away_team,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch prediction");
      }

      const data = await response.json();
      const { prediction, probabilities } = data;

      setPredictions((prev) => ({
        ...prev,
        [match.id]: {
          prediction,
          probabilities,
        },
      }));
    } catch (error) {
      console.error("Error fetching prediction:", error);
      setPredictions((prev) => ({
        ...prev,
        [match.id]: { error: "Unable to fetch prediction." },
      }));
    } finally {
      setLoading((prev) => ({ ...prev, [match.id]: false }));
    }
  };

  // Group matches by league
  const groupedMatches = groupMatchesByLeague(matches);

  return (
    <div className="min-h-screen bg-green-800 text-white p-8">
      <div className="max-w-4xl mx-auto bg-white text-green-800 p-6 rounded-lg shadow-lg">
        <h1 className="text-center text-3xl font-bold mb-4">Today's Matches</h1>

        {Object.keys(groupedMatches).length > 0 ? (
          Object.keys(groupedMatches).map((league) => (
            <div key={league} className="mb-8">
              {/* Display the league logo and name */}
              <div className="flex items-center justify-center mb-4">
                <img
                  src={groupedMatches[league][0].leagueLogo}
                  alt={`${league} logo`}
                  className="w-12 h-12 mr-2"
                />
                <h2 className="text-center text-2xl font-bold">{league}</h2>
              </div>

              {/* Display matches for the league */}
              {groupedMatches[league].map((match) => (
                <div key={match.id} className="mb-4">
                  <div className="flex items-center justify-center mb-2">
                    {/* Home team logo */}
                    <img
                      src={match.homeTeamLogo}
                      alt={`${match.homeTeam} logo`}
                      className="w-10 h-10 mr-2"
                    />
                    <h3 className="text-xl font-bold">{match.homeTeam}</h3>
                    <span className="mx-2">vs</span>
                    {/* Away team logo */}
                    <h3 className="text-xl font-bold">{match.awayTeam}</h3>
                    <img
                      src={match.awayTeamLogo}
                      alt={`${match.awayTeam} logo`}
                      className="w-10 h-10 ml-2"
                    />
                  </div>
                  <p className="text-center">
                    <strong>Date:</strong> {match.date}
                  </p>
                  <p className="text-center">
                    <strong>Kick-off:</strong> {match.time} CET
                  </p>
                  <div className="text-center mt-4">
                    <button
                      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                      onClick={() => getPrediction(match)}
                      disabled={loading[match.id]} // Disable only for this match while loading
                    >
                      {loading[match.id] ? "Loading..." : "Get Prediction"}
                    </button>
                  </div>
                  {predictions[match.id] && !predictions[match.id].error && (
                    <div className="text-center mt-2">
                      <p>
                        <strong>Prediction:</strong>{" "}
                        {predictions[match.id].prediction}
                      </p>
                      <p>
                        <strong>Probabilities:</strong>
                      </p>
                      <ul>
                        {Object.entries(
                          predictions[match.id].probabilities
                        ).map(([key, value]) => (
                          <li key={key}>
                            {key === "H"
                              ? "Home Win"
                              : key === "D"
                              ? "Draw"
                              : "Away Win"}{" "}
                            ({key}): {(value * 100).toFixed(2)}%
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {predictions[match.id] && predictions[match.id].error && (
                    <div className="text-center mt-2 text-red-600">
                      <p>{predictions[match.id].error}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ))
        ) : (
          <p className="text-center text-xl text-red-700">
            No matches scheduled for today.
          </p>
        )}
      </div>
    </div>
  );
}
