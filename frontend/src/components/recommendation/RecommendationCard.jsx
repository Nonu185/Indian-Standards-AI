import { useState } from 'react';
import ApplicabilityScore from './ApplicabilityScore';

// Modal for detailed view of a recommendation
function DetailsModal({ recommendation, onClose }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-gray-100">
          <div>
            <span className="text-xs font-semibold text-primary-700 bg-primary-50 px-2 py-1 rounded-md">
              {recommendation.standardNumber}
            </span>
            <h2 className="mt-2 text-lg font-semibold text-gray-900">{recommendation.title}</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors ml-4 cursor-pointer"
            aria-label="Close"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Score */}
          <ApplicabilityScore score={recommendation.applicabilityScore} />

          {/* Scope */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Scope</h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              {recommendation.scope || 'Scope details not available.'}
            </p>
          </div>

          {/* Why recommended */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Why Recommended?</h3>
            <ul className="space-y-1.5">
              {recommendation.reasons.map((reason, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                  <svg className="w-4 h-4 text-primary-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  {reason}
                </li>
              ))}
            </ul>
          </div>

          {/* Phase 2 placeholders */}
          {[
            'Technical Requirements',
            'Related Standards',
            'Certification Requirements (QCO/BIS)',
          ].map((section) => (
            <div key={section} className="border border-dashed border-gray-200 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-gray-500 mb-1">{section}</h3>
              <p className="text-xs text-gray-400 italic">
                Available in Phase 2 — AI/RAG pipeline implementation.
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Individual recommendation card
function RecommendationCard({ recommendation }) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <>
      <div className="bg-white border border-gray-200 rounded-xl p-4 hover:border-primary-200 hover:shadow-sm transition-all duration-150">
        {/* Standard number badge */}
        <div className="flex items-start justify-between gap-2 mb-3">
          <span className="text-xs font-semibold text-primary-700 bg-primary-50 px-2.5 py-1 rounded-md border border-primary-100">
            {recommendation.standardNumber}
          </span>
        </div>

        {/* Title */}
        <h3 className="text-sm font-semibold text-gray-900 mb-3 leading-snug">
          {recommendation.title}
        </h3>

        {/* Applicability score */}
        <div className="mb-3">
          <ApplicabilityScore score={recommendation.applicabilityScore} />
        </div>

        {/* Reasons */}
        <div className="mb-4">
          <p className="text-xs font-medium text-gray-500 mb-1.5">Why recommended?</p>
          <ul className="space-y-1">
            {recommendation.reasons.slice(0, 2).map((reason, i) => (
              <li key={i} className="flex items-start gap-1.5 text-xs text-gray-600">
                <svg className="w-3.5 h-3.5 text-primary-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                {reason}
              </li>
            ))}
            {recommendation.reasons.length > 2 && (
              <li className="text-xs text-gray-400 pl-5">
                +{recommendation.reasons.length - 2} more reason{recommendation.reasons.length - 2 > 1 ? 's' : ''}
              </li>
            )}
          </ul>
        </div>

        {/* View Details */}
        <button
          id={`view-details-${recommendation.standardNumber.replace(/\s/g, '-')}`}
          onClick={() => setShowDetails(true)}
          className="w-full text-xs font-medium text-primary-700 border border-primary-200 rounded-lg py-2 hover:bg-primary-50 transition-colors duration-150 cursor-pointer"
        >
          View Details
        </button>
      </div>

      {showDetails && (
        <DetailsModal
          recommendation={recommendation}
          onClose={() => setShowDetails(false)}
        />
      )}
    </>
  );
}

export default RecommendationCard;
