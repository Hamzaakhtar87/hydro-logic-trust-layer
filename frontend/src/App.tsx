import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useLocation } from 'react-router-dom';
import {
    LayoutDashboard,
    Shield,
    DollarSign,
    FileCheck,
    Settings as SettingsIcon,
    LogOut,
    Menu,
    X
} from 'lucide-react';

// Pages
import Dashboard from './pages/Dashboard';
import ShieldPage from './pages/Shield';
import FinOpsPage from './pages/FinOps';
import CompliancePage from './pages/Compliance';
import Login from './pages/Login';
import Signup from './pages/Signup';
import SettingsPage from './pages/Settings';

// Auth
import { isAuthenticated, authAPI } from './services/api';

// Protected Route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    if (!isAuthenticated()) {
        return <Navigate to="/login" replace />;
    }
    return <>{children}</>;
};

// Navigation items
const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/shield', label: 'Shield', icon: Shield },
    { path: '/finops', label: 'FinOps', icon: DollarSign },
    { path: '/compliance', label: 'Compliance', icon: FileCheck },
];

// Sidebar component
const Sidebar: React.FC = () => {
    const location = useLocation();
    const [mobileOpen, setMobileOpen] = React.useState(false);

    return (
        <>
            {/* Mobile menu button */}
            <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-slate-800 rounded-lg text-white"
            >
                {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>

            {/* Overlay */}
            {mobileOpen && (
                <div
                    className="lg:hidden fixed inset-0 bg-black/50 z-40"
                    onClick={() => setMobileOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside className={`
        fixed lg:static inset-y-0 left-0 z-40
        w-64 bg-slate-900 border-r border-slate-800
        transform ${mobileOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0
        transition-transform duration-200 ease-in-out
        flex flex-col
      `}>
                {/* Logo */}
                <div className="p-6 border-b border-slate-800">
                    <Link to="/dashboard" className="flex items-center gap-3 text-white">
                        <span className="text-3xl">🌊</span>
                        <div>
                            <span className="font-bold text-lg">Hydro-Logic</span>
                            <span className="block text-xs text-slate-400">Trust Layer</span>
                        </div>
                    </Link>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-4 space-y-1">
                    {navItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                onClick={() => setMobileOpen(false)}
                                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                  ${isActive
                                        ? 'bg-indigo-600 text-white'
                                        : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                                    }
                `}
                            >
                                <item.icon className="w-5 h-5" />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>

                {/* Bottom section */}
                <div className="p-4 border-t border-slate-800 space-y-1">
                    <Link
                        to="/settings"
                        onClick={() => setMobileOpen(false)}
                        className={`
              flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
              ${location.pathname === '/settings'
                                ? 'bg-indigo-600 text-white'
                                : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                            }
            `}
                    >
                        <SettingsIcon className="w-5 h-5" />
                        Settings
                    </Link>
                    <button
                        onClick={() => authAPI.logout()}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 hover:bg-red-500/20 hover:text-red-400 transition-colors"
                    >
                        <LogOut className="w-5 h-5" />
                        Logout
                    </button>
                </div>
            </aside>
        </>
    );
};

// Main layout with sidebar
const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex">
            <Sidebar />
            <main className="flex-1 p-6 lg:p-8 overflow-auto">
                <div className="max-w-7xl mx-auto">
                    {children}
                </div>
            </main>
        </div>
    );
};

// App component
function App() {
    return (
        <Router>
            <Routes>
                {/* Public routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />

                {/* Redirect root based on auth status */}
                <Route
                    path="/"
                    element={
                        isAuthenticated()
                            ? <Navigate to="/dashboard" replace />
                            : <Navigate to="/login" replace />
                    }
                />

                {/* Protected routes */}
                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>
                            <AppLayout>
                                <Dashboard />
                            </AppLayout>
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/shield"
                    element={
                        <ProtectedRoute>
                            <AppLayout>
                                <ShieldPage />
                            </AppLayout>
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/finops"
                    element={
                        <ProtectedRoute>
                            <AppLayout>
                                <FinOpsPage />
                            </AppLayout>
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/compliance"
                    element={
                        <ProtectedRoute>
                            <AppLayout>
                                <CompliancePage />
                            </AppLayout>
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/settings"
                    element={
                        <ProtectedRoute>
                            <AppLayout>
                                <SettingsPage />
                            </AppLayout>
                        </ProtectedRoute>
                    }
                />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </Router>
    );
}

export default App;
