import { motion } from 'framer-motion';
import {
    Shield,
    FileWarning,
    ScanFace,
    Bot,
    ArrowRight,
    CheckCircle2,
    Fingerprint,
    Brain,
    Lock,
    Zap
} from 'lucide-react';
import { Link } from 'react-router-dom';
import './Landing.css';

const Landing = () => {
    const threatVectors = [
        {
            icon: FileWarning,
            title: 'Forged Documents',
            subtitle: 'ELA + EfficientNet Detection',
            description: 'Advanced Error Level Analysis combined with deep learning to detect manipulated identity documents.',
            features: ['Pixel-level tampering detection', 'Font inconsistency analysis', 'Metadata verification'],
            color: '#ef4444'
        },
        {
            icon: ScanFace,
            title: 'Deepfake Biometrics',
            subtitle: 'MTCNN + DeepFace Analysis',
            description: 'Real-time face detection and liveness verification to prevent spoofing attacks.',
            features: ['3D depth estimation', 'Micro-expression analysis', 'Texture authenticity check'],
            color: '#8b5cf6'
        },
        {
            icon: Bot,
            title: 'Bot Behavioral Analysis',
            subtitle: 'Keystroke Dynamics',
            description: 'Passive behavioral biometrics to detect automated fraud attempts and synthetic identities.',
            features: ['Typing pattern analysis', 'Mouse movement tracking', 'Session behavior profiling'],
            color: '#00d4ff'
        }
    ];

    const features = [
        { icon: Fingerprint, title: 'Biometric Fusion', desc: 'Multi-modal identity verification' },
        { icon: Brain, title: 'AI-Powered', desc: 'Machine learning fraud detection' },
        { icon: Lock, title: 'Secure Pipeline', desc: 'End-to-end encrypted processing' },
        { icon: Zap, title: 'Real-time', desc: 'Instant verification decisions' }
    ];

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.2 }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 30 },
        visible: { opacity: 1, y: 0 }
    };

    return (
        <div className="landing-page">
            {/* Hero Section */}
            <section className="hero-section">
                <div className="hero-background">
                    <div className="hero-gradient"></div>
                    <div className="hero-grid"></div>
                    <div className="hero-orb hero-orb-1"></div>
                    <div className="hero-orb hero-orb-2"></div>
                </div>

                <div className="container">
                    <motion.div
                        className="hero-content"
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                    >
                        <motion.div
                            className="hero-badge"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: 0.3, type: 'spring' }}
                        >
                            <Shield size={16} />
                            <span>Enterprise-Grade Security</span>
                        </motion.div>

                        <h1 className="hero-title">
                            Preventing{' '}
                            <span className="gradient-text">Synthetic Identity Fraud</span>
                            <br />with Multi-Layered AI
                        </h1>

                        <p className="hero-subtitle">
                            Advanced e-KYC pipeline that correlates biometric, document, and behavioral
                            signals to detect sophisticated fraud attempts in real-time.
                        </p>

                        <div className="hero-actions">
                            <Link to="/kyc" className="btn btn-primary btn-lg">
                                Start Verification
                                <ArrowRight size={20} />
                            </Link>
                            <Link to="/register" className="btn btn-secondary btn-lg">
                                Create Account
                            </Link>
                        </div>

                        <div className="hero-stats">
                            <div className="stat-item">
                                <span className="stat-value">99.7%</span>
                                <span className="stat-label">Detection Rate</span>
                            </div>
                            <div className="stat-divider"></div>
                            <div className="stat-item">
                                <span className="stat-value">&lt;2s</span>
                                <span className="stat-label">Verification Time</span>
                            </div>
                            <div className="stat-divider"></div>
                            <div className="stat-item">
                                <span className="stat-value">0.1%</span>
                                <span className="stat-label">False Positive Rate</span>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Threat Vectors Section */}
            <section className="threat-section section">
                <div className="container">
                    <motion.div
                        className="section-header"
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                    >
                        <span className="section-tag">Threat Detection</span>
                        <h2>Multi-Vector Fraud Prevention</h2>
                        <p>Our AI analyzes multiple attack vectors simultaneously to detect synthetic identity fraud.</p>
                    </motion.div>

                    <motion.div
                        className="threat-grid"
                        variants={containerVariants}
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true }}
                    >
                        {threatVectors.map((threat, index) => (
                            <motion.div
                                key={index}
                                className="threat-card glass-card"
                                variants={itemVariants}
                                whileHover={{ y: -8 }}
                            >
                                <div
                                    className="threat-icon"
                                    style={{ '--accent-color': threat.color }}
                                >
                                    <threat.icon size={32} />
                                </div>
                                <h3>{threat.title}</h3>
                                <span className="threat-subtitle">{threat.subtitle}</span>
                                <p>{threat.description}</p>
                                <ul className="threat-features">
                                    {threat.features.map((feature, i) => (
                                        <li key={i}>
                                            <CheckCircle2 size={14} />
                                            {feature}
                                        </li>
                                    ))}
                                </ul>
                            </motion.div>
                        ))}
                    </motion.div>
                </div>
            </section>

            {/* Features Section */}
            <section className="features-section section">
                <div className="container">
                    <motion.div
                        className="features-grid"
                        variants={containerVariants}
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true }}
                    >
                        {features.map((feature, index) => (
                            <motion.div
                                key={index}
                                className="feature-card"
                                variants={itemVariants}
                            >
                                <div className="feature-icon">
                                    <feature.icon size={24} />
                                </div>
                                <h4>{feature.title}</h4>
                                <p>{feature.desc}</p>
                            </motion.div>
                        ))}
                    </motion.div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta-section section">
                <div className="container">
                    <motion.div
                        className="cta-card glass-card"
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                    >
                        <div className="cta-content">
                            <h2>Ready to Secure Your Verification Pipeline?</h2>
                            <p>Get started with SecureVerify AI and protect your platform from synthetic identity fraud.</p>
                            <div className="cta-actions">
                                <Link to="/kyc" className="btn btn-primary btn-lg">
                                    Try Demo
                                    <ArrowRight size={20} />
                                </Link>
                                <Link to="/admin" className="btn btn-ghost btn-lg">
                                    View Analytics
                                </Link>
                            </div>
                        </div>
                        <div className="cta-visual">
                            <div className="cta-shield">
                                <Shield size={80} />
                            </div>
                        </div>
                    </motion.div>
                </div>
            </section>
        </div>
    );
};

export default Landing;
