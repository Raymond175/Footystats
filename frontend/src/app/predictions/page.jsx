"use client"; // Ensure this component runs on the client

import React, { useEffect, useState } from "react";

export default function PredictionsPage() {
  const [predictions, setPredictions] = useState([]);
  const [totalPredictions, setTotalPredictions] = useState(0);
  const [correctPredictions, setCorrectPredictions] = useState(0);
  const [accuracy, setAccuracy] = useState(0);
  const [loading, setLoading] = useState(false);

  // Fetch predictions from localStorage (mocking database call)
  // useEffect(() => {
  //   const savedPredictions =
  //     JSON.parse(localStorage.getItem("predictions")) || [];
  //   setPredictions(savedPredictions);

  //   // Calculate total predictions
  //   const total = savedPredictions.length;
  //   setTotalPredictions(total);

  //   // Calculate correct predictions
  //   let correct = 0;
  //   savedPredictions.forEach((prediction) => {
  //     // Check if the prediction matches the actual outcome (mocked)
  //     if (isPredictionCorrect(prediction)) {
  //       correct++;
  //     }
  //   });

  //   setCorrectPredictions(correct);

  //   // Calculate accuracy percentage
  //   const accuracyPercentage = total > 0 ? (correct / total) * 100 : 0;
  //   setAccuracy(accuracyPercentage.toFixed(2)); // Keep it to two decimal places
  // }, []);

  useEffect(() => {
    const getAllPredictions = async () => {
      setLoading(true);
      try {
        // Replace with your actual Django API endpoint
        const response = await fetch(
          `http://127.0.0.1:8000/footstatsapi/predictions/`
        );
        const data = await response.json();
        setPredictions(data);
        const total = data.length;
        setTotalPredictions(total);

        let correct = 0;
        data.forEach((prediction) => {
          // Check if the prediction matches the actual outcome (mocked)
          if (isPredictionCorrect(prediction)) {
            correct++;
          }
        });

        setCorrectPredictions(correct);

        // Calculate accuracy percentage
        const accuracyPercentage = total > 0 ? (correct / total) * 100 : 0;
        setAccuracy(accuracyPercentage.toFixed(2));
      } catch (error) {
        console.error("Error fetching match stats:", error);
      }
      setLoading(false);
    };

    getAllPredictions();
  }, []);

  // Function to check if a prediction matches the actual outcome (mocked for now)
  // const isPredictionCorrect = (prediction) => {
  //   const actualOutcomes = {
  //     1: "Real Madrid will win", // Mocked actual outcomes
  //     2: "Draw",
  //     3: "Chelsea will win",
  //   };
  //   return prediction.prediction === actualOutcomes[prediction.matchId];
  // };

  function formatTimestamp(isoString) {
    const date = new Date(isoString);
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }

  return (
    <div className="min-h-screen bg-gray-800 text-white p-8">
      <div className="max-w-4xl mx-auto bg-white text-gray-800 p-6 rounded-lg shadow-lg">
        <h1 className="text-center text-3xl font-bold mb-6">
          Predictions & Results
        </h1>

        {/* Display total predictions and accuracy */}
        <div className="text-center mb-6">
          <p className="text-xl">
            <strong>Total Predictions:</strong> {totalPredictions}
          </p>
          <p className="text-xl">
            <strong>Accuracy:</strong> {accuracy}% ({correctPredictions}/
            {totalPredictions} correct)
          </p>
        </div>

        {/* Display each prediction */}
        {predictions.length > 0 ? (
          predictions.map((prediction, index) => (
            <div key={index} className="mb-6 border-b border-gray-300 pb-4">
              <h2 className="text-xl font-bold mb-2">
              {prediction.away_team} vs {prediction.home_team} (
                {prediction.date}, {prediction.time})
              </h2>
              <p>
                <strong>Prediction:</strong> {prediction.prediction}
              </p>
              <p>
                <strong>Predicted At:</strong> {formatTimestamp(prediction.predicted_at)}
              </p>
              <p>
                <strong>Actual Outcome:</strong> {/* Mocked actual outcome */}
                {prediction.prediction.includes("win")
                  ? `${prediction.homeTeam} won`
                  : "Draw"}
              </p>
            </div>
          ))
        ) : (
          <p className="text-center text-xl text-red-700">
            No predictions made yet.
          </p>
        )}
      </div>
    </div>
  );
}
