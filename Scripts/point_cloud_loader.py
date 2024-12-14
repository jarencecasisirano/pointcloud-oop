import laspy
import open3d as o3d
import numpy as np
from base_point_cloud_processor import BasePointCloudProcessor


class PointCloudLoader(BasePointCloudProcessor):
    def __init__(self, file_path):
        """
        Initialize the loader with the file path.

        Args:
            file_path (str): Path to the .LAZ file.
        """
        super().__init__()  # Initialize the base class
        self.file_path = file_path

    def load_data(self):
        """
        Load point cloud data from the .LAZ file.

        Returns:
            open3d.geometry.PointCloud: The point cloud as an Open3D object.
        """
        try:
            las = laspy.read(self.file_path)
            points = np.vstack((las.x, las.y, las.z)).T  # Extract coordinates
            self.point_cloud = o3d.geometry.PointCloud()
            self.point_cloud.points = o3d.utility.Vector3dVector(points)
            self.add_metadata("loaded_points", len(points))
            self.track_transformation(
                f"Loaded point cloud from {self.file_path} with {len(points)} points."
            )
            print(f"Loaded point cloud with {len(points)} points from {self.file_path}")
            return self.point_cloud
        except Exception as e:
            raise RuntimeError(f"Failed to load point cloud: {str(e)}")

    def process(self):
        """
        Run the loading pipeline.

        Returns:
            open3d.geometry.PointCloud: The loaded point cloud.
        """
        try:
            result = self.load_data()
            self.track_transformation("Completed loading pipeline.")
            return result
        except RuntimeError as e:
            self.track_transformation(f"Loading failed: {str(e)}")
            raise
