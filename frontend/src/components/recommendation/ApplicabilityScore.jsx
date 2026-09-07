// Displays the applicability score as a labeled percentage with a green progress bar
function ApplicabilityScore({ score }) {
  // Color based on score range
  const getScoreColor = (s) => {
    if (s >= 85) return 'bg-primary-600';
    if (s >= 70) return 'bg-primary-500';
    if (s >= 55) return 'bg-yellow-500';
    return 'bg-orange-400';
  };

  const getScoreTextColor = (s) => {
    if (s >= 85) return 'text-primary-700';
    if (s >= 70) return 'text-primary-600';
    if (s >= 55) return 'text-yellow-600';
    return 'text-orange-500';
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
          Applicability Score
        </span>
        <span className={`text-sm font-bold ${getScoreTextColor(score)}`}>
          {score}%
        </span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${getScoreColor(score)}`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}

export default ApplicabilityScore;
