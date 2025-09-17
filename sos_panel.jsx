// React Component for SOS Emergency Management Panel
import React, { useState, useEffect } from 'react';
import './SOSPanel.css';

const SOSPanel = () => {
    const [activeSOS, setActiveSOS] = useState([]);
    const [selectedSOS, setSelectedSOS] = useState(null);
    const [newAlert, setNewAlert] = useState(false);

    useEffect(() => {
        fetchActiveSOS();

        // Setup WebSocket for real-time SOS alerts
        const ws = new WebSocket('ws://localhost:8000/ws');

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === 'sos_alert') {
                setNewAlert(true);
                fetchActiveSOS();

                // Show notification
                showNotification('New SOS Alert!', message.data);

                // Reset alert after 5 seconds
                setTimeout(() => setNewAlert(false), 5000);
            }
        };

        return () => ws.close();
    }, []);

    const fetchActiveSOS = async () => {
        try {
            const response = await fetch('/api/sos/active');
            const data = await response.json();
            setActiveSOS(data);
        } catch (error) {
            console.error('Error fetching SOS data:', error);
        }
    };

    const showNotification = (title, data) => {
        if (Notification.permission === 'granted') {
            new Notification(title, {
                body: `Emergency: ${data.emergency_type}`,
                icon: '/emergency-icon.png'
            });
        }
    };

    const handleSOSResponse = async (sosId, action) => {
        try {
            const response = await fetch(`/api/sos/${sosId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    status: action,
                    response_time: new Date().toISOString(),
                    officer_id: 'OFFICER_001'
                })
            });

            if (response.ok) {
                fetchActiveSOS();
                setSelectedSOS(null);
            }
        } catch (error) {
            console.error('Error updating SOS status:', error);
        }
    };

    const getPriorityColor = (priority) => {
        if (priority >= 9) return '#f44336'; // High priority - Red
        if (priority >= 7) return '#ff9800'; // Medium priority - Orange
        return '#4caf50'; // Low priority - Green
    };

    const getEmergencyIcon = (type) => {
        const icons = {
            'medical': '🚑',
            'fire': '🚒',
            'accident': '🚗',
            'crime': '🚔',
            'general': '⚠️'
        };
        return icons[type] || '⚠️';
    };

    return (
        <div className="sos-panel">
            <div className="panel-header">
                <h2>
                    🚨 Emergency Response Center
                    {newAlert && <span className="new-alert">NEW ALERT!</span>}
                </h2>
                <div className="stats">
                    <span>Active: {activeSOS.length}</span>
                    <span>Response Time: 4.2 min avg</span>
                </div>
            </div>

            <div className="sos-list">
                {activeSOS.length === 0 ? (
                    <div className="no-sos">
                        <p>✅ No active emergencies</p>
                    </div>
                ) : (
                    activeSOS.map(sos => (
                        <div
                            key={sos.id}
                            className={`sos-item ${selectedSOS?.id === sos.id ? 'selected' : ''}`}
                            onClick={() => setSelectedSOS(sos)}
                            style={{
                                borderLeft: `4px solid ${getPriorityColor(sos.priority)}`
                            }}
                        >
                            <div className="sos-header">
                                <span className="emergency-icon">
                                    {getEmergencyIcon(sos.emergency_type)}
                                </span>
                                <div className="sos-info">
                                    <h4>SOS #{sos.id}</h4>
                                    <p>{sos.emergency_type.toUpperCase()}</p>
                                </div>
                                <div className="sos-priority">
                                    <span className="priority-badge" style={{
                                        backgroundColor: getPriorityColor(sos.priority)
                                    }}>
                                        P{sos.priority}
                                    </span>
                                </div>
                            </div>

                            <div className="sos-details">
                                <p><strong>Location:</strong> {sos.location.address || 'Unknown'}</p>
                                <p><strong>Time:</strong> {new Date(sos.timestamp).toLocaleString()}</p>
                                <p><strong>Status:</strong> {sos.status}</p>
                                {sos.description && (
                                    <p><strong>Description:</strong> {sos.description}</p>
                                )}
                            </div>

                            <div className="sos-actions">
                                <button
                                    className="btn-respond"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleSOSResponse(sos.id, 'responding');
                                    }}
                                >
                                    📞 Respond
                                </button>
                                <button
                                    className="btn-dispatch"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleSOSResponse(sos.id, 'dispatched');
                                    }}
                                >
                                    🚗 Dispatch
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {selectedSOS && (
                <div className="sos-detail-panel">
                    <div className="detail-header">
                        <h3>SOS Details #{selectedSOS.id}</h3>
                        <button onClick={() => setSelectedSOS(null)}>✕</button>
                    </div>

                    <div className="detail-content">
                        <div className="detail-section">
                            <h4>Emergency Information</h4>
                            <p><strong>Type:</strong> {selectedSOS.emergency_type}</p>
                            <p><strong>Priority:</strong> {selectedSOS.priority}/10</p>
                            <p><strong>Status:</strong> {selectedSOS.status}</p>
                            <p><strong>Reported:</strong> {new Date(selectedSOS.timestamp).toLocaleString()}</p>
                        </div>

                        <div className="detail-section">
                            <h4>Location Details</h4>
                            <p><strong>Coordinates:</strong> {selectedSOS.location.lat}, {selectedSOS.location.lon}</p>
                            <p><strong>Address:</strong> {selectedSOS.location.address || 'Unknown'}</p>
                        </div>

                        <div className="detail-section">
                            <h4>Contact Information</h4>
                            <p><strong>User ID:</strong> {selectedSOS.user_id}</p>
                            <p><strong>Contact:</strong> {selectedSOS.contact || 'Not provided'}</p>
                        </div>

                        {selectedSOS.green_corridor && (
                            <div className="detail-section">
                                <h4>Green Corridor</h4>
                                <p><strong>Route:</strong> {selectedSOS.green_corridor.route.join(' → ')}</p>
                                <p><strong>Duration:</strong> {selectedSOS.green_corridor.duration}s</p>
                                <p><strong>Created:</strong> {new Date(selectedSOS.green_corridor.created_at).toLocaleString()}</p>
                            </div>
                        )}

                        <div className="detail-actions">
                            <button
                                className="btn-complete"
                                onClick={() => handleSOSResponse(selectedSOS.id, 'completed')}
                            >
                                ✅ Mark Complete
                            </button>
                            <button
                                className="btn-cancel"
                                onClick={() => handleSOSResponse(selectedSOS.id, 'cancelled')}
                            >
                                ❌ Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SOSPanel;
