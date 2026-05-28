import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    TrendingUp,
    TrendingDown,
    Users,
    Shield,
    AlertTriangle,
    CheckCircle,
    XCircle,
    Clock,
    Target,
    Activity,
    PieChart as PieChartIcon
} from 'lucide-react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell
} from 'recharts';
import './Admin.css';

const Admin = () => {
    const [timeRange, setTimeRange] = useState('7d');

    const stats = [
        {
            label: 'Total Verifications',
            value: '12,847',
            change: '+12.5%',
            trend: 'up',
            icon: Users,
            color: '#00d4ff'
        },
        {
            label: 'Fraud Detected',
            value: '342',
            change: '-8.2%',
            trend: 'down',
            icon: AlertTriangle,
            color: '#ef4444'
        },
        {
            label: 'Approval Rate',
            value: '94.2%',
            change: '+2.1%',
            trend: 'up',
            icon: CheckCircle,
            color: '#10b981'
        },
        {
            label: 'Avg. Processing',
            value: '1.8s',
            change: '-0.3s',
            trend: 'down',
            icon: Clock,
            color: '#8b5cf6'
        }
    ];

    const performanceData = [
        { name: 'Mon', precision: 97.2, recall: 94.5, f1: 95.8 },
        { name: 'Tue', precision: 96.8, recall: 95.1, f1: 95.9 },
        { name: 'Wed', precision: 97.5, recall: 94.8, f1: 96.1 },
        { name: 'Thu', precision: 98.1, recall: 95.2, f1: 96.6 },
        { name: 'Fri', precision: 97.8, recall: 95.8, f1: 96.8 },
        { name: 'Sat', precision: 98.2, recall: 96.1, f1: 97.1 },
        { name: 'Sun', precision: 98.5, recall: 96.5, f1: 97.5 }
    ];

    const fraudDetectionData = [
        { name: 'Week 1', detected: 45, missed: 2 },
        { name: 'Week 2', detected: 52, missed: 1 },
        { name: 'Week 3', detected: 48, missed: 3 },
        { name: 'Week 4', detected: 61, missed: 1 }
    ];

    const threatDistribution = [
        { name: 'Document Forgery', value: 35, color: '#ef4444' },
        { name: 'Deepfake Attack', value: 25, color: '#8b5cf6' },
        { name: 'Bot Activity', value: 20, color: '#00d4ff' },
        { name: 'Identity Mismatch', value: 15, color: '#f59e0b' },
        { name: 'Other', value: 5, color: '#64748b' }
    ];

    const verificationTrend = [
        { date: 'Jan', verifications: 8500, approved: 8100, rejected: 400 },
        { date: 'Feb', verifications: 9200, approved: 8700, rejected: 500 },
        { date: 'Mar', verifications: 10100, approved: 9500, rejected: 600 },
        { date: 'Apr', verifications: 11300, approved: 10700, rejected: 600 },
        { date: 'May', verifications: 12000, approved: 11300, rejected: 700 },
        { date: 'Jun', verifications: 12847, approved: 12100, rejected: 747 }
    ];

    const modelMetrics = [
        { name: 'Precision', value: 98.5, target: 99 },
        { name: 'Recall', value: 96.5, target: 98 },
        { name: 'F1 Score', value: 97.5, target: 98 },
        { name: 'AUC-ROC', value: 99.2, target: 99 }
    ];

    return (
        <div className="admin-page">
            <div className="admin-container">
                <div className="admin-header">
                    <div>
                        <h1>Analytics Dashboard</h1>
                        <p>Monitor fraud detection performance and verification metrics</p>
                    </div>
                    <div className="time-filter">
                        {['24h', '7d', '30d', '90d'].map((range) => (
                            <button
                                key={range}
                                className={`filter-btn ${timeRange === range ? 'active' : ''}`}
                                onClick={() => setTimeRange(range)}
                            >
                                {range}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Stats Grid */}
                <div className="stats-grid">
                    {stats.map((stat, index) => (
                        <motion.div
                            key={index}
                            className="stat-card glass-card"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                        >
                            <div className="stat-icon" style={{ background: `${stat.color}20`, color: stat.color }}>
                                <stat.icon size={24} />
                            </div>
                            <div className="stat-content">
                                <span className="stat-label">{stat.label}</span>
                                <span className="stat-value">{stat.value}</span>
                                <span className={`stat-change ${stat.trend}`}>
                                    {stat.trend === 'up' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                                    {stat.change}
                                </span>
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Charts Row 1 */}
                <div className="charts-row">
                    {/* Performance Metrics */}
                    <motion.div
                        className="chart-card glass-card"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        <div className="chart-header">
                            <div>
                                <h3>Model Performance</h3>
                                <p>Precision, Recall & F1 Score</p>
                            </div>
                            <div className="chart-legend">
                                <span className="legend-item"><span className="dot precision"></span>Precision</span>
                                <span className="legend-item"><span className="dot recall"></span>Recall</span>
                                <span className="legend-item"><span className="dot f1"></span>F1</span>
                            </div>
                        </div>
                        <ResponsiveContainer width="100%" height={280}>
                            <LineChart data={performanceData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                                <YAxis domain={[90, 100]} stroke="#64748b" fontSize={12} />
                                <Tooltip
                                    contentStyle={{
                                        background: '#12182b',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="precision"
                                    stroke="#00d4ff"
                                    strokeWidth={2}
                                    dot={{ fill: '#00d4ff', r: 4 }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="recall"
                                    stroke="#8b5cf6"
                                    strokeWidth={2}
                                    dot={{ fill: '#8b5cf6', r: 4 }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="f1"
                                    stroke="#10b981"
                                    strokeWidth={2}
                                    dot={{ fill: '#10b981', r: 4 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </motion.div>

                    {/* Threat Distribution */}
                    <motion.div
                        className="chart-card glass-card"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <div className="chart-header">
                            <div>
                                <h3>Threat Distribution</h3>
                                <p>Fraud types detected</p>
                            </div>
                        </div>
                        <div className="pie-container">
                            <ResponsiveContainer width="100%" height={220}>
                                <PieChart>
                                    <Pie
                                        data={threatDistribution}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={90}
                                        paddingAngle={2}
                                        dataKey="value"
                                    >
                                        {threatDistribution.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{
                                            background: '#12182b',
                                            border: '1px solid rgba(255,255,255,0.1)',
                                            borderRadius: '8px'
                                        }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                            <div className="pie-legend">
                                {threatDistribution.map((item, index) => (
                                    <div key={index} className="pie-legend-item">
                                        <span className="dot" style={{ background: item.color }}></span>
                                        <span className="legend-label">{item.name}</span>
                                        <span className="legend-value">{item.value}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                </div>

                {/* Charts Row 2 */}
                <div className="charts-row">
                    {/* Verification Trend */}
                    <motion.div
                        className="chart-card glass-card wide"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                    >
                        <div className="chart-header">
                            <div>
                                <h3>Verification Trend</h3>
                                <p>Monthly verification volume</p>
                            </div>
                        </div>
                        <ResponsiveContainer width="100%" height={280}>
                            <AreaChart data={verificationTrend}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                                <YAxis stroke="#64748b" fontSize={12} />
                                <Tooltip
                                    contentStyle={{
                                        background: '#12182b',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="approved"
                                    stackId="1"
                                    stroke="#10b981"
                                    fill="rgba(16, 185, 129, 0.3)"
                                />
                                <Area
                                    type="monotone"
                                    dataKey="rejected"
                                    stackId="1"
                                    stroke="#ef4444"
                                    fill="rgba(239, 68, 68, 0.3)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </motion.div>
                </div>

                {/* Fraud Detection Chart */}
                <motion.div
                    className="chart-card glass-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                >
                    <div className="chart-header">
                        <div>
                            <h3>Fraud Detection Rate</h3>
                            <p>Detected vs Missed fraud attempts</p>
                        </div>
                    </div>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={fraudDetectionData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                            <YAxis stroke="#64748b" fontSize={12} />
                            <Tooltip
                                contentStyle={{
                                    background: '#12182b',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px'
                                }}
                            />
                            <Bar dataKey="detected" fill="#10b981" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="missed" fill="#ef4444" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </motion.div>

                {/* Model Metrics */}
                <motion.div
                    className="metrics-section"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7 }}
                >
                    <h3>Model Performance Metrics</h3>
                    <div className="metrics-grid">
                        {modelMetrics.map((metric, index) => (
                            <div key={index} className="metric-card glass-card">
                                <div className="metric-header">
                                    <Target size={18} />
                                    <span>{metric.name}</span>
                                </div>
                                <div className="metric-value-large">{metric.value}%</div>
                                <div className="metric-progress">
                                    <div
                                        className="metric-progress-fill"
                                        style={{ width: `${metric.value}%` }}
                                    />
                                </div>
                                <div className="metric-target">
                                    Target: {metric.target}%
                                </div>
                            </div>
                        ))}
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default Admin;
