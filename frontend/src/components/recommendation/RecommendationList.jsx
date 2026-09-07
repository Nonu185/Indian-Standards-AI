import RecommendationCard from './RecommendationCard';

function RecommendationList({ recommendations }) {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <div className="mt-4 space-y-3">
      <div className="flex items-center gap-2 mb-3">
        <div className="h-px flex-1 bg-gray-100" />
        <span className="text-xs font-medium text-gray-400 px-2">
          {recommendations.length} Applicable Indian Standard{recommendations.length !== 1 ? 's' : ''} Found
        </span>
        <div className="h-px flex-1 bg-gray-100" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {recommendations.map((rec, index) => (
          <RecommendationCard key={`${rec.standardNumber}-${index}`} recommendation={rec} />
        ))}
      </div>
    </div>
  );
}

export default RecommendationList;
