import Foundation
import Combine

@MainActor
class RecommendationViewModel: ObservableObject {
    @Published var results: [Restaurant] = []

    func search(keywords: String,
                    maxPrice: Int?,
                    meal: String,
                    isVegan: Bool,
                    isOpenNow: Bool) async {
        // Build the query string
        var urlComponents = URLComponents(string: "http://127.0.0.1:8000/recommend")!
        var queryItems: [URLQueryItem] = [
            URLQueryItem(name: "keywords", value: keywords)
        ]
        if let maxPrice = maxPrice {
            queryItems.append(URLQueryItem(name: "max_price", value: "\(maxPrice)"))
        }
        if !meal.isEmpty {
            queryItems.append(URLQueryItem(name: "meal", value: meal))
        }
        queryItems.append(URLQueryItem(name: "vegan", value: "\(isVegan)"))
        queryItems.append(URLQueryItem(name: "open_now", value: "\(isOpenNow)"))
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
    // Helper to parse good_for_meal string -> dictionary
       func parseMealInfo(_ str: String?) -> [String: Bool] {
           guard let str = str else { return [:] }
           let jsonStr = str.replacingOccurrences(of: "'", with: "\"")
           let data = Data(jsonStr.utf8)
           return (try? JSONDecoder().decode([String: Bool].self, from: data)) ?? [:]
       }

       // Helper to parse hours string -> dictionary
       func parseHours(_ str: String?) -> [String: String] {
           guard let str = str else { return [:] }
           let jsonStr = str.replacingOccurrences(of: "'", with: "\"")
           let data = Data(jsonStr.utf8)
           return (try? JSONDecoder().decode([String: String].self, from: data)) ?? [:]
       }
}
