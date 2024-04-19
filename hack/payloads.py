import folium
import openrouteservice as ors
import math

# Example coordinates and service times
coords = [
    {'location': [-87.7898440, 41.8879786], 'service': 1 * 60 * 60},
    {'location': [-87.7808524, 41.8906422], 'service': 0.5 * 60 * 60},
    {'location': [-87.7895149, 41.8933762], 'service': 1 * 60 * 60},
    {'location': [-87.7552925, 41.8809087], 'service': 6 * 60 * 60},
    {'location': [-87.7728134, 41.8804058], 'service': 1 * 60 * 60},
    {'location': [-87.7702890, 41.8802231], 'service': 1 * 60 * 60},
    {'location': [-87.7787924, 41.8944518], 'service': 1 * 60 * 60},
    {'location': [-87.7732345, 41.8770663], 'service': 0.25 * 60 * 60},
]

# Example start locations for two vehicles
vehicle_starts = [
    [-87.718686, 41.876678],
    [-87.718686, 41.860007]  # Adjust the start location for the second vehicle as needed
]

# Capacity of each vehicle
vehicle_capacity = 10

# Initialize the map
m = folium.Map(location=list(reversed([-87.787984, 41.8871616])), tiles="cartodbpositron", zoom_start=14)

# Add markers for vehicle start locations
for start in vehicle_starts:
    folium.Marker(location=list(reversed(start)), icon=folium.Icon(color="red")).add_to(m)

# Create two vehicles with capacity constraints and time windows
vehicles = [
    ors.optimization.Vehicle(id=0, profile='driving-car', start=start, end=start,
                             capacity=[vehicle_capacity], time_window=[0, 8 * 60 * 60]),
    ors.optimization.Vehicle(id=1, profile='driving-car', start=start, end=start,
                             capacity=[vehicle_capacity], time_window=[0, 8 * 60 * 60])
]

# Calculate total demand
total_demand = sum(job['service'] for job in coords)

# Calculate payload per vehicle
payload_per_vehicle = total_demand / len(vehicles)

# Assign jobs to vehicles based on payload
vehicle_jobs = [[] for _ in range(len(vehicles))]
current_payloads = [0] * len(vehicles)
for job in sorted(coords, key=lambda x: x['service'], reverse=True):
    min_payload_index = current_payloads.index(min(current_payloads))
    if current_payloads[min_payload_index] + job['service'] <= payload_per_vehicle:
        vehicle_jobs[min_payload_index].append(job)
        current_payloads[min_payload_index] += job['service']

# Create jobs with locations and service times for each vehicle
all_jobs = []
for i, jobs in enumerate(vehicle_jobs):
    for index, job in enumerate(jobs):
        # Generate a unique job ID using a combination of vehicle ID, index, and a unique identifier
        job_id = f"vehicle_{i}_job_{index}"
        all_jobs.append(ors.optimization.Job(id=job_id, **job))

# Initialize the client with your OpenRouteService API key
ors_client = ors.Client(key='5b3ce3597851110001cf6248fc08c57f856040f788312ce74ae6d260')

# Make optimization request
optimized = ors_client.optimization(jobs=all_jobs, vehicles=vehicles, geometry=True)

# Define line colors for different routes
line_colors = ['green', 'orange', 'blue', 'yellow']

# Plot optimized routes and job locations on the map
for route in optimized['routes']:
    # Plot route polyline
    folium.PolyLine(
        locations=[list(reversed(coords)) for coords in ors.convert.decode_polyline(route['geometry'])['coordinates']],
        color=line_colors[route['vehicle']]).add_to(m)

    # Add markers for job locations
    for step in route['steps']:
        if step['type'] == 'job':
            folium.Marker(location=list(reversed(step['location'])),
                          popup=f"Arrival time: {math.floor(step['arrival'] / (60 * 60))} hours {math.floor((step['arrival'] % (60 * 60)) / 60)} minutes",
                          icon=folium.Icon(color=line_colors[route['vehicle']])).add_to(m)

# Save the map to an HTML file
m.save("optimized_routes_with_capacity_balanced.html")
