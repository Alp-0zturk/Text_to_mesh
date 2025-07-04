import numpy as np
import torch
import trimesh
from scipy.spatial.distance import cdist
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import networkx as nx
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings("ignore")

class MeshAnalyzer:
    """
    Advanced mesh analysis and segmentation system for identifying semantic regions
    in generated 3D meshes based on geometric and topological features.
    """
    
    def __init__(self, device='cpu'):
        self.device = device
        
        # Predefined semantic categories with their geometric characteristics
        self.semantic_categories = {
            'water': {
                'height_range': (0.0, 0.2),  # Typically low areas
                'flatness_threshold': 0.1,   # Very flat surfaces
                'color': np.array([0.2, 0.6, 1.0]),  # Blue
                'clustering_weight': 2.0
            },
            'terrain': {
                'height_range': (0.1, 0.8),  # Mid-level areas
                'flatness_threshold': 0.5,   # Moderately flat
                'color': np.array([0.6, 0.4, 0.2]),  # Brown
                'clustering_weight': 1.0
            },
            'vegetation': {
                'height_range': (0.2, 0.9),  # Various heights
                'flatness_threshold': 0.7,   # Can be uneven
                'color': np.array([0.2, 0.8, 0.3]),  # Green
                'clustering_weight': 1.5
            },
            'rocks': {
                'height_range': (0.3, 1.0),  # Higher areas
                'flatness_threshold': 0.9,   # Very uneven
                'color': np.array([0.5, 0.5, 0.5]),  # Gray
                'clustering_weight': 1.2
            },
            'snow': {
                'height_range': (0.7, 1.0),  # High altitude
                'flatness_threshold': 0.3,   # Relatively flat
                'color': np.array([0.9, 0.9, 1.0]),  # White-blue
                'clustering_weight': 1.1
            }
        }
    
    def analyze_mesh(self, mesh, text_description: str = "") -> Dict:
        """
        Perform comprehensive mesh analysis to identify semantic regions.
        
        Args:
            mesh: TriMesh object from Shap-E
            text_description: Original text description for context
        
        Returns:
            Dictionary containing segmentation results and features
        """
        print("\n🔍 Starting mesh analysis...")
        
        # Extract geometric features
        geometric_features = self._extract_geometric_features(mesh)
        
        # Extract topological features
        topological_features = self._extract_topological_features(mesh)
        
        # Combine features for clustering
        combined_features = self._combine_features(geometric_features, topological_features)
        
        # Perform semantic segmentation
        segmentation_results = self._perform_segmentation(
            mesh, combined_features, text_description
        )
        
        # Refine segmentation using post-processing
        refined_segmentation = self._refine_segmentation(
            mesh, segmentation_results, combined_features
        )
        
        print(f"✅ Analysis complete! Found {len(np.unique(refined_segmentation['labels']))} semantic regions")
        
        return {
            'geometric_features': geometric_features,
            'topological_features': topological_features,
            'combined_features': combined_features,
            'segmentation': refined_segmentation,
            'semantic_mapping': self._create_semantic_mapping(refined_segmentation, text_description)
        }
    
    def _extract_geometric_features(self, mesh) -> Dict[str, np.ndarray]:
        """Extract geometric features from mesh vertices."""
        print("  📐 Extracting geometric features...")
        
        vertices = mesh.verts if hasattr(mesh, 'verts') else mesh.vertices
        faces = mesh.faces
        
        # Height-based features
        z_coords = vertices[:, 2]
        z_normalized = (z_coords - z_coords.min()) / (z_coords.max() - z_coords.min() + 1e-8)
        
        # Local curvature estimation
        curvature = self._estimate_curvature(vertices, faces)
        
        # Surface normal variation (roughness)
        normals = self._compute_vertex_normals(vertices, faces)
        roughness = self._compute_roughness(vertices, normals, k=8)
        
        # Local density (vertex clustering)
        density = self._compute_local_density(vertices, k=10)
        
        # Slope analysis
        slopes = self._compute_slopes(vertices, faces)
        
        # Distance from mesh center
        center = np.mean(vertices, axis=0)
        distances_from_center = np.linalg.norm(vertices - center, axis=1)
        distances_normalized = distances_from_center / (distances_from_center.max() + 1e-8)
        
        return {
            'height': z_normalized,
            'curvature': curvature,
            'roughness': roughness,
            'density': density,
            'slopes': slopes,
            'distance_from_center': distances_normalized,
            'normals': normals
        }
    
    def _extract_topological_features(self, mesh) -> Dict[str, np.ndarray]:
        """Extract topological features from mesh connectivity."""
        print("  🕸️  Extracting topological features...")
        
        vertices = mesh.verts if hasattr(mesh, 'verts') else mesh.vertices
        faces = mesh.faces
        
        # Build adjacency graph
        adjacency_graph = self._build_adjacency_graph(vertices, faces)
        
        # Compute connectivity features
        connectivity_features = self._compute_connectivity_features(adjacency_graph)
        
        # Compute geodesic distances to boundary
        boundary_distances = self._compute_boundary_distances(vertices, faces)
        
        return {
            'vertex_degree': connectivity_features['degrees'],
            'clustering_coefficient': connectivity_features['clustering'],
            'boundary_distance': boundary_distances,
            'connectivity_graph': adjacency_graph
        }
    
    def _combine_features(self, geometric_features: Dict, topological_features: Dict) -> np.ndarray:
        """Combine all features into a unified feature matrix."""
        print("  🔗 Combining features...")
        
        feature_list = []
        
        # Add geometric features
        for key, values in geometric_features.items():
            if key != 'normals' and len(values.shape) == 1:  # Skip normals and multi-dimensional features
                feature_list.append(values.reshape(-1, 1))
        
        # Add topological features
        for key, values in topological_features.items():
            if key != 'connectivity_graph' and len(values.shape) == 1:
                feature_list.append(values.reshape(-1, 1))
        
        # Combine and normalize
        combined = np.hstack(feature_list)
        
        # Standardize features
        scaler = StandardScaler()
        combined_normalized = scaler.fit_transform(combined)
        
        return combined_normalized
    
    def _perform_segmentation(self, mesh, features: np.ndarray, text_description: str) -> Dict:
        """Perform multi-scale segmentation using various clustering methods."""
        print("  🎯 Performing semantic segmentation...")
        
        vertices = mesh.verts if hasattr(mesh, 'verts') else mesh.vertices
        
        # Determine number of expected clusters based on text description
        expected_clusters = self._estimate_cluster_count(text_description)
        
        # Multi-scale clustering
        results = {}
        
        # 1. K-means clustering
        kmeans = KMeans(n_clusters=expected_clusters, random_state=42, n_init=10)
        kmeans_labels = kmeans.fit_predict(features)
        results['kmeans'] = kmeans_labels
        
        # 2. DBSCAN for density-based clustering
        eps = self._estimate_eps(features)
        dbscan = DBSCAN(eps=eps, min_samples=max(5, len(vertices) // 100))
        dbscan_labels = dbscan.fit_predict(features)
        results['dbscan'] = dbscan_labels
        
        # 3. Hierarchical clustering
        if len(vertices) < 5000:  # Only for smaller meshes due to computational cost
            linkage_matrix = linkage(features, method='ward')
            hierarchical_labels = fcluster(linkage_matrix, expected_clusters, criterion='maxclust')
            results['hierarchical'] = hierarchical_labels
        
        # 4. Height-based segmentation (for terrain-specific features)
        height_labels = self._height_based_segmentation(vertices, expected_clusters)
        results['height_based'] = height_labels
        
        return results
    
    def _refine_segmentation(self, mesh, segmentation_results: Dict, features: np.ndarray) -> Dict:
        """Refine segmentation by combining different clustering results."""
        print("  ✨ Refining segmentation...")
        
        vertices = mesh.verts if hasattr(mesh, 'verts') else mesh.vertices
        
        # Combine different segmentation results using ensemble method
        all_labels = []
        weights = []
        
        for method, labels in segmentation_results.items():
            if len(np.unique(labels)) > 1:  # Only use valid segmentations
                all_labels.append(labels)
                # Weight different methods based on their effectiveness
                weight = {'kmeans': 1.0, 'dbscan': 1.2, 'hierarchical': 0.8, 'height_based': 1.5}.get(method, 1.0)
                weights.append(weight)
        
        if not all_labels:
            # Fallback to height-based segmentation
            final_labels = self._height_based_segmentation(vertices, 3)
        else:
            # Ensemble voting
            final_labels = self._ensemble_voting(all_labels, weights)
        
        # Post-process to ensure spatial coherence
        final_labels = self._spatial_smoothing(vertices, mesh.faces, final_labels)
        
        return {
            'labels': final_labels,
            'n_clusters': len(np.unique(final_labels)),
            'cluster_sizes': np.bincount(final_labels),
            'individual_results': segmentation_results
        }
    
    def _create_semantic_mapping(self, segmentation: Dict, text_description: str) -> Dict:
        """Map cluster labels to semantic categories based on analysis."""
        print("  🏷️  Creating semantic mapping...")
        
        labels = segmentation['labels']
        n_clusters = segmentation['n_clusters']
        
        # Analyze text description for semantic hints
        text_lower = text_description.lower()
        semantic_hints = {}
        
        for category, properties in self.semantic_categories.items():
            if any(keyword in text_lower for keyword in self._get_category_keywords(category)):
                semantic_hints[category] = properties
        
        # If no specific hints, use default categories
        if not semantic_hints:
            semantic_hints = {
                'terrain': self.semantic_categories['terrain'],
                'vegetation': self.semantic_categories['vegetation'],
                'water': self.semantic_categories['water']
            }
        
        # Map clusters to semantic categories
        mapping = {}
        available_categories = list(semantic_hints.keys())
        
        for cluster_id in range(n_clusters):
            if cluster_id < len(available_categories):
                mapping[cluster_id] = available_categories[cluster_id]
            else:
                # Default to terrain for extra clusters
                mapping[cluster_id] = 'terrain'
        
        return {
            'cluster_to_semantic': mapping,
            'semantic_categories': semantic_hints,
            'available_categories': available_categories
        }
    
    # Helper methods
    def _estimate_curvature(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Estimate mean curvature at each vertex."""
        try:
            mesh_obj = trimesh.Trimesh(vertices=vertices, faces=faces)
            return mesh_obj.vertex_defects
        except:
            # Fallback: simple curvature estimation
            curvature = np.zeros(len(vertices))
            for i, vertex in enumerate(vertices):
                # Find neighboring vertices
                neighbors = self._find_vertex_neighbors(i, faces)
                if len(neighbors) > 2:
                    # Compute local variation
                    neighbor_coords = vertices[neighbors]
                    center = np.mean(neighbor_coords, axis=0)
                    distances = np.linalg.norm(neighbor_coords - center, axis=1)
                    curvature[i] = np.std(distances)
            return curvature
    
    def _compute_vertex_normals(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Compute vertex normals."""
        try:
            mesh_obj = trimesh.Trimesh(vertices=vertices, faces=faces)
            return mesh_obj.vertex_normals
        except:
            # Fallback: simple normal estimation
            normals = np.zeros_like(vertices)
            for i in range(len(vertices)):
                neighbors = self._find_vertex_neighbors(i, faces)
                if len(neighbors) >= 2:
                    # Estimate normal from local surface
                    v1 = vertices[neighbors[0]] - vertices[i]
                    v2 = vertices[neighbors[1]] - vertices[i]
                    normal = np.cross(v1, v2)
                    if np.linalg.norm(normal) > 0:
                        normals[i] = normal / np.linalg.norm(normal)
                    else:
                        normals[i] = np.array([0, 0, 1])  # Default up
                else:
                    normals[i] = np.array([0, 0, 1])
            return normals
    
    def _compute_roughness(self, vertices: np.ndarray, normals: np.ndarray, k: int = 8) -> np.ndarray:
        """Compute local surface roughness."""
        roughness = np.zeros(len(vertices))
        
        for i, vertex in enumerate(vertices):
            # Find k nearest neighbors
            distances = np.linalg.norm(vertices - vertex, axis=1)
            neighbor_indices = np.argsort(distances)[1:k+1]  # Exclude self
            
            if len(neighbor_indices) > 0:
                # Compute normal variation
                neighbor_normals = normals[neighbor_indices]
                current_normal = normals[i]
                
                # Calculate angular differences
                dot_products = np.dot(neighbor_normals, current_normal)
                dot_products = np.clip(dot_products, -1, 1)  # Numerical stability
                angular_diffs = np.arccos(dot_products)
                roughness[i] = np.mean(angular_diffs)
        
        return roughness
    
    def _compute_local_density(self, vertices: np.ndarray, k: int = 10) -> np.ndarray:
        """Compute local vertex density."""
        density = np.zeros(len(vertices))
        
        for i, vertex in enumerate(vertices):
            distances = np.linalg.norm(vertices - vertex, axis=1)
            k_nearest_distances = np.sort(distances)[1:k+1]  # Exclude self
            if len(k_nearest_distances) > 0:
                density[i] = 1.0 / (np.mean(k_nearest_distances) + 1e-8)
        
        return density
    
    def _compute_slopes(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Compute local slope at each vertex."""
        slopes = np.zeros(len(vertices))
        
        for i in range(len(vertices)):
            neighbors = self._find_vertex_neighbors(i, faces)
            if len(neighbors) >= 2:
                # Compute local gradient
                neighbor_coords = vertices[neighbors]
                current_coord = vertices[i]
                
                # Calculate height differences
                height_diffs = neighbor_coords[:, 2] - current_coord[2]
                horizontal_distances = np.linalg.norm(neighbor_coords[:, :2] - current_coord[:2], axis=1)
                
                # Avoid division by zero
                valid_indices = horizontal_distances > 1e-8
                if np.any(valid_indices):
                    local_slopes = np.abs(height_diffs[valid_indices] / horizontal_distances[valid_indices])
                    slopes[i] = np.mean(local_slopes)
        
        return slopes
    
    def _build_adjacency_graph(self, vertices: np.ndarray, faces: np.ndarray) -> nx.Graph:
        """Build adjacency graph from mesh faces."""
        G = nx.Graph()
        G.add_nodes_from(range(len(vertices)))
        
        for face in faces:
            # Add edges between all vertex pairs in the face
            for i in range(3):
                for j in range(i+1, 3):
                    G.add_edge(face[i], face[j])
        
        return G
    
    def _compute_connectivity_features(self, graph: nx.Graph) -> Dict[str, np.ndarray]:
        """Compute graph-based connectivity features."""
        n_vertices = len(graph.nodes())
        
        # Vertex degrees
        degrees = np.array([graph.degree(i) for i in range(n_vertices)])
        
        # Clustering coefficients
        clustering = np.array([nx.clustering(graph, i) for i in range(n_vertices)])
        
        return {
            'degrees': degrees,
            'clustering': clustering
        }
    
    def _compute_boundary_distances(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Compute distance to mesh boundary for each vertex."""
        # Find boundary vertices (vertices with degree < expected for interior vertices)
        vertex_degrees = np.zeros(len(vertices))
        for face in faces:
            for vertex_id in face:
                vertex_degrees[vertex_id] += 1
        
        # Boundary vertices typically have lower degree
        mean_degree = np.mean(vertex_degrees)
        boundary_vertices = np.where(vertex_degrees < mean_degree * 0.7)[0]
        
        if len(boundary_vertices) == 0:
            return np.ones(len(vertices))  # All vertices are equally far from boundary
        
        # Compute distances to nearest boundary vertex
        boundary_coords = vertices[boundary_vertices]
        distances = np.zeros(len(vertices))
        
        for i, vertex in enumerate(vertices):
            if i in boundary_vertices:
                distances[i] = 0.0
            else:
                vertex_distances = np.linalg.norm(boundary_coords - vertex, axis=1)
                distances[i] = np.min(vertex_distances)
        
        # Normalize
        max_distance = np.max(distances)
        if max_distance > 0:
            distances = distances / max_distance
        
        return distances
    
    def _find_vertex_neighbors(self, vertex_id: int, faces: np.ndarray) -> List[int]:
        """Find neighboring vertices for a given vertex."""
        neighbors = set()
        for face in faces:
            if vertex_id in face:
                neighbors.update(face.tolist())
        neighbors.discard(vertex_id)  # Remove the vertex itself
        return list(neighbors)
    
    def _estimate_cluster_count(self, text_description: str) -> int:
        """Estimate the expected number of clusters based on text description."""
        text_lower = text_description.lower()
        
        # Count semantic elements mentioned
        element_count = 0
        for category, keywords in {
            'water': ['water', 'lake', 'river', 'stream', 'pond', 'spring'],
            'vegetation': ['tree', 'forest', 'grass', 'flower', 'vegetation', 'bush'],
            'terrain': ['mountain', 'hill', 'terrain', 'ground', 'landscape'],
            'rocks': ['rock', 'stone', 'cliff', 'boulder'],
            'snow': ['snow', 'ice', 'frozen']
        }.items():
            if any(keyword in text_lower for keyword in keywords):
                element_count += 1
        
        # Default to 3-5 clusters, adjust based on complexity
        return max(3, min(element_count + 2, 8))
    
    def _estimate_eps(self, features: np.ndarray) -> float:
        """Estimate eps parameter for DBSCAN."""
        # Use k-distance graph method
        from sklearn.neighbors import NearestNeighbors
        
        k = min(10, len(features) // 10)
        neighbors = NearestNeighbors(n_neighbors=k)
        neighbors.fit(features)
        distances, _ = neighbors.kneighbors(features)
        
        # Use the k-th nearest neighbor distance
        kth_distances = distances[:, k-1]
        return np.percentile(kth_distances, 80)  # Use 80th percentile
    
    def _height_based_segmentation(self, vertices: np.ndarray, n_clusters: int) -> np.ndarray:
        """Simple height-based segmentation as fallback."""
        z_coords = vertices[:, 2]
        z_normalized = (z_coords - z_coords.min()) / (z_coords.max() - z_coords.min() + 1e-8)
        
        # Create height-based bins
        bins = np.linspace(0, 1, n_clusters + 1)
        labels = np.digitize(z_normalized, bins) - 1
        labels = np.clip(labels, 0, n_clusters - 1)
        
        return labels
    
    def _ensemble_voting(self, all_labels: List[np.ndarray], weights: List[float]) -> np.ndarray:
        """Combine multiple segmentation results using weighted voting."""
        n_vertices = len(all_labels[0])
        final_labels = np.zeros(n_vertices, dtype=int)
        
        # For each vertex, find the most common label across methods
        for i in range(n_vertices):
            votes = {}
            for labels, weight in zip(all_labels, weights):
                label = labels[i]
                votes[label] = votes.get(label, 0) + weight
            
            # Choose label with highest weighted vote
            final_labels[i] = max(votes.keys(), key=votes.get)
        
        # Relabel to ensure consecutive integers starting from 0
        unique_labels = np.unique(final_labels)
        label_mapping = {old: new for new, old in enumerate(unique_labels)}
        final_labels = np.array([label_mapping[label] for label in final_labels])
        
        return final_labels
    
    def _spatial_smoothing(self, vertices: np.ndarray, faces: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """Apply spatial smoothing to segmentation labels."""
        smoothed_labels = labels.copy()
        
        # Iterative smoothing
        for iteration in range(3):  # 3 iterations of smoothing
            new_labels = smoothed_labels.copy()
            
            for i in range(len(vertices)):
                neighbors = self._find_vertex_neighbors(i, faces)
                if neighbors:
                    neighbor_labels = smoothed_labels[neighbors]
                    # Use majority vote among neighbors
                    unique_labels, counts = np.unique(neighbor_labels, return_counts=True)
                    majority_label = unique_labels[np.argmax(counts)]
                    
                    # Only change if majority is different and significant
                    if majority_label != smoothed_labels[i] and np.max(counts) > len(neighbors) * 0.6:
                        new_labels[i] = majority_label
            
            smoothed_labels = new_labels
        
        return smoothed_labels
    
    def _get_category_keywords(self, category: str) -> List[str]:
        """Get keywords associated with a semantic category."""
        keyword_map = {
            'water': ['water', 'lake', 'river', 'stream', 'pond', 'spring', 'pool', 'blue'],
            'vegetation': ['tree', 'forest', 'grass', 'flower', 'green', 'vegetation', 'bush', 'plant'],
            'terrain': ['terrain', 'ground', 'earth', 'soil', 'dirt', 'brown'],
            'rocks': ['rock', 'stone', 'cliff', 'boulder', 'gray', 'grey'],
            'snow': ['snow', 'ice', 'frozen', 'white', 'winter']
        }
        return keyword_map.get(category, []) 