import { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import EmptyChat from './EmptyChat';

function ChatArea({ messages, loading }) {
  const bottomRef = useRef(null);

  // Auto-scroll to newest message
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading]);

  if (messages.length === 0 && !loading) {
    return <EmptyChat />;
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-1">
      <div className="max-w-3xl mx-auto">
        {messages.map((message) => (
          <MessageBubble key={message._id || message.tempId} message={message} />
        ))}

        {/* Loading indicator while waiting for assistant response */}
        {loading && (
          <div className="flex justify-start mb-4">
            <div className="flex items-start gap-3">
              <div className="w-7 h-7 bg-primary-700 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-white text-xs font-bold">IS</span>
              </div>
              <div className="bg-gray-50 border border-gray-100 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}

export default ChatArea;
