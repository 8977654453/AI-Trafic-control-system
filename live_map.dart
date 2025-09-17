// Flutter Widget for User Live Traffic Map
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

class LiveMapView extends StatefulWidget {
  @override
  _LiveMapViewState createState() => _LiveMapViewState();
}

class _LiveMapViewState extends State<LiveMapView> {
  MapController mapController = MapController();
  List<Marker> junctionMarkers = [];
  Timer? updateTimer;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    loadTrafficData();

    // Update every 30 seconds
    updateTimer = Timer.periodic(Duration(seconds: 30), (timer) {
      loadTrafficData();
    });
  }

  @override
  void dispose() {
    updateTimer?.cancel();
    super.dispose();
  }

  Future<void> loadTrafficData() async {
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/api/traffic/current'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        updateJunctionMarkers(data['junctions']);
        setState(() {
          isLoading = false;
        });
      }
    } catch (e) {
      print('Error loading traffic data: $e');
      setState(() {
        isLoading = false;
      });
    }
  }

  void updateJunctionMarkers(Map<String, dynamic> junctions) {
    List<Marker> newMarkers = [];

    junctions.forEach((junctionId, data) {
      LatLng position = getJunctionPosition(junctionId);
      Color markerColor = getTrafficColor(data['status']);

      newMarkers.add(
        Marker(
          point: position,
          width: 60,
          height: 60,
          builder: (context) => GestureDetector(
            onTap: () => showJunctionDetails(junctionId, data),
            child: Container(
              decoration: BoxDecoration(
                color: markerColor,
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 2),
                boxShadow: [
                  BoxShadow(
                    color: markerColor.withOpacity(0.5),
                    blurRadius: 10,
                    spreadRadius: 2,
                  ),
                ],
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.traffic,
                    color: Colors.white,
                    size: 20,
                  ),
                  Text(
                    junctionId,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 8,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    });

    setState(() {
      junctionMarkers = newMarkers;
    });
  }

  LatLng getJunctionPosition(String junctionId) {
    // Map junction IDs to Bangalore coordinates
    Map<String, LatLng> positions = {
      'J0': LatLng(12.9716, 77.5946), // Central Bangalore
      'J1': LatLng(12.9750, 77.6000),
      'J2': LatLng(12.9680, 77.5900),
      'J3': LatLng(12.9800, 77.5950),
      'J4': LatLng(12.9650, 77.6050),
    };
    return positions[junctionId] ?? LatLng(12.9716, 77.5946);
  }

  Color getTrafficColor(String status) {
    switch (status) {
      case 'normal':
        return Colors.green;
      case 'moderate':
        return Colors.orange;
      case 'congested':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  void showJunctionDetails(String junctionId, Map<String, dynamic> data) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.4,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Junction $junctionId',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: Icon(Icons.close),
                ),
              ],
            ),
            SizedBox(height: 20),
            _buildInfoRow('Status', data['status'].toString().toUpperCase()),
            _buildInfoRow('Vehicles', '${data['vehicles']}'),
            _buildInfoRow('Avg Speed', '${data['avg_speed']?.toStringAsFixed(1) ?? 'N/A'} km/h'),
            _buildInfoRow('Waiting Time', '${data['waiting_time']?.toStringAsFixed(1) ?? 'N/A'}s'),
            SizedBox(height: 20),
            Container(
              width: double.infinity,
              height: 50,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.pop(context);
                  // Navigate to route planner with this junction
                },
                icon: Icon(Icons.directions),
                label: Text('Plan Route from Here'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(25),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Live Traffic Map'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            onPressed: loadTrafficData,
            icon: Icon(Icons.refresh),
          ),
        ],
      ),
      body: Stack(
        children: [
          FlutterMap(
            mapController: mapController,
            options: MapOptions(
              center: LatLng(12.9716, 77.5946), // Bangalore center
              zoom: 13.0,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                subdomains: ['a', 'b', 'c'],
              ),
              MarkerLayer(markers: junctionMarkers),
            ],
          ),

          // Legend
          Positioned(
            top: 20,
            right: 20,
            child: Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black26,
                    blurRadius: 5,
                    offset: Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Traffic Status',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                  SizedBox(height: 8),
                  _buildLegendItem(Colors.green, 'Normal'),
                  _buildLegendItem(Colors.orange, 'Moderate'),
                  _buildLegendItem(Colors.red, 'Congested'),
                ],
              ),
            ),
          ),

          // Loading indicator
          if (isLoading)
            Center(
              child: Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('Loading traffic data...'),
                  ],
                ),
              ),
            ),
        ],
      ),

      // Floating Action Button for current location
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          mapController.move(LatLng(12.9716, 77.5946), 13.0);
        },
        child: Icon(Icons.my_location),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
    );
  }

  Widget _buildLegendItem(Color color, String label) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(fontSize: 10),
          ),
        ],
      ),
    );
  }
}
