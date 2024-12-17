import numpy as np
import open3d as o3d
from shapely.geometry import Point, Polygon
from base_point_cloud_processor import BasePointCloudProcessor
from point_cloud_preprocessor import PointCloudPreprocessor


class PointCloudSegmenter(BasePointCloudProcessor):
    def __init__(self, point_cloud):
        """
        Initialize the segmenter with a point cloud.

        Args:
            point_cloud (open3d.geometry.PointCloud): The input point cloud object.
        """
        super().__init__(point_cloud=point_cloud)  # Initialize the base class
        self.preprocessor = PointCloudPreprocessor(point_cloud)  # Composition

    def polygon_filter(self, polygon_coords):
        """
        Apply a polygon-based filter to the point cloud.

        Args:
            polygon_coords (list of tuples): List of (X, Y) coordinates defining the polygon vertices.

        Returns:
            open3d.geometry.PointCloud: The filtered point cloud within the polygon.
        """
        self.validate_point_cloud()  # Ensure the point cloud is loaded
        original_count = len(self.point_cloud.points)
        polygon = Polygon(polygon_coords)
        points = np.asarray(self.point_cloud.points)
        mask = [polygon.contains(Point(pt[0], pt[1])) for pt in points]
        filtered_points = points[mask]

        filtered_cloud = o3d.geometry.PointCloud()
        filtered_cloud.points = o3d.utility.Vector3dVector(filtered_points)
        self.point_cloud = filtered_cloud
        self.add_metadata("polygon_filter", len(filtered_points))
        self.track_transformation(
            f"Applied polygon filter: {len(filtered_points)} points remain."
        )

        headers = ["Step", "Original Points", "Remaining Points"]
        rows = [["Polygon Filter", original_count, len(filtered_points)]]
        self.log_table(headers, rows, "Polygon Filter Summary")
        return self.point_cloud

    def ground_removal(self, z_threshold=2.0):
        """
        Remove ground points based on height (Z-coordinate).

        Args:
            z_threshold (float): Height threshold below which points are considered ground.

        Returns:
            open3d.geometry.PointCloud: The filtered point cloud without ground points.
        """
        self.validate_point_cloud()  # Ensure the point cloud is loaded
        original_count = len(self.point_cloud.points)
        points = np.asarray(self.point_cloud.points)
        mask = points[:, 2] > z_threshold  # Keep points above the Z threshold
        filtered_points = points[mask]

        filtered_cloud = o3d.geometry.PointCloud()
        filtered_cloud.points = o3d.utility.Vector3dVector(filtered_points)
        self.point_cloud = filtered_cloud
        self.add_metadata("ground_removal", len(filtered_points))
        self.track_transformation(
            f"Ground removal applied: {len(filtered_points)} points remain."
        )

        headers = ["Step", "Original Points", "Remaining Points"]
        rows = [["Ground Removal", original_count, len(filtered_points)]]
        self.log_table(headers, rows, "Ground Removal Summary")
        return self.point_cloud

    def preprocess_and_segment(self):
        """
        Preprocess the point cloud using the preprocessor and then segment it.
        """
        self.point_cloud = self.preprocessor.process()
        self.track_transformation("Preprocessed point cloud for segmentation.")
        return self.process()

    def process(self):
        """
        Run the segmentation pipeline: polygon filter and ground removal.

        Returns:
            open3d.geometry.PointCloud: The segmented point cloud.
        """
        polygon_coords = [
            (281580.799, 1614183.657),
            (281535.686, 1614142.893),
            (281585.177, 1614088.225),
            (281630.142, 1614128.812),
        ]
        self.polygon_filter(polygon_coords)
        self.ground_removal(z_threshold=0.5)
        self.track_transformation("Completed segmentation pipeline.")
        return self.point_cloud
