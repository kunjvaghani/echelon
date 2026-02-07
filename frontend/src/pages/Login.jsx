import { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
    Mail,
    ArrowRight,
    Shield,
    Loader2,
    KeyRound,
    CheckCircle,
    AlertCircle
} from 'lucide-react';
import { sendLoginOtp, verifyLoginOtp } from '../api/kycApi';
import './Login.css';

const Login = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState('email'); // 'email' or 'otp'
    const [email, setEmail] = useState('');
    const [otp, setOtp] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSendOtp = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            const result = await sendLoginOtp(email);
            if (result.success) {
                setSuccess(result.message || 'OTP sent to your email!');
                setStep('otp');
            } else {
                setError(result.message || 'Failed to send OTP');
            }
        } catch (err) {
            setError(err.message || 'Failed to send OTP. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyOtp = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            const result = await verifyLoginOtp(email, otp);
            if (result.success) {
                setSuccess('Login successful!');
                // Store user data in localStorage
                localStorage.setItem('user', JSON.stringify(result.user));
                localStorage.setItem('isLoggedIn', 'true');
                // Redirect to home page after short delay
                setTimeout(() => navigate('/'), 1000);
            } else {
                setError(result.message || 'Invalid OTP');
            }
        } catch (err) {
            setError(err.message || 'Verification failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleResendOtp = async () => {
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            const result = await sendLoginOtp(email);
            if (result.success) {
                setSuccess('OTP resent to your email!');
            } else {
                setError(result.message || 'Failed to resend OTP');
            }
        } catch (err) {
            setError(err.message || 'Failed to resend OTP');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-background">
                <div className="bg-gradient"></div>
                <div className="bg-orb bg-orb-1"></div>
                <div className="bg-orb bg-orb-2"></div>
            </div>

            <div className="login-container">
                <motion.div
                    className="login-card glass-card"
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <div className="login-header">
                        <div className="login-logo">
                            <Shield size={32} />
                        </div>
                        <h1>Welcome Back</h1>
                        <p>Sign in with your registered email</p>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <motion.div
                            className="alert alert-error"
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <AlertCircle size={18} />
                            <span>{error}</span>
                        </motion.div>
                    )}

                    {/* Success Message */}
                    {success && (
                        <motion.div
                            className="alert alert-success"
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <CheckCircle size={18} />
                            <span>{success}</span>
                        </motion.div>
                    )}

                    {step === 'email' ? (
                        <form onSubmit={handleSendOtp} className="login-form">
                            <div className="form-group">
                                <label htmlFor="email">Email Address</label>
                                <div className="input-wrapper">
                                    <Mail size={18} className="input-icon" />
                                    <input
                                        type="email"
                                        id="email"
                                        className="input-field"
                                        placeholder="Enter your registered email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        disabled={loading}
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                className="btn btn-primary w-full"
                                disabled={loading || !email}
                            >
                                {loading ? (
                                    <>
                                        <Loader2 size={18} className="spin" />
                                        Sending OTP...
                                    </>
                                ) : (
                                    <>
                                        Send OTP
                                        <ArrowRight size={18} />
                                    </>
                                )}
                            </button>
                        </form>
                    ) : (
                        <form onSubmit={handleVerifyOtp} className="login-form">
                            <div className="otp-info">
                                <p>We've sent a verification code to:</p>
                                <strong>{email}</strong>
                            </div>

                            <div className="form-group">
                                <label htmlFor="otp">Enter OTP</label>
                                <div className="input-wrapper">
                                    <KeyRound size={18} className="input-icon" />
                                    <input
                                        type="text"
                                        id="otp"
                                        className="input-field otp-input"
                                        placeholder="Enter 6-digit OTP"
                                        value={otp}
                                        onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                        maxLength={6}
                                        required
                                        disabled={loading}
                                        autoFocus
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                className="btn btn-primary w-full"
                                disabled={loading || otp.length < 6}
                            >
                                {loading ? (
                                    <>
                                        <Loader2 size={18} className="spin" />
                                        Verifying...
                                    </>
                                ) : (
                                    <>
                                        Verify & Login
                                        <ArrowRight size={18} />
                                    </>
                                )}
                            </button>

                            <div className="otp-actions">
                                <button
                                    type="button"
                                    className="btn btn-ghost"
                                    onClick={handleResendOtp}
                                    disabled={loading}
                                >
                                    Resend OTP
                                </button>
                                <button
                                    type="button"
                                    className="btn btn-ghost"
                                    onClick={() => {
                                        setStep('email');
                                        setOtp('');
                                        setError('');
                                        setSuccess('');
                                    }}
                                >
                                    Change Email
                                </button>
                            </div>
                        </form>
                    )}

                    <div className="login-footer">
                        <p>Don't have an account? <Link to="/register">Register here</Link></p>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default Login;
