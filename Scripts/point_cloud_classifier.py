import numpy as np
import open3d as o3d
from base_point_cloud_processor import BasePointCloudProcessor
from point_cloud_preprocessor import PointCloudPreprocessor


class PointCloudClassifier(BasePointCloudProcessor):
    def __init__(self, point_cloud):
        """
        Initialize the classifier with a point cloud.

        Args:
            point_cloud (open3d.geometry.PointCloud): The input point cloud object.
        """
        super().__init__(point_cloud=point_cloud)  # Initialize the base class
        self.preprocessor = PointCloudPreprocessor(point_cloud)  # Composition

    def preprocess(self):
        """
        Preprocess the point cloud using the preprocessor before classification.
        """
        self.point_cloud = self.preprocessor.process()
        self.track_transformation("Preprocessed point cloud before classification.")

    def detect_planes(
        self,
        distance_threshold=0.1,
        ransac_n=3,
        num_iterations=1000,
        min_plane_points=500,
        max_planes=20,
    ):
        """
        Detect large planar surfaces using RANSAC and merge similar planes.

        Returns:
            tuple: A list of detected planes and their normals.
        """
        self.validate_point_cloud()  # Ensure the point cloud is loaded
        planes = []
        plane_normals = []
        remaining_pcd = self.point_cloud

        while len(planes) < max_planes:
            plane_model, inliers = remaining_pcd.segment_plane(
                distance_threshold=distance_threshold,
                ransac_n=ransac_n,
                num_iterations=num_iterations,
            )

            if len(inliers) < min_plane_points:
                print("No more large planes found.")
                break

            plane = remaining_pcd.select_by_index(inliers)
            remaining_pcd = remaining_pcd.select_by_index(inliers, invert=True)
            normal = plane_model[:3]

            # Merge similar planes
            similar_plane_found = False
            for i, existing_normal in enumerate(plane_normals):
                normal_similarity = np.dot(existing_normal, normal)
                centroid_distance = np.linalg.norm(
                    np.mean(np.asarray(planes[i].points), axis=0)
                    - np.mean(np.asarray(plane.points), axis=0)
                )
                if normal_similarity > 0.95 and centroid_distance < 5:
                    similar_plane_found = True
                    planes[i] += plane
                    break

            if not similar_plane_found:
                planes.append(plane)
                plane_normals.append(normal)

            self.track_transformation(
                f"Detected a plane with {len(plane.points)} points."
            )
            print(f"Detected a plane with {len(plane.points)} points.")

        # Log detected planes
        headers = ["Plane", "Points", "Normal Vector"]
        rows = [
            [
                i + 1,
                len(plane.points),
                f"[{normal[0]:.4f}, {normal[1]:.4f}, {normal[2]:.4f}]",
            ]
            for i, (plane, normal) in enumerate(zip(planes, plane_normals))
        ]
        self.log_table(headers, rows, "Detected Planes")

        self.add_metadata("detected_planes", len(planes))
        print(f"Detected {len(planes)} planes.")
        return planes, plane_normals

    def classify_planes(self, planes, plane_normals, min_roof_height=5.0):
        """
        Classify planes into walls and roofs based on normals and height.

        Returns:
            dict: A dictionary containing lists of walls and roofs.
        """
        walls = []
        roofs = []
        rows = []

        for i, (plane, normal) in enumerate(zip(planes, plane_normals)):
            normal /= np.linalg.norm(normal)
            points = np.asarray(plane.points)
            min_z = np.min(points[:, 2])
            max_z = np.max(points[:, 2])

            if abs(normal[2]) < 0.3:  # Vertical planes (walls)
                walls.append(plane)
                plane_type = "Wall"
            elif (
                abs(normal[2]) > 0.7 and max_z >= min_roof_height
            ):  # Horizontal planes (roofs)
                roofs.append(plane)
                plane_type = "Roof"
            else:
                plane_type = "Other"

            rows.append(
                [i + 1, plane_type, len(plane.points), f"{min_z:.2f} to {max_z:.2f}"]
            )

        # Log classified planes
        headers = ["Plane", "Type", "Points", "Height Range"]
        self.log_table(headers, rows, "Classified Planes")

        self.add_metadata("classified_walls", len(walls))
        self.add_metadata("classified_roofs", len(roofs))
        self.track_transformation(
            f"Classified planes: {len(walls)} walls, {len(roofs)} roofs."
        )
        print(f"Classified {len(walls)} walls and {len(roofs)} roofs.")
        return {"walls": walls, "roofs": roofs}

    def process(self):
        """
        Run the classification pipeline: preprocess, detect planes, and classify them.

        Returns:
            dict: Classified planes as walls and roofs.
        """
        self.preprocess()  # Preprocessing step
        planes, normals = self.detect_planes(
            distance_threshold=0.1,
            ransac_n=3,
            num_iterations=1000,
            min_plane_points=500,
            max_planes=20,
        )
        results = self.classify_planes(planes, normals, min_roof_height=4.0)
        self.track_transformation("Completed classification pipeline.")
        return results
