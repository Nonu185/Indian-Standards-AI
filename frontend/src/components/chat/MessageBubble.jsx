function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[75%] bg-primary-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-sm">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[85%] space-y-2">
        {/* Assistant avatar + message */}
        <div className="flex items-start gap-3">
          <div className="w-7 h-7 bg-primary-700 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
            <span className="text-white text-xs font-bold">IS</span>
          </div>
          <div className="bg-gray-50 border border-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
            <p className="text-sm text-gray-800 leading-relaxed">{message.content}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MessageBubble;

