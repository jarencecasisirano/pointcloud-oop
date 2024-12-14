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

        for plane, normal in zip(planes, plane_normals):
            normal /= np.linalg.norm(normal)
            points = np.asarray(plane.points)
            min_z = np.min(points[:, 2])
            max_z = np.max(points[:, 2])

            print(f"Plane normal: {normal}, Height range: {min_z} to {max_z}")

            if abs(normal[2]) < 0.3:  # Vertical planes (walls)
                walls.append(plane)
            elif (
                abs(normal[2]) > 0.7 and max_z >= min_roof_height
            ):  # Horizontal planes (roofs)
                roofs.append(plane)
            else:
                print("Plane classified as ground or oblique, excluded.")

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
