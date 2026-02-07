import { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
    Upload,
    Camera,
    Brain,
    CheckCircle,
    AlertCircle,
    FileImage,
    X,
    Zap,
    Eye,
    Loader2,
    ArrowRight,
    ArrowLeft,
    Shield
} from 'lucide-react';
import { verifyDocument, verifyFace, calculateKYCScore, submitBehavior, updateUserKyc } from '../api/kycApi';
import './KYCPipeline.css';

const KYCPipeline = () => {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(1);

    // Document state
    const [idDocument, setIdDocument] = useState(null);
    const [idPreview, setIdPreview] = useState(null);
    const [idQuality, setIdQuality] = useState(null);
    const [docResult, setDocResult] = useState(null);
    const [docLoading, setDocLoading] = useState(false);
    const [docError, setDocError] = useState(null);

    // Face/Selfie state
    const [selfieImage, setSelfieImage] = useState(null);
    const [isCapturing, setIsCapturing] = useState(false);
    const [livenessStatus, setLivenessStatus] = useState('idle'); // idle, scanning, verified, failed
    const [faceResult, setFaceResult] = useState(null);
    const [faceLoading, setFaceLoading] = useState(false);
    const [faceError, setFaceError] = useState(null);

    // Fusion state
    const [fusionProgress, setFusionProgress] = useState(0);
    const [fusionStage, setFusionStage] = useState('');
    const [kycResult, setKycResult] = useState(null);

    // Behavior tracking
    const [sessionId] = useState(() => `kyc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
    const [behaviorEvents, setBehaviorEvents] = useState([]);

    const videoRef = useRef(null);
    const streamRef = useRef(null);

    const steps = [
        { id: 1, title: 'ID Upload', icon: Upload },
        { id: 2, title: 'Biometric Liveness', icon: Camera },
        { id: 3, title: 'Fraud Fusion', icon: Brain }
    ];

    // Track behavioral events (keystrokes, mouse movements)
    useEffect(() => {
        const handleKeyDown = (e) => {
            setBehaviorEvents(prev => [...prev, {
                type: 'k',
                t: Date.now(),
                d: 0 // Will be calculated on keyup
            }]);
        };

        const handleMouseMove = (e) => {
            setBehaviorEvents(prev => {
                // Throttle mouse events
                const lastEvent = prev[prev.length - 1];
                if (lastEvent && lastEvent.type === 'm' && Date.now() - lastEvent.t < 50) {
                    return prev;
                }
                return [...prev, {
                    type: 'm',
                    t: Date.now(),
                    x: e.clientX,
                    y: e.clientY,
                    v: 0.5 // Placeholder velocity
                }];
            });
        };

        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('mousemove', handleMouseMove);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('mousemove', handleMouseMove);
        };
    }, []);

    // Document verification via API
    const analyzeDocument = async (file) => {
        setDocLoading(true);
        setDocError(null);
        setIdQuality(null);

        try {
            const result = await verifyDocument(file);
            console.log('[KYC] Document verification result:', result);

            // Safely extract values with defaults
            const qualityScore = result?.quality_score ?? 0.5;
            const forgeryScore = result?.forgery_score ?? 0.5;
            const decision = result?.decision ?? 'MANUAL_REVIEW';

            // Map API response to quality display format
            const quality = {
                blur: qualityScore > 0.5 ? 'pass' : 'warn',
                brightness: qualityScore > 0.4 ? 'pass' : 'warn',
                resolution: qualityScore > 0.3 ? 'pass' : 'fail',
                glare: qualityScore > 0.5 ? 'pass' : 'warn',
                forgery: forgeryScore < 0.5 ? 'pass' : forgeryScore < 0.7 ? 'warn' : 'fail',
                overall: decision === 'APPROVE' ? 'pass' : decision === 'MANUAL_REVIEW' ? 'warn' : 'fail'
            };

            setIdQuality(quality);
            setDocResult(result || {});

        } catch (error) {
            console.error('Document verification failed:', error);
            setDocError(error.message || 'Document verification failed');
            setIdQuality({ overall: 'fail' });
        } finally {
            setDocLoading(false);
        }
    };

    const handleDrop = useCallback(async (e) => {
        e.preventDefault();
        const file = e.dataTransfer?.files[0] || e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            setIdDocument(file);
            setIdPreview(URL.createObjectURL(file));
            await analyzeDocument(file);
        }
    }, []);

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    // Camera handling
    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user', width: 640, height: 480 }
            });
            streamRef.current = stream;
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }
            setIsCapturing(true);
        } catch (err) {
            console.error('Camera access denied:', err);
            setFaceError('Camera access denied. Please allow camera permissions.');
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
        }
        setIsCapturing(false);
    };

    // Face verification via API
    const captureSelfie = async () => {
        if (!videoRef.current) {
            setFaceError('Camera not initialized');
            return;
        }

        // Check if video has valid dimensions
        const video = videoRef.current;
        if (!video.videoWidth || !video.videoHeight || video.videoWidth === 0 || video.videoHeight === 0) {
            setFaceError('Camera not ready. Please wait for the video to load.');
            return;
        }

        // Capture image from video
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');

        if (!ctx) {
            setFaceError('Failed to create canvas context');
            return;
        }

        ctx.drawImage(video, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg', 0.9);

        // Validate the captured image
        if (!imageData || imageData === 'data:,' || imageData.length < 100) {
            setFaceError('Failed to capture image. Please try again.');
            return;
        }

        console.log('[KYC] Captured selfie, size:', imageData.length);

        setSelfieImage(imageData);
        stopCamera();

        // Call face verification API
        setLivenessStatus('scanning');
        setFaceLoading(true);
        setFaceError(null);

        try {
            // Get user email for face match comparison with stored embedding
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            const result = await verifyFace(imageData, user.email || null);
            console.log('[KYC] Face verification result:', result);
            setFaceResult(result);

            if (result.success && result.is_live && result.face_detected) {
                setLivenessStatus('verified');
            } else if (!result.face_detected) {
                setLivenessStatus('failed');
                setFaceError('No face detected. Please try again.');
            } else if (!result.is_live) {
                setLivenessStatus('failed');
                setFaceError('Liveness check failed. Please ensure you are in good lighting.');
            } else {
                setLivenessStatus('failed');
                setFaceError(result.reason || 'Face verification failed');
            }
        } catch (error) {
            console.error('Face verification failed:', error);
            setLivenessStatus('failed');
            setFaceError(error.message || 'Face verification failed');
        } finally {
            setFaceLoading(false);
        }
    };

    // Cleanup camera on unmount
    useEffect(() => {
        return () => stopCamera();
    }, []);

    // Auto-start camera when entering step 2
    useEffect(() => {
        if (currentStep === 2 && !isCapturing && !selfieImage) {
            startCamera();
        } else if (currentStep !== 2 && isCapturing) {
            stopCamera();
        }
    }, [currentStep, isCapturing, selfieImage]);

    // Fusion progress with real API
    useEffect(() => {
        if (currentStep === 3) {
            const runFusion = async () => {
                const stages = [
                    { progress: 15, label: 'Extracting document features...' },
                    { progress: 35, label: 'Analyzing biometric embeddings...' },
                    { progress: 55, label: 'Processing behavioral patterns...' },
                    { progress: 75, label: 'Computing fraud probability scores...' },
                    { progress: 90, label: 'Generating decision matrix...' },
                ];

                // Animate through stages
                for (const stage of stages) {
                    setFusionProgress(stage.progress);
                    setFusionStage(stage.label);
                    await new Promise(resolve => setTimeout(resolve, 800));
                }

                // Submit behavioral data
                try {
                    await submitBehavior(sessionId, behaviorEvents);
                } catch (e) {
                    console.warn('Behavior submission failed:', e);
                }

                // Calculate final KYC score
                try {
                    const scores = {
                        doc_score: docResult?.risk_score || 0.5,
                        face_score: faceResult?.is_live ? (1 - (faceResult?.liveness_confidence || 0.5)) : 0.8,
                        behavior_score: 0.2 // Default low risk for now
                    };

                    const result = await calculateKYCScore(scores);
                    setKycResult(result);

                    // Store face embedding and KYC data in database
                    try {
                        const user = JSON.parse(localStorage.getItem('user') || '{}');
                        if (user.email && faceResult?.embedding) {
                            await updateUserKyc(user.email, faceResult.embedding, {
                                scores: scores,
                                decision: result.decision,
                                final_risk_score: result.final_risk_score
                            });
                            console.log('KYC data stored successfully');
                        }
                    } catch (storeError) {
                        console.warn('Failed to store KYC data:', storeError);
                    }

                    setFusionProgress(100);
                    setFusionStage(result.message || 'Verification complete!');

                    // Navigate after showing result
                    setTimeout(() => navigate('/dashboard'), 2000);

                } catch (error) {
                    console.error('KYC score calculation failed:', error);
                    setFusionStage('Error calculating score');
                }
            };

            runFusion();
        }
    }, [currentStep, navigate, docResult, faceResult, sessionId, behaviorEvents]);

    const canProceed = () => {
        if (currentStep === 1) return idQuality?.overall === 'pass' || idQuality?.overall === 'warn';
        if (currentStep === 2) return livenessStatus === 'verified';
        return false;
    };

    const nextStep = () => {
        if (canProceed() && currentStep < 3) {
            setCurrentStep(currentStep + 1);
        }
    };

    const prevStep = () => {
        if (currentStep > 1) {
            setCurrentStep(currentStep - 1);
            if (currentStep === 2) {
                stopCamera();
                setSelfieImage(null);
                setLivenessStatus('idle');
                setFaceError(null);
            }
        }
    };

    return (
        <div className="kyc-page">
            <div className="kyc-container">
                {/* Step Indicator */}
                <div className="step-indicator">
                    {steps.map((step, index) => (
                        <div key={step.id} className="step-item-wrapper">
                            <motion.div
                                className={`step-item ${currentStep >= step.id ? 'active' : ''} ${currentStep > step.id ? 'completed' : ''}`}
                                initial={false}
                                animate={{ scale: currentStep === step.id ? 1.05 : 1 }}
                            >
                                <div className="step-icon">
                                    {currentStep > step.id ? (
                                        <CheckCircle size={24} />
                                    ) : (
                                        <step.icon size={24} />
                                    )}
                                </div>
                                <span className="step-title">{step.title}</span>
                            </motion.div>
                            {index < steps.length - 1 && (
                                <div className={`step-connector ${currentStep > step.id ? 'active' : ''}`} />
                            )}
                        </div>
                    ))}
                </div>

                {/* Step Content */}
                <AnimatePresence mode="wait">
                    {/* Step 1: ID Upload */}
                    {currentStep === 1 && (
                        <motion.div
                            key="step1"
                            className="step-content"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                        >
                            <div className="step-header">
                                <h2>Upload Identity Document</h2>
                                <p>Upload a clear photo of your government-issued ID for verification</p>
                            </div>

                            <div
                                className={`dropzone ${idPreview ? 'has-file' : ''}`}
                                onDrop={handleDrop}
                                onDragOver={handleDragOver}
                            >
                                {idPreview ? (
                                    <div className="preview-container">
                                        <img src={idPreview} alt="ID Preview" className="id-preview" />
                                        <button
                                            className="remove-file"
                                            onClick={() => {
                                                setIdDocument(null);
                                                setIdPreview(null);
                                                setIdQuality(null);
                                                setDocResult(null);
                                                setDocError(null);
                                            }}
                                        >
                                            <X size={16} />
                                        </button>
                                    </div>
                                ) : (
                                    <div className="dropzone-content">
                                        <div className="dropzone-icon">
                                            <FileImage size={48} />
                                        </div>
                                        <p className="dropzone-text">Drag & drop your ID here</p>
                                        <span className="dropzone-hint">or click to browse</span>
                                        <input
                                            type="file"
                                            accept="image/*"
                                            onChange={handleDrop}
                                            className="file-input"
                                        />
                                    </div>
                                )}
                            </div>

                            {/* Error Message */}
                            {docError && (
                                <motion.div
                                    className="error-panel"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                >
                                    <AlertCircle size={18} />
                                    <span>{docError}</span>
                                </motion.div>
                            )}

                            {/* Quality Feedback */}
                            {idPreview && (
                                <motion.div
                                    className="quality-panel glass-card"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                >
                                    <div className="quality-header">
                                        <Zap size={18} />
                                        <span>AI Quality Analysis</span>
                                        {docLoading && <Loader2 size={18} className="spin" />}
                                    </div>

                                    {idQuality && !docLoading && (
                                        <div className="quality-checks">
                                            {Object.entries(idQuality).filter(([key]) => key !== 'overall').map(([key, value]) => (
                                                <div key={key} className={`quality-item ${value}`}>
                                                    <span className="quality-label">{key}</span>
                                                    <span className={`quality-status ${value}`}>
                                                        {value === 'pass' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
                                                        {value}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {docResult?.ocr_data && Object.keys(docResult.ocr_data).length > 0 && (
                                        <div className="ocr-results">
                                            <h4>Extracted Information</h4>
                                            {Object.entries(docResult.ocr_data).map(([key, value]) => {
                                                // Skip null/undefined values and complex nested objects
                                                if (!value || key === 'all_ids') return null;
                                                // If value is an object, stringify it
                                                const displayValue = typeof value === 'object'
                                                    ? JSON.stringify(value)
                                                    : String(value);
                                                return (
                                                    <p key={key}><strong>{key}:</strong> {displayValue}</p>
                                                );
                                            })}
                                        </div>
                                    )}
                                </motion.div>
                            )}
                        </motion.div>
                    )}

                    {/* Step 2: Face Capture */}
                    {currentStep === 2 && (
                        <motion.div
                            key="step2"
                            className="step-content"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                        >
                            <div className="step-header">
                                <h2>Capture Selfie</h2>
                                <p>Take a clear photo of your face for verification</p>
                            </div>

                            {/* Error Message */}
                            {faceError && (
                                <div className="error-panel">
                                    <AlertCircle size={18} />
                                    <span>{faceError}</span>
                                </div>
                            )}

                            <div className="camera-container glass-card">
                                {/* Camera Preview Box */}
                                <div className="simple-camera-box">
                                    {!selfieImage ? (
                                        <>
                                            <video
                                                ref={videoRef}
                                                autoPlay
                                                playsInline
                                                muted
                                                className="simple-video-preview"
                                                style={{ display: isCapturing ? 'block' : 'none' }}
                                            />
                                            {!isCapturing && (
                                                <div className="camera-placeholder">
                                                    <Camera size={48} />
                                                    <p>Click "Start Camera" to begin</p>
                                                </div>
                                            )}
                                        </>
                                    ) : (
                                        <img src={selfieImage} alt="Your selfie" className="selfie-preview" />
                                    )}
                                </div>

                                {/* Status Badge */}
                                {selfieImage && (
                                    <div className={`status-badge ${livenessStatus}`}>
                                        {faceLoading && (
                                            <>
                                                <Loader2 size={16} className="spin" />
                                                <span>Verifying...</span>
                                            </>
                                        )}
                                        {livenessStatus === 'verified' && (
                                            <>
                                                <CheckCircle size={16} />
                                                <span>Face Verified</span>
                                            </>
                                        )}
                                        {livenessStatus === 'failed' && !faceLoading && (
                                            <>
                                                <AlertCircle size={16} />
                                                <span>Verification Failed</span>
                                            </>
                                        )}
                                    </div>
                                )}

                                {/* Action Buttons */}
                                <div className="camera-buttons">
                                    {!selfieImage ? (
                                        <>
                                            {!isCapturing ? (
                                                <button className="btn btn-primary" onClick={startCamera}>
                                                    <Camera size={18} />
                                                    Start Camera
                                                </button>
                                            ) : (
                                                <button className="btn btn-primary" onClick={captureSelfie}>
                                                    <Camera size={18} />
                                                    Capture Selfie
                                                </button>
                                            )}
                                        </>
                                    ) : (
                                        <button
                                            className="btn btn-secondary"
                                            onClick={() => {
                                                setSelfieImage(null);
                                                setLivenessStatus('idle');
                                                setFaceError(null);
                                                setFaceResult(null);
                                                startCamera();
                                            }}
                                        >
                                            <Camera size={18} />
                                            Retake Photo
                                        </button>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Step 3: Fraud Fusion */}
                    {currentStep === 3 && (
                        <motion.div
                            key="step3"
                            className="step-content fusion-step"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                        >
                            <div className="step-header">
                                <h2>Fraud Fusion Analysis</h2>
                                <p>Correlating biometric, document, and behavioral signals</p>
                            </div>

                            <div className="fusion-container glass-card">
                                <div className="fusion-visual">
                                    <div className="fusion-center">
                                        <Shield size={48} />
                                        <div className="fusion-pulse"></div>
                                    </div>

                                    <div className="fusion-nodes">
                                        <motion.div
                                            className="fusion-node"
                                            animate={{ scale: [1, 1.1, 1] }}
                                            transition={{ repeat: Infinity, duration: 2 }}
                                        >
                                            <FileImage size={24} />
                                            <span>Document</span>
                                        </motion.div>
                                        <motion.div
                                            className="fusion-node"
                                            animate={{ scale: [1, 1.1, 1] }}
                                            transition={{ repeat: Infinity, duration: 2, delay: 0.3 }}
                                        >
                                            <Camera size={24} />
                                            <span>Biometric</span>
                                        </motion.div>
                                        <motion.div
                                            className="fusion-node"
                                            animate={{ scale: [1, 1.1, 1] }}
                                            transition={{ repeat: Infinity, duration: 2, delay: 0.6 }}
                                        >
                                            <Brain size={24} />
                                            <span>Behavioral</span>
                                        </motion.div>
                                    </div>

                                    <svg className="fusion-lines" viewBox="0 0 300 300">
                                        <line x1="150" y1="100" x2="60" y2="200" className="fusion-line" />
                                        <line x1="150" y1="100" x2="150" y2="220" className="fusion-line" />
                                        <line x1="150" y1="100" x2="240" y2="200" className="fusion-line" />
                                    </svg>
                                </div>

                                <div className="fusion-progress">
                                    <div className="progress-bar">
                                        <motion.div
                                            className="progress-bar-fill"
                                            initial={{ width: 0 }}
                                            animate={{ width: `${fusionProgress}%` }}
                                        />
                                    </div>
                                    <div className="progress-info">
                                        <span className="progress-stage">{fusionStage}</span>
                                        <span className="progress-percent">{fusionProgress}%</span>
                                    </div>
                                </div>

                                {kycResult && (
                                    <motion.div
                                        className={`kyc-result ${kycResult.status}`}
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                    >
                                        <h3>
                                            {kycResult.decision === 'APPROVED' && '✅ Identity Verified'}
                                            {kycResult.decision === 'MANUAL_REVIEW' && '⏳ Pending Review'}
                                            {kycResult.decision === 'REJECTED' && '❌ Verification Failed'}
                                        </h3>
                                        <p>{kycResult.message}</p>

                                        {/* Detailed Score Breakdown */}
                                        <div className="score-breakdown">
                                            <h4>Verification Scores</h4>
                                            <div className="score-grid">
                                                <div className="score-item">
                                                    <span className="score-label">Document Score</span>
                                                    <span className="score-value">
                                                        {((1 - (docResult?.risk_score || 0.5)) * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                                <div className="score-item">
                                                    <span className="score-label">Liveness Score</span>
                                                    <span className="score-value">
                                                        {((faceResult?.liveness_confidence || 0) * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                                <div className="score-item">
                                                    <span className="score-label">Face Match</span>
                                                    <span className="score-value">
                                                        {faceResult?.face_match_score
                                                            ? `${(faceResult.face_match_score * 100).toFixed(0)}%`
                                                            : 'First KYC'}
                                                    </span>
                                                </div>
                                                <div className="score-item">
                                                    <span className="score-label">OCR Confidence</span>
                                                    <span className="score-value">
                                                        {((docResult?.ocr_data?.confidence || 0.5) * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                            </div>

                                            {/* Extracted Data Summary */}
                                            {docResult?.ocr_data?.extracted_data && (
                                                <div className="extracted-data-summary">
                                                    <h5>Extracted Information</h5>
                                                    {docResult.ocr_data.extracted_data.name && (
                                                        <p><strong>Name:</strong> {docResult.ocr_data.extracted_data.name}</p>
                                                    )}
                                                    {docResult.ocr_data.extracted_data.id_number && (
                                                        <p><strong>ID:</strong> {docResult.ocr_data.extracted_data.id_number}</p>
                                                    )}
                                                    {docResult.ocr_data.extracted_data.dob && (
                                                        <p><strong>DOB:</strong> {docResult.ocr_data.extracted_data.dob}</p>
                                                    )}
                                                </div>
                                            )}
                                        </div>

                                        <p className="risk-score">
                                            Overall Risk: {(kycResult.final_risk_score * 100).toFixed(1)}%
                                        </p>
                                    </motion.div>
                                )}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Navigation */}
                {currentStep < 3 && (
                    <div className="step-navigation">
                        <button
                            className="btn btn-ghost"
                            onClick={prevStep}
                            disabled={currentStep === 1}
                        >
                            <ArrowLeft size={18} />
                            Back
                        </button>
                        <button
                            className="btn btn-primary"
                            onClick={nextStep}
                            disabled={!canProceed()}
                        >
                            Continue
                            <ArrowRight size={18} />
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default KYCPipeline;
