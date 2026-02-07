import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
    User,
    Mail,
    Lock,
    Eye,
    EyeOff,
    ArrowRight,
    Activity,
    Shield
} from 'lucide-react';
import './Register.css';

const Register = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        fullName: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [behaviorMetrics, setBehaviorMetrics] = useState({
        keystrokePattern: [],
        mouseMovements: 0,
        focusEvents: 0,
        idleTime: 0,
        typingSpeed: 0
    });
    const lastKeyTime = useRef(Date.now());
    const keystrokeTimes = useRef([]);
    const mouseRef = useRef(0);

    // Passive Behavioral Baseline Tracker
    useEffect(() => {
        const handleMouseMove = () => {
            mouseRef.current += 1;
            setBehaviorMetrics(prev => ({ ...prev, mouseMovements: mouseRef.current }));
        };

        const handleFocus = () => {
            setBehaviorMetrics(prev => ({ ...prev, focusEvents: prev.focusEvents + 1 }));
        };

        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('focus', handleFocus, true);

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('focus', handleFocus, true);
        };
    }, []);

    const handleKeyDown = () => {
        const now = Date.now();
        const interval = now - lastKeyTime.current;
        lastKeyTime.current = now;

        if (interval > 50 && interval < 2000) {
            keystrokeTimes.current.push(interval);
            const avgSpeed = keystrokeTimes.current.reduce((a, b) => a + b, 0) / keystrokeTimes.current.length;
            setBehaviorMetrics(prev => ({
                ...prev,
                typingSpeed: Math.round(60000 / avgSpeed),
                keystrokePattern: [...keystrokeTimes.current.slice(-10)]
            }));
        }
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // Store behavioral baseline with user data
        localStorage.setItem('userBehaviorBaseline', JSON.stringify(behaviorMetrics));
        localStorage.setItem('userData', JSON.stringify(formData));
        navigate('/kyc');
    };

    return (
        <div className="register-page">
            <div className="register-background">
                <div className="bg-gradient"></div>
                <div className="bg-orb bg-orb-1"></div>
                <div className="bg-orb bg-orb-2"></div>
            </div>

            <div className="register-container">
                <motion.div
                    className="register-card glass-card"
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <div className="register-header">
                        <div className="register-logo">
                            <Shield size={32} />
                        </div>
                        <h1>Create Account</h1>
                        <p>Start your secure identity verification journey</p>
                    </div>

                    <form onSubmit={handleSubmit} className="register-form">
                        <div className="form-group">
                            <label htmlFor="fullName">Full Name</label>
                            <div className="input-wrapper">
                                <User size={18} className="input-icon" />
                                <input
                                    type="text"
                                    id="fullName"
                                    name="fullName"
                                    className="input-field"
                                    placeholder="Enter your full name"
                                    value={formData.fullName}
                                    onChange={handleChange}
                                    onKeyDown={handleKeyDown}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="email">Email Address</label>
                            <div className="input-wrapper">
                                <Mail size={18} className="input-icon" />
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    className="input-field"
                                    placeholder="Enter your email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    onKeyDown={handleKeyDown}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <div className="input-wrapper">
                                <Lock size={18} className="input-icon" />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    id="password"
                                    name="password"
                                    className="input-field"
                                    placeholder="Create a password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    onKeyDown={handleKeyDown}
                                    required
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="confirmPassword">Confirm Password</label>
                            <div className="input-wrapper">
                                <Lock size={18} className="input-icon" />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    className="input-field"
                                    placeholder="Confirm your password"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    onKeyDown={handleKeyDown}
                                    required
                                />
                            </div>
                        </div>

                        <button type="submit" className="btn btn-primary w-full">
                            Continue to Verification
                            <ArrowRight size={18} />
                        </button>
                    </form>

                    <div className="register-footer">
                        <p>Already have an account? <Link to="/">Sign in</Link></p>
                    </div>
                </motion.div>

                {/* Behavioral Metrics Panel */}
                <motion.div
                    className="metrics-panel glass-card"
                    initial={{ opacity: 0, x: 30 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                >
                    <div className="metrics-header">
                        <Activity size={20} />
                        <h3>Passive Behavioral Baseline</h3>
                    </div>
                    <p className="metrics-desc">
                        We're analyzing your interaction patterns to create a unique behavioral fingerprint.
                    </p>

                    <div className="metrics-grid">
                        <div className="metric-item">
                            <span className="metric-value">{behaviorMetrics.typingSpeed || 0}</span>
                            <span className="metric-label">WPM Typing Speed</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-value">{behaviorMetrics.mouseMovements}</span>
                            <span className="metric-label">Mouse Events</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-value">{behaviorMetrics.focusEvents}</span>
                            <span className="metric-label">Focus Switches</span>
                        </div>
                        <div className="metric-item">
                            <span className="metric-value">{keystrokeTimes.current.length}</span>
                            <span className="metric-label">Keystrokes</span>
                        </div>
                    </div>

                    <div className="keystroke-visual">
                        <span className="visual-label">Keystroke Pattern</span>
                        <div className="keystroke-bars">
                            {behaviorMetrics.keystrokePattern.slice(-15).map((time, i) => (
                                <motion.div
                                    key={i}
                                    className="keystroke-bar"
                                    initial={{ height: 0 }}
                                    animate={{ height: `${Math.min(time / 5, 100)}%` }}
                                    style={{ opacity: 0.3 + (i / 15) * 0.7 }}
                                />
                            ))}
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default Register;
