import SwiftUI
import MapKit

struct MapResultsView: View {
    @ObservedObject var vm: RecommendationViewModel

    @State private var region = MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 34.4144, longitude: -119.6906),
        span: MKCoordinateSpan(latitudeDelta: 0.1, longitudeDelta: 0.1)
    )

    var body: some View {
        NavigationStack {
            Map(coordinateRegion: $region, annotationItems: vm.results) { r in
                MapMarker(
                    coordinate: CLLocationCoordinate2D(latitude: r.latitude, longitude: r.longitude),
                    tint: .red
                )
            }
            .onChange(of: vm.results) { _ in
                zoomToFitAllPins()
            }
            .navigationTitle("Map")
        }
    }

    private func zoomToFitAllPins() {
        guard !vm.results.isEmpty else { return }

        let lats = vm.results.map(\.latitude)
        let lons = vm.results.map(\.longitude)
        let minLat = lats.min()!
        let maxLat = lats.max()!
        let minLon = lons.min()!
        let maxLon = lons.max()!

        let center = CLLocationCoordinate2D(
            latitude: (minLat + maxLat)/2,
            longitude: (minLon + maxLon)/2
        )
        let span = MKCoordinateSpan(
            latitudeDelta: (maxLat - minLat) * 1.3,
            longitudeDelta: (maxLon - minLon) * 1.3
        )
        region = MKCoordinateRegion(center: center, span: span)
    }
}
