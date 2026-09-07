// Shown when a chat has no messages yet
function EmptyChat() {
  return (
    <div className="flex flex-col items-center justify-center h-full px-6 py-12 text-center">
      {/* Brand mark */}
      <div className="w-14 h-14 bg-primary-700 rounded-2xl flex items-center justify-center mb-5 shadow-sm">
        <span className="text-white font-bold text-lg">IS</span>
      </div>

      <h2 className="text-xl font-semibold text-gray-900 mb-2">Indian Standards AI</h2>
      <p className="text-sm text-gray-500 max-w-sm leading-relaxed">
        Describe your procurement requirement and I'll help identify potentially applicable
        Indian Standards.
      </p>
    </div>
  );
}

export default EmptyChat;

