from point_cloud_loader import PointCloudLoader
from point_cloud_visualizer import PointCloudVisualizer
from point_cloud_segmenter import PointCloudSegmenter
from point_cloud_classifier import PointCloudClassifier


def main():
    file_path = "../data/plaza_roma.laz"

    print("\n===== Step 1: Loading the Point Cloud =====")
    loader = PointCloudLoader(file_path)
    raw_cloud = loader.process()

    print("\n===== Step 2: Visualizing the Raw Point Cloud =====")
    visualizer = PointCloudVisualizer(raw_cloud)
    visualizer.visualize()

    print("\n===== Step 3: Preprocessing and Segmenting the Point Cloud =====")
    segmenter = PointCloudSegmenter(raw_cloud)
    preprocessed_cloud = segmenter.preprocess_and_segment()
    visualizer.point_cloud = preprocessed_cloud
    visualizer.visualize()

    print("\n===== Step 4: Classifying Planes (Walls and Roofs) =====")
    classifier = PointCloudClassifier(preprocessed_cloud)
    classified_planes = classifier.process()

    print("\n===== Step 5: Visualizing Classified Planes =====")
    visualizer.visualize_classified_clouds(
        classified_planes["walls"], classified_planes["roofs"]
    )

    print("\n===== Process Complete =====")
    print("Pipeline execution completed successfully.")


if __name__ == "__main__":
    main()
