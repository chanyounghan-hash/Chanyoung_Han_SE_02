import osmnx as ox
import networkx as nx
import time
import matplotlib.pyplot as plt
import pandas as pd
import random
import numpy as np

# Set fixed seed for reproducibility
random.seed(42)
np.random.seed(42)

def get_heuristic(G):
    def heuristic(u, v):
        return get_straight_line_dist(G, u, v)
    return heuristic

def get_straight_line_dist(G, u, v):
    """Calculates Euclidean distance between two nodes in a projected graph."""
    pos_u = G.nodes[u]
    pos_v = G.nodes[v]
    return ((pos_u['x'] - pos_v['x'])**2 + (pos_u['y'] - pos_v['y'])**2)**0.5

def compare_city_algorithms(city_name, place_query, num_routes=50, target_dist_min=4000, target_dist_max=6000):
    print(f"\n--- Fair Comparison for {city_name} ---")
    
    # 1. Load and project the graph
    print(f"Loading graph for {city_name}...")
    try:
        G = ox.graph_from_place(place_query, network_type="drive")
        G = ox.truncate.largest_component(G, strongly=True)
        G_proj = ox.project_graph(G)
        
        print(f"Graph loaded: {len(G_proj.nodes())} nodes, {len(G_proj.edges())} edges.")
    except Exception as e:
        print(f"Error loading graph for {city_name}: {e}")
        return [], None

    nodes = list(G_proj.nodes())
    results = []
    routes_found = 0
    attempts = 0
    max_attempts = num_routes * 200 # Avoid infinite loops
    
    heuristic_func = get_heuristic(G_proj)
    
    # Track routes for visualization
    sample_routes_astar = []
    sample_routes_dijkstra = []
    
    print(f"Sampling {num_routes} routes with straight-line distance between {target_dist_min}m and {target_dist_max}m...")
    
    while routes_found < num_routes and attempts < max_attempts:
        attempts += 1
        u, v = random.sample(nodes, 2)
        
        sl_dist = get_straight_line_dist(G_proj, u, v)
        
        if target_dist_min <= sl_dist <= target_dist_max:
            try:
                # Check if path exists and run Dijkstra
                start_d = time.perf_counter()
                d_path = nx.dijkstra_path(G_proj, u, v, weight="length")
                d_time = time.perf_counter() - start_d
                d_length = nx.dijkstra_path_length(G_proj, u, v, weight="length")
                
                # Run A*
                start_a = time.perf_counter()
                a_path = nx.astar_path(G_proj, u, v, heuristic=heuristic_func, weight="length")
                a_time = time.perf_counter() - start_a
                a_length = nx.astar_path_length(G_proj, u, v, heuristic=heuristic_func, weight="length")
                
                results.append({
                    "city": city_name,
                    "route_number": routes_found + 1,
                    "start_node": u,
                    "end_node": v,
                    "straight_line_distance": sl_dist,
                    "dijkstra_runtime": d_time,
                    "astar_runtime": a_time,
                    "dijkstra_total_length": d_length,
                    "astar_total_length": a_length
                })
                
                # Save all routes for visualization
                sample_routes_astar.append(a_path)
                sample_routes_dijkstra.append(d_path)
                
                routes_found += 1
                if routes_found % 10 == 0:
                    print(f"  Found {routes_found}/{num_routes} routes...")
                    
            except nx.NetworkXNoPath:
                continue
            except Exception as e:
                # print(f"Error finding path: {e}")
                continue

    if routes_found < num_routes:
        print(f"Warning: Only found {routes_found} routes for {city_name} after {attempts} attempts.")

    # Visualization
    if sample_routes_astar and sample_routes_dijkstra:
        print(f"Saving visualization for {city_name}...")

        # Plot Dijkstra routes first (blue)
        # Then plot A* routes (red) with a thinner line to see both if they overlap
        # Or Dijkstra (blue) thicker, A* (red) thinner.
        all_routes = sample_routes_dijkstra + sample_routes_astar
        colors = ['b'] * len(sample_routes_dijkstra) + ['r'] * len(sample_routes_astar)
        widths = [4] * len(sample_routes_dijkstra) + [1.5] * len(sample_routes_astar)
    
    # All algorithms
    #    fig, ax = ox.plot_graph_routes(
    #        G_proj,
    #        all_routes,
    #        route_colors=colors,
    #        route_linewidth=widths,
    #        node_size=0,
    #        show=False,
    #        close=False
    #    )

    #    ax.set_title(f"{city_name}: A* (red, thin) vs Dijkstra (blue, thick)")
    #    plt.savefig(f"{city_name.lower().replace(' ', '_')}_comparison.png", dpi=300)
    #    plt.close()
    
    # Dijkstra only
    fig, ax = ox.plot_graph_routes(
        G_proj,
        sample_routes_dijkstra,
        route_colors=['b'] * len(sample_routes_dijkstra),
        route_linewidth=3,
        node_size=0,
        show=False,
        close=False
    )
    ax.set_title(f"{city_name}: Dijkstra routes")
    plt.savefig(f"{city_name.lower().replace(' ', '_')}_dijkstra.png", dpi=300)
    plt.close()

    # A* only
    fig, ax = ox.plot_graph_routes(
        G_proj,
        sample_routes_astar,
        route_colors=['r'] * len(sample_routes_astar),
        route_linewidth=3,
        node_size=0,
        show=False,
        close=False
    )
    ax.set_title(f"{city_name}: A* routes")
    plt.savefig(f"{city_name.lower().replace(' ', '_')}_astar.png", dpi=300)
    plt.close()
    return results, G_proj

if __name__ == "__main__":
    all_results = []
    
    # Define cities and queries
    cities = [
        ("Madrid", "Madrid, Spain"),
        ("Manhattan", "Manhattan, New York City, New York, USA")
    ]
    
    # Target distance range in meters
    T_MIN = 3000
    T_MAX = 5000
    
    for city_name, query in cities:
        city_results, _ = compare_city_algorithms(city_name, query, num_routes=50, target_dist_min=T_MIN, target_dist_max=T_MAX)
        all_results.extend(city_results)
    
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv("comparison_results.csv", index=False)
        print("\nRaw results saved to 'comparison_results.csv'.")
        
        # Summary Table
        summary = df.groupby('city').agg({
            'dijkstra_runtime': 'mean',
            'astar_runtime': 'mean',
            'dijkstra_total_length': 'mean',
            'route_number': 'count'
        }).rename(columns={
            'dijkstra_runtime': 'Avg Dijkstra Time (s)',
            'astar_runtime': 'Avg A* Time (s)',
            'dijkstra_total_length': 'Avg Total Length',
            'route_number': 'Successful Routes'
        })
        
        print("\n--- Summary Table ---")
        print(summary.to_string())
        
        # Calculate speedup
        summary['Speedup (A*)'] = summary['Avg Dijkstra Time (s)'] / summary['Avg A* Time (s)']
        print("\n--- Average Speedup (Dijkstra / A*) ---")
        print(summary[['Speedup (A*)']])
        
        print("\nVisualizations saved as PNG files.")
    else:
        print("No results generated.")

