//
//  ProfileView.swift
//  QuickBites
//
import SwiftUI
import MapKit
import CoreLocation

struct IdentifiablePlacemark: Identifiable {
    let id = UUID()
    let placemark: MKPlacemark
    var coordinate: CLLocationCoordinate2D { placemark.coordinate }
}

struct LocationConfirmView: View {
    let item: MKMapItem
    let label: String
    let onConfirm: () -> Void
    let onCancel: () -> Void
    @State private var region: MKCoordinateRegion

    init(item: MKMapItem, label: String, onConfirm: @escaping () -> Void, onCancel: @escaping () -> Void) {
        self.item = item
        self.label = label
        self.onConfirm = onConfirm
        self.onCancel = onCancel
        _region = State(initialValue: MKCoordinateRegion(
            center: item.placemark.coordinate,
            span: MKCoordinateSpan(latitudeDelta: 0.02, longitudeDelta: 0.02)
        ))
    }

    var body: some View {
        let annotation = IdentifiablePlacemark(placemark: item.placemark)
        NavigationStack {
            VStack(spacing: 16) {
                Map(coordinateRegion: $region, annotationItems: [annotation]) { place in
                    MapMarker(coordinate: place.coordinate, tint: .red)
                }
                .frame(height: 300)
                .cornerRadius(12)
                .padding()

                VStack(alignment: .leading, spacing: 4) {
                    Text(item.name ?? "Unknown")
                        .font(.headline)
                    Text(item.placemark.title ?? "")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal)

                Spacer()

                HStack(spacing: 16) {
                    Button("Cancel") { onCancel() }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(.gray.opacity(0.2))
                        .cornerRadius(10)

                    Button("Set as \(label.capitalized)") { onConfirm() }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(.teal)
                        .foregroundStyle(.white)
                        .cornerRadius(10)
                }
                .padding()
            }
            .navigationTitle("Confirm Location")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

struct LocationSearchView: View {
    let label: String
    @Binding var isPresented: Bool
    @State private var searchQuery: String = ""
    @State private var results: [MKMapItem] = []
    @State private var selectedItem: MKMapItem? = nil
    @State private var showConfirmation = false
    var onSelect: (Double, Double, String) -> Void

    var body: some View {
        NavigationStack {
            VStack {
                TextField("Search address...", text: $searchQuery)
                    .padding()
                    .background(.gray.opacity(0.1))
                    .cornerRadius(10)
                    .padding()
                    .onChange(of: searchQuery) { _, newValue in
                        searchAddress(newValue)
                    }

                List(results, id: \.self) { item in
                    Button {
                        selectedItem = item
                        showConfirmation = true
                    } label: {
                        VStack(alignment: .leading) {
                            Text(item.name ?? "Unknown")
                                .font(.headline)
                            Text(item.placemark.title ?? "")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
            .navigationTitle("Set \(label.capitalized) Location")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { isPresented = false }
                }
            }
            .sheet(isPresented: $showConfirmation) {
                if let item = selectedItem {
                    LocationConfirmView(item: item, label: label) {
                        let coord = item.placemark.coordinate
                        let name = item.name ?? item.placemark.title ?? "Unknown"
                        onSelect(coord.latitude, coord.longitude, name)
                        isPresented = false
                    } onCancel: {
                        showConfirmation = false
                        selectedItem = nil
                    }
                }
            }
        }
    }

    func searchAddress(_ query: String) {
        guard !query.isEmpty else {
            results = []
            return
        }
        let request = MKLocalSearch.Request()
        request.naturalLanguageQuery = query
        request.region = MKCoordinateRegion(
            center: CLLocationCoordinate2D(latitude: 37.0, longitude: -95.0),
            span: MKCoordinateSpan(latitudeDelta: 30, longitudeDelta: 60)
        )
        request.resultTypes = [.address, .pointOfInterest]
        MKLocalSearch(request: request).start { response, _ in
            results = response?.mapItems ?? []
        }
    }
}

struct ProfileView: View {
    @State private var homeLabel: String = "Not set"
    @State private var workLabel: String = "Not set"
    @State private var showHomeSearch = false
    @State private var showWorkSearch = false
    @State private var statusMessage: String = ""

    var body: some View {
        Form {
            Section("Home Location") {
                HStack {
                    VStack(alignment: .leading) {
                        Text("Home").font(.headline)
                        Text(homeLabel)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                    Button("Change") { showHomeSearch = true }
                }
            }

            Section("Work Location") {
                HStack {
                    VStack(alignment: .leading) {
                        Text("Work").font(.headline)
                        Text(workLabel)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                    Button("Change") { showWorkSearch = true }
                }
            }

            if !statusMessage.isEmpty {
                Text(statusMessage).foregroundStyle(.green)
            }
        }
        .navigationTitle("My Locations")
        .onAppear { fetchLocations() }
        .sheet(isPresented: $showHomeSearch) {
            LocationSearchView(label: "home", isPresented: $showHomeSearch) { lat, lon, name in
                homeLabel = name
                saveLocation(label: "home", lat: lat, lon: lon, name: name)
            }
        }
        .sheet(isPresented: $showWorkSearch) {
            LocationSearchView(label: "work", isPresented: $showWorkSearch) { lat, lon, name in
                workLabel = name
                saveLocation(label: "work", lat: lat, lon: lon, name: name)
            }
        }
    }

    func saveLocation(label: String, lat: Double, lon: Double, name: String) {
        guard let url = URL(string: "http://127.0.0.1:8000/profile/location") else { return }
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body: [String: Any] = ["label": label, "lat": lat, "lon": lon, "name": name]
        req.httpBody = try? JSONSerialization.data(withJSONObject: body)
        URLSession.shared.dataTask(with: req) { _, _, _ in
            DispatchQueue.main.async {
                statusMessage = "\(label.capitalized) location saved!"
            }
        }.resume()
    }

    func fetchLocations() {
        guard let url = URL(string: "http://127.0.0.1:8000/profile/locations") else { return }
        URLSession.shared.dataTask(with: url) { data, _, _ in
            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return }
            DispatchQueue.main.async {
                if let home = json["home"] as? [String: Any],
                   let name = home["name"] as? String, !name.isEmpty {
                    homeLabel = name  // show name instead of coordinates
                }
                if let work = json["work"] as? [String: Any],
                   let name = work["name"] as? String, !name.isEmpty {
                    workLabel = name
                }
            }
        }.resume()
    }
}
