import Image from "next/image";

export default function Home() {
  return (
    <div className="bg-green-900 text-white">
      {/* Hero Section */}
      <section className="bg-green-700 min-h-screen flex items-center justify-center">
        <div className="text-center px-4">
          <div className="container mx-auto flex justify-center">
            <div className="relative h-48 w-48 mb-5 shadow-lg rounded-full">
              <Image
                src="/favicon.ico"
                alt="Footstats logo"
                priority
                fill={true}
              />
            </div>
          </div>
          <h1 className="text-6xl font-bold text-white mb-6">
            Welcome to FootStats!
          </h1>
          <p className="text-lg text-white mb-8 max-w-2xl mx-auto">
            The ultimate football stats and data at your fingertips. Empower
            your apps, services, and websites with real-time football data, just
            like a football pitch empowers the game.
          </p>
          <a
            href="/menu"
            className="px-8 py-4 bg-white text-green-700 font-bold rounded-full shadow-lg hover:bg-gray-100 transition duration-300"
          >
            Check out
          </a>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white text-green-900">
        <div className="container mx-auto text-center">
          <h2 className="text-4xl font-bold mb-10">Why FootStats?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-green-100 shadow-lg rounded-lg p-8">
              <h3 className="text-2xl font-bold mb-4">Real-Time Data</h3>
              <p>
                Get live data from leagues, matches, and players to enhance your
                platform with up-to-date football insights.
              </p>
            </div>
            <div className="bg-green-100 shadow-lg rounded-lg p-8">
              <h3 className="text-2xl font-bold mb-4">Comprehensive Stats</h3>
              <p>
                Access detailed statistics on goals, assists, player
                performances, team rankings, and much more.
              </p>
            </div>
            <div className="bg-green-100 shadow-lg rounded-lg p-8">
              <h3 className="text-2xl font-bold mb-4">Easy Integration</h3>
              <p>
                Integrate our API effortlessly with your project. Full
                documentation and customer support included.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-green-700 py-20">
        <div className="container mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Start using FootStats today!
          </h2>
          <p className="text-lg text-white mb-10">
            Sign up for free and explore the power of football data at your
            fingertips.
          </p>
          <a
            href="#pricing"
            className="px-8 py-4 bg-white text-green-700 font-bold rounded-full shadow-lg hover:bg-gray-100 transition duration-300"
          >
            Sign Up Now
          </a>
        </div>
      </section>
    </div>
  );
}
