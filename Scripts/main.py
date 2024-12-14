from point_cloud_loader import PointCloudLoader
from point_cloud_visualizer import PointCloudVisualizer
from point_cloud_segmenter import PointCloudSegmenter
from point_cloud_classifier import PointCloudClassifier


def main():
    file_path = "../data/plaza_roma.laz"

    # Step 1: Load the point cloud
    loader = PointCloudLoader(file_path)
    raw_cloud = loader.process()
    print("Point cloud loaded successfully.")

    # Step 2: Visualize the loaded point cloud
    visualizer = PointCloudVisualizer(raw_cloud)
    visualizer.visualize()
    print("Visualized loaded point cloud.")

    # Step 3: Preprocess the point cloud
    segmenter = PointCloudSegmenter(raw_cloud)
    preprocessed_cloud = segmenter.preprocess_and_segment()
    visualizer.point_cloud = (
        preprocessed_cloud  # Update visualizer with the preprocessed cloud
    )
    visualizer.visualize()
    print("Visualized preprocessed and segmented point cloud.")

    # Step 4: Classify the planes (walls and roofs)
    classifier = PointCloudClassifier(preprocessed_cloud)
    classified_planes = classifier.process()
    print("Planes classified successfully.")

    # Step 5: Visualize the classified planes
    visualizer.visualize_classified_clouds(
        classified_planes["walls"], classified_planes["roofs"]
    )
    print("Visualized classified planes.")

    # Step 6
    # print(classifier.get_metadata()["history"])
    print("All steps completed successfully.")


if __name__ == "__main__":
    main()
