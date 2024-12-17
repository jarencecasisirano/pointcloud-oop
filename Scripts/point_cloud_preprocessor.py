import open3d as o3d
from base_point_cloud_processor import BasePointCloudProcessor


class PointCloudPreprocessor(BasePointCloudProcessor):
    def __init__(self, point_cloud):
        """
        Initialize the preprocessor with a point cloud.

        Args:
            point_cloud (open3d.geometry.PointCloud): The input point cloud object.
        """
        super().__init__(point_cloud=point_cloud)  # Initialize the base class

    def remove_outliers(self, nb_neighbors=10, std_ratio=3.0):
        """
        Remove outliers from the point cloud using a statistical outlier removal filter.

        Args:
            nb_neighbors (int): Number of nearest neighbors to consider for filtering.
            std_ratio (float): Standard deviation ratio for filtering outliers.

        Returns:
            open3d.geometry.PointCloud: The filtered point cloud.
        """
        self.validate_point_cloud()  # Ensure the point cloud is loaded
        cl, ind = self.point_cloud.remove_statistical_outlier(
            nb_neighbors=nb_neighbors, std_ratio=std_ratio
        )
        original_count = len(self.point_cloud.points)
        self.point_cloud = self.point_cloud.select_by_index(ind)
        self.add_metadata("outlier_removal", len(self.point_cloud.points))
        self.track_transformation(
            f"Removed outliers: {len(self.point_cloud.points)} points remain."
        )

        headers = ["Step", "Original Points", "Remaining Points"]
        rows = [["Outlier Removal", original_count, len(self.point_cloud.points)]]
        self.log_table(headers, rows, "Outlier Removal Summary")
        return self.point_cloud

    def downsample(self, voxel_size=0.3):
        """
        Downsample the point cloud using a voxel grid filter.

        Args:
            voxel_size (float): Size of the voxel grid for downsampling.

        Returns:
            open3d.geometry.PointCloud: The downsampled point cloud.
        """
        self.validate_point_cloud()  # Ensure the point cloud is loaded
        original_count = len(self.point_cloud.points)
        self.point_cloud = self.point_cloud.voxel_down_sample(voxel_size=voxel_size)
        self.add_metadata("downsample", len(self.point_cloud.points))
        self.track_transformation(
            f"Downsampled point cloud: {len(self.point_cloud.points)} points remain."
        )

        headers = ["Step", "Original Points", "Remaining Points"]
        rows = [["Downsampling", original_count, len(self.point_cloud.points)]]
        self.log_table(headers, rows, "Downsampling Summary")
        return self.point_cloud

    def process(self):
        """
        Run the preprocessing pipeline: remove outliers and downsample.

        Returns:
            open3d.geometry.PointCloud: The preprocessed point cloud.
        """
        self.remove_outliers(nb_neighbors=10, std_ratio=3.0)
        self.downsample(voxel_size=0.2)
        self.track_transformation("Completed preprocessing pipeline.")
        return self.point_cloud
