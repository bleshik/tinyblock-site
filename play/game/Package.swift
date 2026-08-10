// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "PoingGodotAdMobDeps",
    platforms: [.iOS(.v13)],
    products: [
        .library(
            name: "PoingGodotAdMobDeps",
            targets: ["PoingGodotAdMobDeps"]),
    ],
    dependencies: [
        .package(url: "https://github.com/googleads/swift-package-manager-google-mobile-ads.git", exact: "13.7.0"),
        .package(url: "https://github.com/googleads/swift-package-manager-google-user-messaging-platform.git", exact: "3.1.0"),
        .package(url: "https://github.com/googleads/googleads-mobile-ios-mediation-liftoffmonetize.git", exact: "7.7.400"),
    ],
    targets: [
        .target(
            name: "PoingGodotAdMobDeps",
            dependencies: [
                .product(name: "GoogleMobileAds", package: "swift-package-manager-google-mobile-ads"),
                .product(name: "GoogleUserMessagingPlatform", package: "swift-package-manager-google-user-messaging-platform"),
                .product(name: "LiftoffMonetizeAdapterTarget", package: "googleads-mobile-ios-mediation-liftoffmonetize"),
            ],
            path: "PoingGodotAdMobDeps"
        )
    ]
)
