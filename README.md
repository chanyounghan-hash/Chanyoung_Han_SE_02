# City Road Network Algorithm Comparison

## Problem Description

This project analyzes and compares the performance of Dijkstra’s algorithm and A* search on real-world urban road networks. The road networks are obtained from OpenStreetMap using OSMnx and represented as graphs.

Two cities with different structural layouts are selected:

- Madrid, Spain (organic, web-like structure)
- Manhattan, New York City (grid-based structure)

The goal is to evaluate how search algorithms behave under different urban network topologies.

## Applied Algorithms

This project applies:

- Dijkstra’s Algorithm  
- A* Search Algorithm  

Both algorithms compute the shortest path between two nodes in a graph.

Dijkstra’s algorithm explores nodes based only on accumulated path cost. In contrast, A* improves efficiency by incorporating a heuristic that estimates the remaining distance to the goal.

In this implementation:

- Edge weight = **road length (`length`)**
- A* heuristic = **Euclidean (straight-line) distance**

Since the graph is projected into a metric coordinate system, the heuristic is measured in meters and is admissible. Therefore, A* guarantees optimal solutions while typically exploring fewer nodes than Dijkstra.

## Data and Tools

The project uses:

- Python  
- OSMnx  
- NetworkX  
- Matplotlib  
- Pandas  
- NumPy  
- OpenStreetMap road network data  

The implementation is based on concepts and examples from the OSMnx examples repository:

https://github.com/gboeing/osmnx-examples

## Method

For each city, the following steps are performed:

1. Download the road network using OSMnx  
2. Extract the largest strongly connected component  
3. Project the graph to a coordinate system (meters)  
4. Randomly sample node pairs  
5. Filter routes by straight-line distance (3000m–5000m)  
6. Compute shortest paths using:
   - Dijkstra (weight = length)
   - A* (weight = length, heuristic = Euclidean distance)
7. Measure:
   - Runtime
   - Total path length
   - Number of successful routes  

Each city is evaluated over 50 valid routes.

## Visualization

The program generates route visualizations for each city:

- `madrid_dijkstra.png`
- `madrid_astar.png`
- `manhattan_dijkstra.png`
- `manhattan_astar.png`

Each image shows multiple sampled routes:

- Dijkstra → blue  
- A* → red  

There is also an optional visualization block (currently commented out) that overlays both algorithms in a single image:

```python
# All algorithms
# fig, ax = ox.plot_graph_routes(
#     G_proj,
#     all_routes,
#     route_colors=colors,
#     route_linewidth=widths,
#     node_size=0,
#     show=False,
#     close=False
# )
