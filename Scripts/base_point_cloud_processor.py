import open3d as o3d


class BasePointCloudProcessor:
    def __init__(self, point_cloud=None, metadata=None):
        """
        Initialize the processor with an optional point cloud and metadata.

        Args:
            point_cloud (open3d.geometry.PointCloud): Input point cloud.
            metadata (dict): Additional information about the point cloud.
        """
        self.point_cloud = point_cloud  # Shared point cloud object
        self.metadata = metadata if metadata else {}  # To track additional info

    def visualize(self):
        """Visualize the point cloud using Open3D."""
        if self.point_cloud:
            o3d.visualization.draw_geometries([self.point_cloud])
        else:
            print("No point cloud loaded.")

    def add_metadata(self, key, value):
        """Add metadata information."""
        self.metadata[key] = value

    def validate_point_cloud(self):
        """Ensure the point cloud is loaded before performing operations."""
        if not self.point_cloud or len(self.point_cloud.points) == 0:
            raise RuntimeError("Point cloud is not loaded or is empty.")

    def track_transformation(self, description):
        """Add a record of a transformation step."""
        if "history" not in self.metadata:
            self.metadata["history"] = []
        self.metadata["history"].append(description)

    def get_metadata(self):
        """Return the metadata dictionary."""
        return self.metadata

    def log_table(self, headers, rows, title=None):
        """
        Logs data in table format.
        Args:
            headers (list): List of column headers.
            rows (list of lists): Each sublist represents a row of data.
            title (str): Optional title for the table.
        """
        if title:
            print("\n" + "=" * len(title))
            print(title)
            print("=" * len(title))
        
        # Print headers
        row_format = "| {:<12} " * len(headers) + "|"
        print(row_format.format(*headers))
        print("|" + "------------" * len(headers) + "|")

        # Print rows
        for row in rows:
            print(row_format.format(*row))
        print("=" * (13 * len(headers)))

    def process(self):
        """Override this in child classes for specific processing steps."""
        raise NotImplementedError("Subclasses must implement this method.")

