from openrouteservice import client
import folium
import openrouteservice as ors
import math
# Simple single route optimization
coords = [
    [-87.7898440, 41.8879786],
    [-87.7808524, 41.8906422],
    [-87.7895149, 41.8933762],
    [-87.7552925, 41.8809087],
    [-87.7728134, 41.8804058],
    [-87.7702890, 41.8802231],
    [-87.7787924, 41.8944518],
    [-87.7732345, 41.8770663],
]
# visualize the points on a map
m = folium.Map(location=list(reversed([-87.787984, 41.8871616])), tiles="cartodbpositron", zoom_start=14)
for coord in coords:
    folium.Marker(location=list(reversed(coord))).add_to(m)

vehicle_start = [-87.800701, 41.876214]
m = folium.Map(location=list(reversed([-87.787984, 41.8871616])), tiles="cartodbpositron", zoom_start=14)

folium.Marker(location=list(reversed(vehicle_start)), icon=folium.Icon(color="red")).add_to(m)

vehicles = [
    ors.optimization.Vehicle(id=0, profile='driving-car', start=vehicle_start, end=vehicle_start, capacity=[5]),
    ors.optimization.Vehicle(id=1, profile='driving-car', start=vehicle_start, end=vehicle_start, capacity=[5])
]

# Initialize the client with your API key
ors_client = ors.Client(key='5b3ce3597851110001cf6248fc08c57f856040f788312ce74ae6d260')

# Create jobs
jobs = [ors.optimization.Job(id=index, location=coords, amount=[1]) for index, coords in enumerate(coords)]

# Make optimization request
optimized = ors_client.optimization(jobs=jobs, vehicles=vehicles, geometry=True)
line_colors = ['green', 'orange', 'blue', 'yellow']
for route in optimized['routes']:
    folium.PolyLine(locations=[list(reversed(coords)) for coords in ors.convert.decode_polyline(route['geometry'])['coordinates']], color=line_colors[route['vehicle']]).add_to(m)
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
vehicle_start = [-87.718686, 41.876678]
m = folium.Map(location=list(reversed([-87.787984, 41.8871616])), tiles="cartodbpositron", zoom_start=14)

folium.Marker(location=list(reversed(vehicle_start)), icon=folium.Icon(color="red")).add_to(m)

vehicles = [
    ors.optimization.Vehicle(id=0, profile='driving-car', start=vehicle_start, end=vehicle_start,
                             time_window=[0, 8 * 60 * 60]),
    ors.optimization.Vehicle(id=1, profile='driving-car', start=vehicle_start, end=vehicle_start,
                             time_window=[0, 8 * 60 * 60])
]
jobs = [ors.optimization.Job(id=index, **job) for index, job in enumerate(coords)]
optimized = ors_client.optimization(jobs=jobs, vehicles=vehicles, geometry=True)
line_colors = ['green', 'orange', 'blue', 'yellow']
for route in optimized['routes']:
    folium.PolyLine(
        locations=[list(reversed(coords)) for coords in ors.convert.decode_polyline(route['geometry'])['coordinates']],
        color=line_colors[route['vehicle']]).add_to(m)
    for step in route['steps']:
        if not step['type'] == 'job':
            continue
        folium.Marker(location=list(reversed(step['location'])),
                      popup=f"Arrival time: {math.floor(step['arrival'] / (60 * 60))} hours {math.floor((step['arrival'] % (60 * 60)) / 60)} minutes",
                      icon=folium.Icon(color=line_colors[route['vehicle']])).add_to(m)
m.save("map.html")