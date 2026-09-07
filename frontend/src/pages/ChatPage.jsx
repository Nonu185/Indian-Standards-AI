import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/layout/Sidebar';
import ChatArea from '../components/chat/ChatArea';
import MessageInput from '../components/chat/MessageInput';
import { getChats, createChat, deleteChat } from '../services/chatService';
import { getMessages, sendMessage } from '../services/messageService';

function ChatPage() {
  const navigate = useNavigate();

  // Sidebar state
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  // Message state
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch all user chats on mount
  useEffect(() => {
    const fetchChats = async () => {
      try {
        const data = await getChats();
        setChats(data);
        // Auto-open the most recent chat if available
        if (data.length > 0) {
          setActiveChatId(data[0]._id);
        }
      } catch {
        setError('Failed to load chats. Please refresh.');
      }
    };
    fetchChats();
  }, []);

  // Fetch messages whenever the active chat changes
  useEffect(() => {
    if (!activeChatId) {
      setMessages([]);
      return;
    }
    const fetchMessages = async () => {
      try {
        const data = await getMessages(activeChatId);
        setMessages(data);
      } catch {
        setError('Failed to load messages.');
      }
    };
    fetchMessages();
  }, [activeChatId]);

  // Create a new chat and switch to it
  const handleNewChat = async () => {
    try {
      const newChat = await createChat('New Chat');
      setChats((prev) => [newChat, ...prev]);
      setActiveChatId(newChat._id);
      setMessages([]);
      setError(null);
    } catch {
      setError('Failed to create a new chat.');
    }
  };

  // Switch to a different chat
  const handleSelectChat = (chatId) => {
    setActiveChatId(chatId);
    setError(null);
  };

  // Delete a chat
  const handleDeleteChat = async (chatId) => {
    try {
      await deleteChat(chatId);
      setChats((prev) => prev.filter((c) => c._id !== chatId));
      if (activeChatId === chatId) {
        // Switch to the next available chat or clear
        const remaining = chats.filter((c) => c._id !== chatId);
        setActiveChatId(remaining.length > 0 ? remaining[0]._id : null);
        setMessages([]);
      }
    } catch {
      setError('Failed to delete chat.');
    }
  };

  // Send a message
  const handleSendMessage = async (content) => {
    if (!activeChatId) {
      // No active chat — create one first
      try {
        const newChat = await createChat('New Chat');
        setChats((prev) => [newChat, ...prev]);
        setActiveChatId(newChat._id);
        await sendMessageToChat(newChat._id, content);
      } catch {
        setError('Failed to create chat and send message.');
      }
      return;
    }
    await sendMessageToChat(activeChatId, content);
  };

  const sendMessageToChat = async (chatId, content) => {
    // Optimistically add user message to UI
    const tempUserMessage = {
      tempId: `temp-user-${Date.now()}`,
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);
    setLoading(true);
    setError(null);

    try {
      const data = await sendMessage(chatId, content);
      setMessages((prev) => {
        const filtered = prev.filter(
          (m) =>
            m.tempId !== tempUserMessage.tempId &&
            m._id !== data.userMessage._id &&
            m._id !== data.assistantMessage._id
        );
        return [...filtered, data.userMessage, data.assistantMessage];
      });

      // Update chat title in sidebar if it changed
      setChats((prev) =>
        prev.map((c) => {
          if (c._id === chatId) {
            const updatedTitle = data.chat?.title || (c.title === 'New Chat' ? content.slice(0, 50) : c.title);
            return { ...c, title: updatedTitle, updatedAt: new Date().toISOString() };
          }
          return c;
        })
      );
    } catch {
      // Remove optimistic message on failure
      setMessages((prev) => prev.filter((m) => m.tempId !== tempUserMessage.tempId));
      setError('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
        isMobileOpen={isMobileSidebarOpen}
        onMobileClose={() => setIsMobileSidebarOpen(false)}
      />

      {/* Main chat area */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Top bar (mobile only) */}
        <div className="md:hidden flex items-center gap-3 px-4 py-3 border-b border-gray-100">
          <button
            id="mobile-menu-btn"
            onClick={() => setIsMobileSidebarOpen(true)}
            className="p-1.5 text-gray-500 hover:text-gray-700 cursor-pointer"
            aria-label="Open menu"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <span className="text-sm font-semibold text-gray-800">Indian Standards AI</span>
        </div>

        {/* Error banner */}
        {error && (
          <div className="mx-4 mt-3 bg-red-50 border border-red-200 rounded-xl px-4 py-3 flex items-center justify-between">
            <p className="text-sm text-red-700">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-600 ml-3 cursor-pointer"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Messages */}
        <ChatArea
          messages={messages}
          loading={loading}
        />

        {/* Input */}
        <MessageInput onSend={handleSendMessage} disabled={loading} />
      </div>
    </div>
  );
}

export default ChatPage;
