// React Component for Traffic Violations Management
import React, { useState, useEffect } from 'react';
import './Violations.css';

const Violations = () => {
    const [violations, setViolations] = useState([]);
    const [selectedViolation, setSelectedViolation] = useState(null);
    const [filter, setFilter] = useState('all');
    const [sortBy, setSortBy] = useState('timestamp');
    const [analytics, setAnalytics] = useState({});

    useEffect(() => {
        fetchViolations();
        fetchAnalytics();
    }, [filter, sortBy]);

    const fetchViolations = async () => {
        try {
            const params = new URLSearchParams();
            if (filter !== 'all') params.append('status', filter);

            const response = await fetch(`/api/violations/?${params}`);
            const data = await response.json();

            // Sort violations
            const sortedData = data.sort((a, b) => {
                if (sortBy === 'timestamp') {
                    return new Date(b.timestamp) - new Date(a.timestamp);
                } else if (sortBy === 'fine_amount') {
                    return b.fine_amount - a.fine_amount;
                }
                return 0;
            });

            setViolations(sortedData);
        } catch (error) {
            console.error('Error fetching violations:', error);
        }
    };

    const fetchAnalytics = async () => {
        try {
            const response = await fetch('/api/violations/analytics/summary');
            const data = await response.json();
            setAnalytics(data);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        }
    };

    const handleViolationAction = async (violationId, action, notes = '') => {
        try {
            const response = await fetch(`/api/violations/${violationId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    status: action,
                    officer_notes: notes,
                    processed_by: 'OFFICER_001',
                    processed_at: new Date().toISOString()
                })
            });

            if (response.ok) {
                fetchViolations();
                fetchAnalytics();
                setSelectedViolation(null);
            }
        } catch (error) {
            console.error('Error updating violation:', error);
        }
    };

    const getViolationIcon = (type) => {
        const icons = {
            'RED_LIGHT_VIOLATION': '🚦',
            'SPEEDING_VIOLATION': '⚡',
            'WRONG_SIDE_DRIVING': '↔️',
            'ILLEGAL_PARKING': '🚫',
            'MOBILE_PHONE_USE': '📱',
            'SEAT_BELT_VIOLATION': '🔒'
        };
        return icons[type] || '⚠️';
    };

    const getStatusColor = (status) => {
        const colors = {
            'pending': '#ff9800',
            'approved': '#4caf50',
            'rejected': '#f44336',
            'under_review': '#2196f3'
        };
        return colors[status] || '#757575';
    };

    const getSeverityColor = (fineAmount) => {
        if (fineAmount >= 1000) return '#f44336'; // High severity
        if (fineAmount >= 500) return '#ff9800';  // Medium severity
        return '#4caf50'; // Low severity
    };

    return (
        <div className="violations-panel">
            <div className="panel-header">
                <h2>🚦 Traffic Violations Management</h2>

                {/* Analytics Summary */}
                <div className="analytics-summary">
                    <div className="stat-card">
                        <h3>{analytics.total_violations}</h3>
                        <p>Total Violations</p>
                    </div>
                    <div className="stat-card">
                        <h3>{analytics.pending_violations}</h3>
                        <p>Pending Review</p>
                    </div>
                    <div className="stat-card">
                        <h3>₹{analytics.total_fine_amount?.toLocaleString()}</h3>
                        <p>Total Fines</p>
                    </div>
                    <div className="stat-card">
                        <h3>₹{Math.round(analytics.average_fine)}</h3>
                        <p>Average Fine</p>
                    </div>
                </div>

                {/* Controls */}
                <div className="controls">
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">All Violations</option>
                        <option value="pending">Pending</option>
                        <option value="approved">Approved</option>
                        <option value="rejected">Rejected</option>
                    </select>

                    <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="sort-select"
                    >
                        <option value="timestamp">Sort by Time</option>
                        <option value="fine_amount">Sort by Fine Amount</option>
                    </select>
                </div>
            </div>

            <div className="violations-content">
                <div className="violations-list">
                    {violations.map(violation => (
                        <div
                            key={violation.id}
                            className={`violation-item ${selectedViolation?.id === violation.id ? 'selected' : ''}`}
                            onClick={() => setSelectedViolation(violation)}
                        >
                            <div className="violation-header">
                                <span className="violation-icon">
                                    {getViolationIcon(violation.violation_type)}
                                </span>
                                <div className="violation-info">
                                    <h4>#{violation.id}</h4>
                                    <p>{violation.vehicle_id}</p>
                                </div>
                                <div className="violation-status">
                                    <span
                                        className="status-badge"
                                        style={{ backgroundColor: getStatusColor(violation.status) }}
                                    >
                                        {violation.status.toUpperCase()}
                                    </span>
                                </div>
                            </div>

                            <div className="violation-details">
                                <p><strong>Type:</strong> {violation.violation_type.replace('_', ' ')}</p>
                                <p><strong>Location:</strong> {violation.location}</p>
                                <p><strong>Time:</strong> {new Date(violation.timestamp).toLocaleString()}</p>
                                <p><strong>Fine:</strong> ₹{violation.fine_amount}</p>
                            </div>

                            {violation.status === 'pending' && (
                                <div className="quick-actions">
                                    <button
                                        className="btn-approve"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleViolationAction(violation.id, 'approved');
                                        }}
                                    >
                                        ✅ Approve
                                    </button>
                                    <button
                                        className="btn-reject"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleViolationAction(violation.id, 'rejected');
                                        }}
                                    >
                                        ❌ Reject
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {selectedViolation && (
                    <div className="violation-detail-panel">
                        <div className="detail-header">
                            <h3>Violation Details #{selectedViolation.id}</h3>
                            <button onClick={() => setSelectedViolation(null)}>✕</button>
                        </div>

                        <div className="detail-content">
                            {/* Evidence Section */}
                            <div className="evidence-section">
                                <h4>Evidence</h4>
                                {selectedViolation.evidence?.photo && (
                                    <div className="evidence-item">
                                        <img
                                            src={`/evidence/${selectedViolation.evidence.photo}`}
                                            alt="Violation Evidence"
                                            className="evidence-photo"
                                            onError={(e) => {
                                                e.target.src = '/placeholder-evidence.jpg';
                                            }}
                                        />
                                        <p>Confidence: {Math.round(selectedViolation.evidence.confidence * 100)}%</p>
                                    </div>
                                )}
                            </div>

                            {/* Violation Info */}
                            <div className="info-section">
                                <h4>Violation Information</h4>
                                <div className="info-grid">
                                    <div>
                                        <label>Vehicle ID:</label>
                                        <span>{selectedViolation.vehicle_id}</span>
                                    </div>
                                    <div>
                                        <label>Driver License:</label>
                                        <span>{selectedViolation.driver_license || 'Unknown'}</span>
                                    </div>
                                    <div>
                                        <label>Violation Type:</label>
                                        <span>{selectedViolation.violation_type.replace('_', ' ')}</span>
                                    </div>
                                    <div>
                                        <label>Location:</label>
                                        <span>{selectedViolation.location}</span>
                                    </div>
                                    <div>
                                        <label>Date & Time:</label>
                                        <span>{new Date(selectedViolation.timestamp).toLocaleString()}</span>
                                    </div>
                                    <div>
                                        <label>Fine Amount:</label>
                                        <span style={{ color: getSeverityColor(selectedViolation.fine_amount) }}>
                                            ₹{selectedViolation.fine_amount}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Speed Info (if applicable) */}
                            {selectedViolation.speed && (
                                <div className="speed-section">
                                    <h4>Speed Information</h4>
                                    <p><strong>Recorded Speed:</strong> {selectedViolation.speed} km/h</p>
                                    <p><strong>Speed Limit:</strong> {selectedViolation.speed_limit} km/h</p>
                                    <p><strong>Excess Speed:</strong> {(selectedViolation.speed - selectedViolation.speed_limit).toFixed(1)} km/h</p>
                                </div>
                            )}

                            {/* Officer Notes */}
                            <div className="notes-section">
                                <h4>Officer Notes</h4>
                                <textarea
                                    rows="3"
                                    placeholder="Add notes about this violation..."
                                    defaultValue={selectedViolation.officer_notes}
                                    id={`notes-${selectedViolation.id}`}
                                />
                            </div>

                            {/* Actions */}
                            {selectedViolation.status === 'pending' && (
                                <div className="detail-actions">
                                    <button
                                        className="btn-approve-detailed"
                                        onClick={() => {
                                            const notes = document.getElementById(`notes-${selectedViolation.id}`).value;
                                            handleViolationAction(selectedViolation.id, 'approved', notes);
                                        }}
                                    >
                                        ✅ Approve Violation
                                    </button>
                                    <button
                                        className="btn-reject-detailed"
                                        onClick={() => {
                                            const notes = document.getElementById(`notes-${selectedViolation.id}`).value;
                                            handleViolationAction(selectedViolation.id, 'rejected', notes);
                                        }}
                                    >
                                        ❌ Reject Violation
                                    </button>
                                    <button
                                        className="btn-review"
                                        onClick={() => {
                                            const notes = document.getElementById(`notes-${selectedViolation.id}`).value;
                                            handleViolationAction(selectedViolation.id, 'under_review', notes);
                                        }}
                                    >
                                        🔍 Mark for Review
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Violations;
