"use client";
import Link from 'next/link'
import { useState, useEffect } from 'react'

export default function Navbar() {
  const [loading, setLoading] = useState(true);
  const [leagues, setLeagues] = useState([]);
  useEffect(() => {
    const fetchLeagues = async () => {
      setLoading(true);
      try {
        // Replace with your actual Django API endpoint
        const response = await fetch(
          `http://127.0.0.1:8000/footstatsapi/leagues/`
        );
        const data = await response.json();
        setLeagues(data);
      } catch (error) {
        console.error("Error fetching match stats:", error);
      }
      setLoading(false);
    };

    fetchLeagues();
  }, []);

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const path = '/leagueTable/';

  return (
   <nav className="bg-green-800 p-4">
      <div className="container mx-auto">
        <ul className="flex justify-center space-x-6">
          <li>
            <Link href="/" className="text-white text-lg font-bold hover:text-gray-200">
              Home
            </Link>
          </li>
          <li>
            <Link href="/menu" className="text-white text-lg font-bold hover:text-gray-200">
              Menu
            </Link>
          </li>
                   {/* League Stats Dropdown */}
          <li className="relative">
            <button
              className="text-white text-lg font-bold hover:text-gray-200"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            >
              League Stats
            </button>

            {isDropdownOpen && (
              <ul className="absolute bg-white text-green-800 mt-2 rounded-lg shadow-lg w-48">
                {leagues.map((league) => (
                  <li key={league.id} className="hover:bg-green-800 hover:text-white">
                    <Link
                      href={path + league.id}
                      className="block px-4 py-2 z-50"
                      onClick={() => setIsDropdownOpen(false)}  // Close dropdown after click
                    >
                      {league.name}
                      {league.logo && (
                        <img src={league.logo} alt={league.name} className="w-6 h-6 inline-block ml-2" />
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </li>
          <li>
          <Link href="/betsplaced" className='text-white text-lg font-bold hover:text-gray-200'>
            Bets placed
          </Link>
          </li> 
          <li>
          <Link href="/predictions" className='text-white text-lg font-bold hover:text-gray-200'>
            Predictions
          </Link>
          </li> 
        </ul>
      </div>
    </nav>
  )
}