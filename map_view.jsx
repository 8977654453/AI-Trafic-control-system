// React Component for Live Traffic Map View
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const MapView = () => {
    const [junctions, setJunctions] = useState([]);
    const [vehicles, setVehicles] = useState([]);
    const [selectedJunction, setSelectedJunction] = useState(null);

    useEffect(() => {
        // Fetch junction data
        fetchJunctionData();
        fetchVehicleData();

        // Setup real-time updates
        const interval = setInterval(() => {
            fetchJunctionData();
            fetchVehicleData();
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    const fetchJunctionData = async () => {
        try {
            const response = await fetch('/api/telemetry/junctions');
            const data = await response.json();

            const junctionArray = Object.entries(data).map(([id, info]) => ({
                id,
                position: getJunctionPosition(id),
                ...info
            }));

            setJunctions(junctionArray);
        } catch (error) {
            console.error('Error fetching junction data:', error);
        }
    };

    const fetchVehicleData = async () => {
        try {
            const response = await fetch('/api/telemetry/vehicles');
            const data = await response.json();
            setVehicles(data);
        } catch (error) {
            console.error('Error fetching vehicle data:', error);
        }
    };

    const getJunctionPosition = (junctionId) => {
        // Map junction IDs to coordinates (Bangalore area)
        const positions = {
            'J0': [12.9716, 77.5946],  // Central Bangalore
            'J1': [12.9750, 77.6000],
            'J2': [12.9680, 77.5900],
            'J3': [12.9800, 77.5950],
            'J4': [12.9650, 77.6050]
        };
        return positions[junctionId] || [12.9716, 77.5946];
    };

    const getJunctionColor = (efficiency) => {
        if (efficiency >= 85) return '#4CAF50';      // Green
        if (efficiency >= 70) return '#FF9800';      // Orange  
        return '#F44336';                            // Red
    };

    const handleJunctionClick = (junction) => {
        setSelectedJunction(junction);
    };

    return (
        <div style={{ height: '100vh', width: '100%' }}>
            <MapContainer
                center={[12.9716, 77.5946]}
                zoom={13}
                style={{ height: '100%', width: '100%' }}
            >
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; OpenStreetMap contributors'
                />

                {/* Junction Markers */}
                {junctions.map((junction) => (
                    <React.Fragment key={junction.id}>
                        <Marker
                            position={junction.position}
                            eventHandlers={{
                                click: () => handleJunctionClick(junction)
                            }}
                        >
                            <Popup>
                                <div>
                                    <h3>{junction.id}</h3>
                                    <p>Vehicles: {junction.vehicles_count}</p>
                                    <p>Avg Speed: {junction.avg_speed.toFixed(1)} km/h</p>
                                    <p>Efficiency: {junction.efficiency.toFixed(1)}%</p>
                                    <p>Waiting Time: {junction.waiting_time.toFixed(1)}s</p>
                                </div>
                            </Popup>
                        </Marker>

                        {/* Traffic density circle */}
                        <Circle
                            center={junction.position}
                            radius={junction.vehicles_count * 10}
                            color={getJunctionColor(junction.efficiency)}
                            fillColor={getJunctionColor(junction.efficiency)}
                            fillOpacity={0.3}
                        />
                    </React.Fragment>
                ))}

                {/* Vehicle Markers */}
                {vehicles.map((vehicle) => (
                    <Marker
                        key={vehicle.id}
                        position={[vehicle.position.y / 1000 + 12.9716, vehicle.position.x / 1000 + 77.5946]}
                        icon={getVehicleIcon(vehicle.type)}
                    >
                        <Popup>
                            <div>
                                <h4>{vehicle.id}</h4>
                                <p>Type: {vehicle.type}</p>
                                <p>Speed: {vehicle.speed.toFixed(1)} km/h</p>
                                {vehicle.type === 'ambulance' && (
                                    <p style={{ color: 'red', fontWeight: 'bold' }}>
                                        🚨 EMERGENCY VEHICLE
                                    </p>
                                )}
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>

            {/* Junction Details Panel */}
            {selectedJunction && (
                <div style={{
                    position: 'absolute',
                    top: 20,
                    right: 20,
                    width: 300,
                    backgroundColor: 'white',
                    padding: 20,
                    borderRadius: 10,
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                    zIndex: 1000
                }}>
                    <h3>Junction {selectedJunction.id}</h3>
                    <div style={{ marginTop: 15 }}>
                        <p><strong>Vehicles:</strong> {selectedJunction.vehicles_count}</p>
                        <p><strong>Average Speed:</strong> {selectedJunction.avg_speed.toFixed(1)} km/h</p>
                        <p><strong>Queue Length:</strong> {selectedJunction.queue_length}</p>
                        <p><strong>Waiting Time:</strong> {selectedJunction.waiting_time.toFixed(1)}s</p>
                        <p><strong>Efficiency:</strong> {selectedJunction.efficiency.toFixed(1)}%</p>
                        <p><strong>Green Duration:</strong> {selectedJunction.green_duration}s</p>
                    </div>
                    <button
                        onClick={() => setSelectedJunction(null)}
                        style={{
                            marginTop: 15,
                            padding: '8px 16px',
                            backgroundColor: '#f44336',
                            color: 'white',
                            border: 'none',
                            borderRadius: 4,
                            cursor: 'pointer'
                        }}
                    >
                        Close
                    </button>
                </div>
            )}
        </div>
    );
};

const getVehicleIcon = (vehicleType) => {
    // Would return appropriate Leaflet icons for different vehicle types
    return null; // Simplified for demo
};

export default MapView;
