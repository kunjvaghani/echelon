import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
    CheckCircle,
    XCircle,
    AlertTriangle,
    Shield,
    FileText,
    User,
    Activity,
    ArrowRight,
    RefreshCcw,
    Download
} from 'lucide-react';
import {
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    ResponsiveContainer
} from 'recharts';
import './Dashboard.css';

const Dashboard = () => {
    const [decision, setDecision] = useState(null);
    const [riskScores, setRiskScores] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Simulate decision engine result
        setTimeout(() => {
            const decisions = ['approved', 'approved', 'approved', 'manual_review', 'reject'];
            const randomDecision = decisions[Math.floor(Math.random() * decisions.length)];

            setDecision(randomDecision);
            setRiskScores({
                forgery: Math.random() * 0.3,
                mismatch: Math.random() * 0.25,
                anomaly: Math.random() * 0.35,
                velocity: Math.random() * 0.2,
                behavioral: Math.random() * 0.3
            });
            setLoading(false);
        }, 1500);
    }, []);

    const radarData = riskScores ? [
        { category: 'Forgery', score: riskScores.forgery * 100, fullMark: 100 },
        { category: 'Mismatch', score: riskScores.mismatch * 100, fullMark: 100 },
        { category: 'Anomaly', score: riskScores.anomaly * 100, fullMark: 100 },
        { category: 'Velocity', score: riskScores.velocity * 100, fullMark: 100 },
        { category: 'Behavioral', score: riskScores.behavioral * 100, fullMark: 100 }
    ] : [];

    const overallScore = riskScores
        ? (Object.values(riskScores).reduce((a, b) => a + b, 0) / 5) * 100
        : 0;

    const getDecisionConfig = () => {
        switch (decision) {
            case 'approved':
                return {
                    icon: CheckCircle,
                    title: 'Verification Approved',
                    subtitle: 'Identity successfully verified',
                    color: 'success',
                    message: 'The identity verification has passed all checks. The user can proceed with full account access.'
                };
            case 'reject':
                return {
                    icon: XCircle,
                    title: 'Verification Rejected',
                    subtitle: 'High risk detected',
                    color: 'danger',
                    message: 'Multiple fraud indicators detected. Manual review by security team is recommended.'
                };
            case 'manual_review':
                return {
                    icon: AlertTriangle,
                    title: 'Manual Review Required',
                    subtitle: 'Needs additional verification',
                    color: 'warning',
                    message: 'Some risk factors require human review. Please wait for a security analyst to review.'
                };
            default:
                return null;
        }
    };

    const decisionConfig = getDecisionConfig();

    const verificationDetails = [
        { label: 'Document Type', value: 'Government ID', icon: FileText },
        { label: 'Face Match', value: '98.5%', icon: User },
        { label: 'Liveness Score', value: '99.2%', icon: Activity },
        { label: 'Processing Time', value: '2.3s', icon: RefreshCcw }
    ];

    if (loading) {
        return (
            <div className="dashboard-page">
                <div className="loading-container">
                    <motion.div
                        className="loading-shield"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    >
                        <Shield size={64} />
                    </motion.div>
                    <h2>Processing Decision...</h2>
                    <p>Analyzing verification results</p>
                </div>
            </div>
        );
    }

    return (
        <div className="dashboard-page">
            <div className="dashboard-container">
                <div className="dashboard-header">
                    <h1>Verification Complete</h1>
                    <p>Identity verification decision and risk analysis</p>
                </div>

                <div className="dashboard-grid">
                    {/* Decision Card */}
                    <motion.div
                        className={`decision-card glass-card ${decisionConfig.color}`}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                    >
                        <div className={`decision-icon ${decisionConfig.color}`}>
                            <decisionConfig.icon size={48} />
                        </div>
                        <h2>{decisionConfig.title}</h2>
                        <p className="decision-subtitle">{decisionConfig.subtitle}</p>
                        <p className="decision-message">{decisionConfig.message}</p>

                        <div className="decision-actions">
                            <Link to="/kyc" className="btn btn-secondary">
                                <RefreshCcw size={18} />
                                New Verification
                            </Link>
                            <button className="btn btn-ghost">
                                <Download size={18} />
                                Download Report
                            </button>
                        </div>
                    </motion.div>

                    {/* Risk Radar Chart */}
                    <motion.div
                        className="radar-card glass-card"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <h3>Risk Score Analysis</h3>
                        <div className="radar-chart-container">
                            <ResponsiveContainer width="100%" height={280}>
                                <RadarChart data={radarData}>
                                    <PolarGrid stroke="rgba(255,255,255,0.1)" />
                                    <PolarAngleAxis
                                        dataKey="category"
                                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                                    />
                                    <PolarRadiusAxis
                                        angle={30}
                                        domain={[0, 100]}
                                        tick={{ fill: '#64748b', fontSize: 10 }}
                                    />
                                    <Radar
                                        name="Risk"
                                        dataKey="score"
                                        stroke="#00d4ff"
                                        fill="#00d4ff"
                                        fillOpacity={0.3}
                                        strokeWidth={2}
                                    />
                                </RadarChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="overall-score">
                            <span className="score-label">Overall Risk Score</span>
                            <span className={`score-value ${overallScore < 30 ? 'low' : overallScore < 60 ? 'medium' : 'high'}`}>
                                {overallScore.toFixed(1)}%
                            </span>
                        </div>
                    </motion.div>
                </div>

                {/* Verification Details */}
                <motion.div
                    className="details-section"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                >
                    <h3>Verification Details</h3>
                    <div className="details-grid">
                        {verificationDetails.map((detail, index) => (
                            <div key={index} className="detail-card glass-card">
                                <div className="detail-icon">
                                    <detail.icon size={20} />
                                </div>
                                <div className="detail-info">
                                    <span className="detail-label">{detail.label}</span>
                                    <span className="detail-value">{detail.value}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </motion.div>

                {/* Risk Breakdown */}
                <motion.div
                    className="breakdown-section glass-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                >
                    <h3>Risk Factor Breakdown</h3>
                    <div className="breakdown-list">
                        {radarData.map((item, index) => (
                            <div key={index} className="breakdown-item">
                                <div className="breakdown-header">
                                    <span className="breakdown-label">{item.category}</span>
                                    <span className={`breakdown-value ${item.score < 30 ? 'low' : item.score < 60 ? 'medium' : 'high'}`}>
                                        {item.score.toFixed(1)}%
                                    </span>
                                </div>
                                <div className="progress-bar">
                                    <motion.div
                                        className={`progress-bar-fill ${item.score < 30 ? 'low' : item.score < 60 ? 'medium' : 'high'}`}
                                        initial={{ width: 0 }}
                                        animate={{ width: `${item.score}%` }}
                                        transition={{ delay: 0.5 + index * 0.1 }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </motion.div>

                {/* CTA */}
                <div className="dashboard-cta">
                    <Link to="/admin" className="btn btn-primary">
                        View Analytics Dashboard
                        <ArrowRight size={18} />
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
