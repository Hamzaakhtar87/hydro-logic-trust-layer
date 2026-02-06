import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Shield, DollarSign, FileCheck, LayoutDashboard, Menu, X } from 'lucide-react';
import { useState } from 'react';
import Dashboard from './pages/Dashboard';
import ShieldPage from './pages/Shield';
import FinOpsPage from './pages/FinOps';
import CompliancePage from './pages/Compliance';

function App() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const navItems = [
        { path: '/', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/shield', label: 'Shield', icon: Shield },
        { path: '/finops', label: 'FinOps', icon: DollarSign },
        { path: '/compliance', label: 'Compliance', icon: FileCheck },
    ];

    return (
        <Router>
            <div className="min-h-screen">
                {/* Header */}
                <header className="fixed top-0 left-0 right-0 z-50 bg-dark-950/80 backdrop-blur-lg border-b border-white/10">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="flex items-center justify-between h-16">
                            {/* Logo */}
                            <div className="flex items-center gap-3">
                                <div className="text-3xl">🌊</div>
                                <div>
                                    <h1 className="font-bold text-lg gradient-text">Hydro-Logic</h1>
                                    <p className="text-xs text-slate-400">Trust Layer</p>
                                </div>
                            </div>

                            {/* Desktop Navigation */}
                            <nav className="hidden md:flex items-center gap-1">
                                {navItems.map((item) => (
                                    <NavLink
                                        key={item.path}
                                        to={item.path}
                                        className={({ isActive }) =>
                                            `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${isActive
                                                ? 'bg-primary-600/20 text-primary-400 border border-primary-500/50'
                                                : 'text-slate-300 hover:text-white hover:bg-white/5'
                                            }`
                                        }
                                    >
                                        <item.icon className="w-4 h-4" />
                                        {item.label}
                                    </NavLink>
                                ))}
                            </nav>

                            {/* Mobile menu button */}
                            <button
                                className="md:hidden p-2 rounded-lg hover:bg-white/10"
                                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            >
                                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                            </button>
                        </div>
                    </div>

                    {/* Mobile Navigation */}
                    {mobileMenuOpen && (
                        <nav className="md:hidden border-t border-white/10 bg-dark-950/95 backdrop-blur-lg">
                            <div className="px-4 py-2 space-y-1">
                                {navItems.map((item) => (
                                    <NavLink
                                        key={item.path}
                                        to={item.path}
                                        onClick={() => setMobileMenuOpen(false)}
                                        className={({ isActive }) =>
                                            `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${isActive
                                                ? 'bg-primary-600/20 text-primary-400'
                                                : 'text-slate-300 hover:bg-white/5'
                                            }`
                                        }
                                    >
                                        <item.icon className="w-5 h-5" />
                                        {item.label}
                                    </NavLink>
                                ))}
                            </div>
                        </nav>
                    )}
                </header>

                {/* Main Content */}
                <main className="pt-20 pb-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/shield" element={<ShieldPage />} />
                        <Route path="/finops" element={<FinOpsPage />} />
                        <Route path="/compliance" element={<CompliancePage />} />
                    </Routes>
                </main>

                {/* Footer */}
                <footer className="border-t border-white/10 py-6 text-center text-slate-500 text-sm">
                    <p>🏆 Built for Gemini 3 Hackathon 2026 | Powered by Google Gemini API</p>
                </footer>
            </div>
        </Router>
    );
}

export default App;
