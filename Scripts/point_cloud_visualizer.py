import numpy as np
import open3d as o3d
from base_point_cloud_processor import BasePointCloudProcessor
from point_cloud_preprocessor import PointCloudPreprocessor


class PointCloudVisualizer(BasePointCloudProcessor):
    def __init__(self, point_cloud=None):
        """
        Initialize the visualizer with a point cloud.

        Args:
            point_cloud (open3d.geometry.PointCloud): The input point cloud.
        """
        super().__init__(point_cloud=point_cloud)  # Initialize the base class
        self.preprocessor = PointCloudPreprocessor(point_cloud)  # Composition

    def prepare_classified_clouds(self, walls, roofs):
        """
        Combine walls and roofs into a single point cloud with assigned colors.

        Args:
            walls (list): List of wall point clouds.
            roofs (list): List of roof point clouds.

        Returns:
            open3d.geometry.PointCloud: Combined point cloud with colors applied.
        """
        self.validate_point_cloud()  # Ensure the point cloud is loaded

        walls_combined = o3d.geometry.PointCloud()
        roofs_combined = o3d.geometry.PointCloud()

        for wall in walls:
            walls_combined += wall

        for roof in roofs:
            roofs_combined += roof

        # Assign colors to walls and roofs
        walls_combined.colors = o3d.utility.Vector3dVector(
            np.tile([0, 0, 1], (len(walls_combined.points), 1))
        )  # Blue for walls
        roofs_combined.colors = o3d.utility.Vector3dVector(
            np.tile([1, 0, 0], (len(roofs_combined.points), 1))
        )  # Red for roofs

        # Combine both into one for visualization
        combined_cloud = walls_combined + roofs_combined
        self.add_metadata("combined_cloud_points", len(combined_cloud.points))
        self.track_transformation(
            f"Prepared classified clouds: {len(combined_cloud.points)} total points."
        )

        # Log summary table
        headers = ["Category", "Points"]
        rows = [
            ["Walls", len(walls_combined.points)],
            ["Roofs", len(roofs_combined.points)],
        ]
        self.log_table(headers, rows, "Classified Clouds Summary")
        return combined_cloud

    def preprocess_and_visualize(self):
        """
        Preprocess the point cloud using the preprocessor and then visualize.
        """
        self.point_cloud = self.preprocessor.process()
        self.track_transformation("Preprocessed point cloud for visualization.")
        self.visualize()

    def visualize_classified_clouds(self, walls, roofs):
        """
        Visualize walls and roofs with assigned colors.

        Args:
            walls (list): List of wall point clouds.
            roofs (list): List of roof point clouds.
        """
        # Prepare combined point cloud with colors
        combined_cloud = self.prepare_classified_clouds(walls, roofs)

        # Visualize the combined cloud
        print(
            f"Visualizing classified clouds with {len(combined_cloud.points)} points."
        )
        o3d.visualization.draw_geometries([combined_cloud])

    def visualize(self):
        """
        Visualize the point cloud using Open3D.
        """
        self.validate_point_cloud()  # Ensure the point cloud is loaded
        print(f"Visualizing point cloud with {len(self.point_cloud.points)} points.")
        self.track_transformation(
            f"Visualized point cloud with {len(self.point_cloud.points)} points."
        )
        o3d.visualization.draw_geometries([self.point_cloud])

    def process(self):
        """
        Visualize the current point cloud.

        Returns:
            None
        """
        self.visualize()
        self.track_transformation("Visualization completed.")
