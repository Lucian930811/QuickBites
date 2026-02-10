//
//  APIService.swift
//  CS125QuickBites
//
//  Created by Ivan Pham on 2/9/26.
//
import Foundation
class APIService {
    static func fetchRecommendations(
        keywords: String,
        maxPrice: Int?,
        meal: String?,
        completion: @escaping ([Restaurant]) -> Void
    ) {
        var components = URLComponents(string: "http://127.0.0.1:8000/recommend")!
        components.queryItems = [
            URLQueryItem(name: "keywords", value: keywords),
            URLQueryItem(name: "meal", value: meal),
            maxPrice.map { URLQueryItem(name: "max_price", value: "\($0)") }
        ].compactMap { $0 }

        URLSession.shared.dataTask(with: components.url!) { data, _, _ in
            let decoded = (try? JSONDecoder().decode([Restaurant].self, from: data ?? Data())) ?? []
            DispatchQueue.main.async { completion(decoded) }
        }.resume()
    }
}
