
(function () {
    // Unique session ID handling
    const getSessionId = () => {
        if (window.PYTHON_SESSION_ID) {
            return window.PYTHON_SESSION_ID;
        }
        let sid = sessionStorage.getItem('behavior_session_id');
        if (!sid) {
            sid = 'sess_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('behavior_session_id', sid);
        }
        return sid;
    };

    const SESSION_ID = getSessionId();
    const API_URL = 'http://localhost:5001/api/behavior';

    // State buffer
    let eventBuffer = [];
    const MAX_BUFFER_SIZE = 50;

    // Keystroke state
    let keyTimes = {};

    // Mouse state
    let mousePath = 0;
    let lastMousePos = null;
    let lastMouseTime = Date.now();

    // Helper to push data
    const flushData = () => {
        if (eventBuffer.length === 0) return;

        const payload = {
            session_id: SESSION_ID,
            events: eventBuffer,
            timestamp: Date.now()
        };

        // Clear buffer immediately to avoid duplicates if async feels slow
        eventBuffer = [];

        fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            keepalive: true // Ensure sends even if page unloads
        }).catch(err => console.error("Behavior tracking error:", err));
    };

    // --- Event Listeners ---

    // 1. Keystroke Dynamics (Privacy safe: no key codes stored for text inputs)
    // We only care about timing: Flight Time (Up->Down) and Dwell Time (Down->Up)

    document.addEventListener('keydown', (e) => {
        const now = Date.now();
        // If it's a printable key or standard nav, track timing
        if (!keyTimes[e.code]) {
            keyTimes[e.code] = now;
        }
    });

    document.addEventListener('keyup', (e) => {
        const now = Date.now();
        const downTime = keyTimes[e.code];
        if (downTime) {
            const dwell = now - downTime;
            eventBuffer.push({
                type: 'k', // keystroke
                d: dwell, // dwell time
                t: now // timestamp
            });
            delete keyTimes[e.code];
        }

        // Check buffer
        if (eventBuffer.length >= MAX_BUFFER_SIZE) flushData();
    });

    // 2. Mouse Dynamics
    // We don't stream every pixel. We calculate velocity/distance periodically.
    document.addEventListener('mousemove', (e) => {
        const now = Date.now();
        if (now - lastMouseTime > 100) { // Sample every 100ms
            if (lastMousePos) {
                const dist = Math.sqrt(
                    Math.pow(e.clientX - lastMousePos.x, 2) +
                    Math.pow(e.clientY - lastMousePos.y, 2)
                );
                mousePath += dist;
                eventBuffer.push({
                    type: 'm', // mouse
                    v: dist / (now - lastMouseTime), // velocity (px/ms)
                    t: now
                });
            }
            lastMousePos = { x: e.clientX, y: e.clientY };
            lastMouseTime = now;

            if (eventBuffer.length >= MAX_BUFFER_SIZE) flushData();
        }
    });

    // 3. Focus/Blur (Tab switching)
    window.addEventListener('blur', () => {
        eventBuffer.push({ type: 'b', t: Date.now() }); // blur
        flushData();
    });

    window.addEventListener('focus', () => {
        eventBuffer.push({ type: 'f', t: Date.now() }); // focus
    });

    // Periodic flush (every 2 seconds to capture end-of-flow data)
    setInterval(flushData, 2000);

    // Initial ping
    eventBuffer.push({ type: 'init', t: Date.now(), agent: navigator.userAgent });
    flushData();

    console.log("Behavioral Analysis Initialized. Session:", SESSION_ID);
})();
