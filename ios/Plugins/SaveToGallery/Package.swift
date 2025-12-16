// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "SaveToGallery",
    platforms: [.iOS(.v15)],
    products: [
        .library(
            name: "SaveToGallery",
            targets: ["SaveToGalleryPlugin"]
        )
    ],
    targets: [
        .target(
            name: "SaveToGalleryPlugin",
            dependencies: [],
            path: "Sources"
        )
    ]
)



