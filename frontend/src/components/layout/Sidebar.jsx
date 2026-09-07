import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { logout as logoutService } from '../../services/authService';

function Sidebar({
  chats,
  activeChatId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  isMobileOpen,
  onMobileClose,
}) {
  const { user, logout } = useAuth();
  const [deletingId, setDeletingId] = useState(null);
  const [showProfile, setShowProfile] = useState(false);

  const handleLogout = async () => {
    try {
      await logoutService();
      logout();
    } catch {
      // Force logout even if API call fails
      logout();
    }
  };

  const handleDelete = async (e, chatId) => {
    e.stopPropagation();
    if (!window.confirm('Delete this chat?')) return;
    setDeletingId(chatId);
    await onDeleteChat(chatId);
    setDeletingId(null);
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-white border-r border-gray-100">
      {/* Logo */}
      <div className="px-4 py-4 border-b border-gray-100">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-primary-700 rounded-lg flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-bold">IS</span>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900 leading-tight">Indian Standards AI</p>
            <p className="text-xs text-gray-400">Procurement Assistant</p>
          </div>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="px-3 pt-3 pb-2">
        <button
          id="new-chat-btn"
          onClick={() => { onNewChat(); onMobileClose?.(); }}
          className="w-full flex items-center gap-2 px-3 py-2.5 bg-primary-600 text-white text-sm font-medium rounded-xl hover:bg-primary-700 transition-colors duration-150 cursor-pointer"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          New Chat
        </button>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto px-3 py-1">
        {chats.length === 0 ? (
          <p className="text-xs text-gray-400 px-2 py-4 text-center">No chats yet</p>
        ) : (
          <div className="space-y-0.5">
            <p className="text-xs font-medium text-gray-400 px-2 py-2 uppercase tracking-wide">
              Recent Chats
            </p>
            {chats.map((chat) => (
              <div
                key={chat._id}
                onClick={() => { onSelectChat(chat._id); onMobileClose?.(); }}
                className={`group flex items-center gap-2 px-3 py-2.5 rounded-xl cursor-pointer transition-colors duration-100 ${
                  activeChatId === chat._id
                    ? 'bg-primary-50 text-primary-800'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <svg className="w-4 h-4 flex-shrink-0 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span className="text-xs truncate flex-1">{chat.title}</span>
                {deletingId !== chat._id && (
                  <button
                    onClick={(e) => handleDelete(e, chat._id)}
                    className="opacity-0 group-hover:opacity-100 p-0.5 text-gray-400 hover:text-red-500 transition-all cursor-pointer"
                    title="Delete chat"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                )}
                {deletingId === chat._id && (
                  <div className="w-3.5 h-3.5 border border-gray-300 border-t-transparent rounded-full animate-spin" />
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Bottom — User Profile & Logout */}
      <div className="border-t border-gray-100 p-3 space-y-1">
        {/* Profile */}
        <button
          id="profile-btn"
          onClick={() => setShowProfile(!showProfile)}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-gray-50 transition-colors cursor-pointer text-left"
        >
          {user?.profileImage ? (
            <img
              src={user.profileImage}
              alt={user.name}
              className="w-7 h-7 rounded-full object-cover flex-shrink-0"
            />
          ) : (
            <div className="w-7 h-7 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-primary-700 text-xs font-semibold">
                {user?.name?.[0]?.toUpperCase() || '?'}
              </span>
            </div>
          )}
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium text-gray-800 truncate">{user?.name}</p>
            <p className="text-xs text-gray-400 truncate">{user?.email}</p>
          </div>
        </button>

        {/* Logout */}
        <button
          id="logout-btn"
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2 text-xs text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-xl transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Sign out
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden md:flex w-64 flex-shrink-0 h-full">{sidebarContent}</div>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div className="md:hidden fixed inset-0 z-40">
          <div
            className="absolute inset-0 bg-black/30"
            onClick={onMobileClose}
          />
          <div className="absolute left-0 top-0 h-full w-72 shadow-xl">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
}

export default Sidebar;
