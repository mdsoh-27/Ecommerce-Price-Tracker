import React, { useState } from "react";
import { trackProduct, getPriceHistory } from "./services/api";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<any[]>([]);

  const handleTrack = async () => {
    if (!query.trim()) {
      setError("Please enter a product name");
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      console.log('Tracking product:', query);
      const data = await trackProduct(query);
      console.log('Response:', data);
      setResults(data);

      if (!data.results || data.results.length === 0) {
        setError("No products found. Try a different search term.");
      }
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.message || "Failed to fetch product data. Make sure the backend is running on http://localhost:5000");
    } finally {
      setLoading(false);
    }
  };

  const handleViewHistory = async () => {
    if (!query.trim()) return;

    try {
      console.log('Fetching history for:', query);
      const data = await getPriceHistory(query);
      console.log('History data:', data);
      setHistory(data);

      if (!data || data.length === 0) {
        setError("No price history available for this product yet.");
      }
    } catch (err: any) {
      console.error('History error:', err);
      setError(err.message || "Failed to fetch price history");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      handleTrack();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white flex flex-col items-center justify-center p-6">
      <div className="max-w-6xl w-full">
        <h1 className="text-5xl font-bold mb-2 text-center">
          <span className="bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
            E-Commerce
          </span>{" "}
          Price Tracker 🛒
        </h1>
        <p className="text-center text-gray-400 mb-8">Track prices from Flipkart and save money!</p>

        <div className="flex space-x-2 w-full max-w-2xl mx-auto mb-4">
          <input
            type="text"
            placeholder="Enter product name (e.g., laptop, iphone, headphones)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-grow p-4 rounded-lg text-black text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            onClick={handleTrack}
            disabled={loading}
            className="bg-gradient-to-r from-blue-600 to-blue-700 px-8 py-4 rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-semibold text-lg shadow-lg hover:shadow-xl"
          >
            {loading ? "Tracking..." : "Track"}
          </button>
        </div>

        {error && (
          <div className="mt-4 bg-red-500/20 border border-red-500 text-red-200 p-4 rounded-lg max-w-2xl mx-auto">
            <p className="font-semibold">⚠️ Error</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        {loading && (
          <div className="mt-8 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
            <p className="mt-4 text-gray-400">Searching Flipkart...</p>
          </div>
        )}

        {results && results.results && results.results.length > 0 && (
          <div className="mt-8 bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 shadow-2xl w-full max-w-4xl mx-auto border border-gray-700">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-semibold text-yellow-400">
                Results from Flipkart ({results.count || results.results.length})
              </h2>
              <button
                onClick={handleViewHistory}
                className="bg-green-600 px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
              >
                📊 View Price History
              </button>
            </div>

            <div className="grid grid-cols-1 gap-3 max-h-96 overflow-y-auto pr-2">
              {results.results.map((item: any, idx: number) => (
                <div
                  key={idx}
                  className="bg-gray-700/50 p-4 rounded-lg flex justify-between items-center hover:bg-gray-700 transition-colors border border-gray-600"
                >
                  <span className="flex-1 pr-4">{item.name}</span>
                  <span className="font-bold text-xl text-green-400">₹{item.price}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {history.length > 0 && (
          <div className="mt-8 bg-gray-800/50 backdrop-blur-sm p-6 rounded-xl w-full max-w-4xl mx-auto border border-gray-700 shadow-2xl">
            <h2 className="text-2xl font-semibold mb-6 text-yellow-400">
              📈 Price History for "{query}"
            </h2>

            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="timestamp"
                  tick={{ fill: "#9CA3AF", fontSize: 12 }}
                  stroke="#4B5563"
                />
                <YAxis
                  tick={{ fill: "#9CA3AF", fontSize: 12 }}
                  stroke="#4B5563"
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#10B981"
                  strokeWidth={3}
                  dot={{ fill: '#10B981', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {!loading && !results && !error && (
          <div className="mt-12 text-center text-gray-400">
            <p className="text-lg">👆 Enter a product name above to start tracking prices</p>
            <p className="text-sm mt-2">Try: laptop, iphone, headphones, mouse, keyboard</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
