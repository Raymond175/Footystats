import React from "react";

export default function Betsplaced() {
  const bets = [
    {
      betId: 1,
      team: "Liverpool vs Manchester City",
      amount: 100,
      odds: 2.5,
      status: "Won",
      date: "2024-10-22",
      market: "Match Winner",
      selection: "Liverpool",
    },
    {
      betId: 2,
      team: "Real Madrid vs Barcelona",
      amount: 50,
      odds: 1.8,
      status: "Lost",
      date: "2024-10-22",
      market: "Match Winner",
      selection: "Real Madrid",
    },
    {
      betId: 3,
      team: "Chelsea vs Arsenal",
      amount: 75,
      odds: 3.0,
      status: "Pending",
      date: "2024-10-22",
      market: "Match Winner",
      selection: "Chelsea",
    },
    {
      betId: 4,
      team: "Bayern Munich vs Borussia Dortmund",
      amount: 200,
      odds: 2.2,
      status: "Won",
      date: "2024-10-22",
      market: "Over/Under",
      selection: "Over 2.5",
    },
    {
      betId: 5,
      team: "Atletico Madrid vs Sevilla",
      amount: 120,
      odds: 1.9,
      status: "Lost",
      date: "2024-10-22",
      market: "Handicap",
      selection: "Atletico Madrid -1",
    },
  ];
  const calculateStats = (bets) => {
    const wonBets = bets.filter((bet) => bet.status === "Won");
    const lostBets = bets.filter((bet) => bet.status === "Lost");

    const totalBets = bets.length;
    const wonBetsCount = wonBets.length;
    const winPercentage = ((wonBetsCount / totalBets) * 100).toFixed(2);

    // Calculate total winnings for won bets and total losses for lost bets
    const totalWinnings = wonBets.reduce(
      (total, bet) => total + bet.amount * bet.odds,
      0
    );
    const totalLosses = lostBets.reduce((total, bet) => total + bet.amount, 0);

    // Net Winnings = Total Winnings - Total Losses
    const netWinnings = totalWinnings - totalLosses;
    return {
      totalBets,
      wonBetsCount,
      lostBetsCount: lostBets.length,
      winPercentage,
      netWinnings,
    };
  };
  const stats = calculateStats(bets);
    return (
      <div className="min-h-screen bg-green-800 text-white p-8">
        <div className="max-w-4xl mx-auto bg-white text-green-800 p-6 rounded-lg shadow-lg">
          <h1 className="text-center text-3xl font-bold mb-4">Bets Overview</h1>

          {/* Displaying statistics */}
          <div className="mb-8 text-center">
            <p>
              Total Bets: <strong>{stats.totalBets}</strong>
            </p>
            <p>
              Bets Won: <strong>{stats.wonBetsCount}</strong>
            </p>
            <p>
              Bets Lost: <strong>{stats.lostBetsCount}</strong>
            </p>
            <p>
              Win Percentage: <strong>{stats.winPercentage}%</strong>
            </p>
            <p>
              Net Winnings/Losses:{" "}
              <strong>
                {stats.netWinnings >= 0
                  ? `+$${stats.netWinnings.toFixed(2)}`
                  : `-$${Math.abs(stats.netWinnings).toFixed(2)}`}
              </strong>
            </p>
          </div>

          {/* Displaying bets in a table */}
          <div className="overflow-x-auto">
            <table className="table-auto w-full border-collapse">
              <thead>
                <tr className="bg-green-800 text-white">
                  <th className="px-4 py-2">Bet ID</th>
                  <th className="px-4 py-2">Match</th>
                  <th className="px-4 py-2">Bet type</th>
                  <th className="px-4 py-2">Amount ($)</th>
                  <th className="px-4 py-2">Odds</th>
                  <th className="px-4 py-2">Status</th>
                  <th className="px-4 py-2">Potential Winnings ($)</th>
                </tr>
              </thead>
              <tbody>
                {bets.map((bet) => (
                  <tr key={bet.betId} className="text-center">
                    <td className="border px-4 py-2">{bet.betId}</td>
                    <td className="border px-4 py-2">{bet.team} <br />{bet.date}</td>
                    <td className="border px-4 py-2">{bet.market}<br />{bet.selection}</td>
                    <td className="border px-4 py-2">
                      ${bet.amount.toFixed(2)}
                    </td>
                    <td className="border px-4 py-2">{bet.odds}</td>
                    <td
                      className={`border px-4 py-2 ${
                        bet.status === "Won"
                          ? "text-green-600"
                          : bet.status === "Lost"
                          ? "text-red-600"
                          : "text-yellow-600"
                      }`}
                    >
                      {bet.status}
                    </td>
                    <td className="border px-4 py-2">
                      {bet.status === "Won"
                        ? `$${(bet.amount * bet.odds).toFixed(2)}`
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };
