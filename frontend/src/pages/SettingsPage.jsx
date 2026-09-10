import { useAuth } from '../context/AuthContext';
import { logout as logoutService } from '../services/authService';

function SettingsPage() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logoutService();
    logout();
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-2xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold text-gray-900 mb-8">Settings</h1>

        {/* Account section */}
        <section className="mb-8">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Account</h2>
          <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
            <div className="flex items-center gap-4 p-5">
              {user?.profileImage ? (
                <img
                  src={user.profileImage}
                  alt={user.name}
                  className="w-14 h-14 rounded-full object-cover"
                />
              ) : (
                <div className="w-14 h-14 bg-primary-100 rounded-full flex items-center justify-center">
                  <span className="text-primary-700 font-bold text-xl">
                    {user?.name?.[0]?.toUpperCase() || '?'}
                  </span>
                </div>
              )}
              <div>
                <p className="font-semibold text-gray-900">{user?.name}</p>
                <p className="text-sm text-gray-500">{user?.email}</p>
                <p className="text-xs text-gray-400 mt-0.5">Signed in with Google</p>
              </div>
            </div>
          </div>
        </section>

        {/* Appearance section */}
        <section className="mb-8">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Appearance</h2>
          <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
            <div className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Theme</p>
                  <p className="text-xs text-gray-400 mt-0.5">Light theme is currently active</p>
                </div>
                <span className="text-xs text-gray-400 bg-gray-100 px-2.5 py-1 rounded-md">
                  Available in Phase 2
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* Danger zone */}
        <section>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Session</h2>
          <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
            <div className="p-5 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">Sign out</p>
                <p className="text-xs text-gray-400 mt-0.5">Sign out of your account on this device</p>
              </div>
              <button
                id="settings-logout-btn"
                onClick={handleLogout}
                className="text-sm font-medium text-red-600 border border-red-200 px-4 py-2 rounded-xl hover:bg-red-50 transition-colors cursor-pointer"
              >
                Sign out
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default SettingsPage;
