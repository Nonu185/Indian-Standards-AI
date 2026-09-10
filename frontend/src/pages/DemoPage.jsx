import { useState } from 'react';
import RecommendationList from '../components/recommendation/RecommendationList';
import api from '../services/api';

function DemoPage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Call standard Node/Express endpoint which proxies/calls FastAPI
      const response = await api.post('/recommendations', { requirement: query });
      
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'An error occurred during search.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900">
            Indian Standards AI (Demo)
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Standalone recommendation flow with BIS live discovery fallback
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSearch}>
          <div className="rounded-md shadow-sm -space-y-px">
            <input
              id="search-query"
              name="query"
              type="text"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-4 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-lg"
              placeholder="Describe your procurement requirement (e.g., Portland Cement Grade 43)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:bg-gray-400 cursor-pointer"
            >
              {loading ? 'Searching (May take longer if fallback is triggered)...' : 'Find Standards'}
            </button>
          </div>
        </form>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {result && result.recommendations && (
          <div className="mt-8 bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-bold mb-4 border-b pb-2">Results</h3>
            <RecommendationList recommendations={result.recommendations} />
          </div>
        )}
      </div>
    </div>
  );
}

export default DemoPage;
