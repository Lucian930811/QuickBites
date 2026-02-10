import Foundation
import Combine

@MainActor
class RecommendationViewModel: ObservableObject {
    @Published var results: [Restaurant] = []

    func search(keywords: String, maxPrice: Int?, meal: String?) async {
        // Build the query string
        var urlComponents = URLComponents(string: "http://127.0.0.1:8000/recommend")!
        var queryItems: [URLQueryItem] = [
            URLQueryItem(name: "keywords", value: keywords)
        ]
        if let maxPrice = maxPrice {
            queryItems.append(URLQueryItem(name: "max_price", value: "\(maxPrice)"))
        }
        if let meal = meal {
            queryItems.append(URLQueryItem(name: "meal", value: meal))
        }
        urlComponents.queryItems = queryItems

        guard let url = urlComponents.url else { return }

        do {
            let (data, response) = try await URLSession.shared.data(from: url)
            let decoded = try JSONDecoder().decode([Restaurant].self, from: data)
            self.results = decoded
            print("Response:", response)
            print("Decoded restaurants:", decoded.count)

        } catch {
            print("Request failed:", error)
        }
    }
}
