import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Menu, X, ChevronRight, User, LogOut, ChevronDown } from 'lucide-react';
import './Navbar.css';

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [userMenuOpen, setUserMenuOpen] = useState(false);
    const [user, setUser] = useState(null);
    const location = useLocation();
    const navigate = useNavigate();

    // Check for logged in user on mount and location change
    useEffect(() => {
        const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        if (isLoggedIn) {
            const userData = localStorage.getItem('user');
            if (userData) {
                try {
                    setUser(JSON.parse(userData));
                } catch {
                    setUser(null);
                }
            }
        } else {
            setUser(null);
        }
    }, [location]);

    const handleLogout = () => {
        localStorage.removeItem('user');
        localStorage.removeItem('isLoggedIn');
        setUser(null);
        setUserMenuOpen(false);
        navigate('/');
    };

    const navLinks = [
        { path: '/', label: 'Home' },
        { path: '/kyc', label: 'KYC Pipeline' },
        { path: '/dashboard', label: 'Dashboard' },
        { path: '/admin', label: 'Analytics' },
    ];

    const isActive = (path) => location.pathname === path;

    return (
        <motion.nav
            className="navbar"
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
        >
            <div className="navbar-container">
                <Link to="/" className="navbar-logo">
                    <div className="logo-icon">
                        <Shield size={28} />
                    </div>
                    <span className="logo-text">
                        Secure<span className="gradient-text">Verify</span> AI
                    </span>
                </Link>

                <div className="navbar-links">
                    {navLinks.map((link) => (
                        <Link
                            key={link.path}
                            to={link.path}
                            className={`nav-link ${isActive(link.path) ? 'active' : ''}`}
                        >
                            {link.label}
                            {isActive(link.path) && (
                                <motion.div
                                    className="nav-link-indicator"
                                    layoutId="activeIndicator"
                                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                                />
                            )}
                        </Link>
                    ))}
                </div>

                <div className="navbar-actions">
                    {user ? (
                        <div className="user-menu-container">
                            <button
                                className="user-menu-btn"
                                onClick={() => setUserMenuOpen(!userMenuOpen)}
                            >
                                <div className="user-avatar">
                                    <User size={18} />
                                </div>
                                <span className="user-name">{user.full_name || user.email?.split('@')[0] || 'User'}</span>
                                <ChevronDown size={16} className={`chevron ${userMenuOpen ? 'open' : ''}`} />
                            </button>

                            <AnimatePresence>
                                {userMenuOpen && (
                                    <motion.div
                                        className="user-dropdown"
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -10 }}
                                        transition={{ duration: 0.2 }}
                                    >
                                        <div className="dropdown-header">
                                            <p className="dropdown-email">{user.email}</p>
                                        </div>
                                        <div className="dropdown-divider"></div>
                                        <Link
                                            to="/kyc"
                                            className="dropdown-item"
                                            onClick={() => setUserMenuOpen(false)}
                                        >
                                            <Shield size={16} />
                                            Start KYC
                                        </Link>
                                        <button
                                            className="dropdown-item logout"
                                            onClick={handleLogout}
                                        >
                                            <LogOut size={16} />
                                            Logout
                                        </button>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    ) : (
                        <>
                            <Link to="/login" className="btn btn-ghost btn-sm">
                                Login
                            </Link>
                            <Link to="/register" className="btn btn-primary btn-sm">
                                Register
                                <ChevronRight size={16} />
                            </Link>
                        </>
                    )}
                </div>

                <button
                    className="mobile-menu-btn"
                    onClick={() => setIsOpen(!isOpen)}
                    aria-label="Toggle menu"
                >
                    {isOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        className="mobile-menu"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        {navLinks.map((link, index) => (
                            <motion.div
                                key={link.path}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.1 }}
                            >
                                <Link
                                    to={link.path}
                                    className={`mobile-nav-link ${isActive(link.path) ? 'active' : ''}`}
                                    onClick={() => setIsOpen(false)}
                                >
                                    {link.label}
                                </Link>
                            </motion.div>
                        ))}

                        {user ? (
                            <div className="mobile-user-section">
                                <div className="mobile-user-info">
                                    <User size={20} />
                                    <span>{user.full_name || user.email}</span>
                                </div>
                                <button
                                    className="btn btn-ghost w-full"
                                    onClick={() => { handleLogout(); setIsOpen(false); }}
                                >
                                    <LogOut size={16} />
                                    Logout
                                </button>
                            </div>
                        ) : (
                            <>
                                <Link
                                    to="/login"
                                    className="btn btn-ghost w-full mt-md"
                                    onClick={() => setIsOpen(false)}
                                >
                                    Login
                                </Link>
                                <Link
                                    to="/register"
                                    className="btn btn-primary w-full"
                                    onClick={() => setIsOpen(false)}
                                >
                                    Register
                                </Link>
                            </>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.nav>
    );
};

export default Navbar;
