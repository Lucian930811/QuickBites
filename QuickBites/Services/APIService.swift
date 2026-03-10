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
        isVegan: Bool,
        isOpenNow: Bool,
        personalize: Bool = false,
        completion: @escaping ([Restaurant]) -> Void
    ) {
        var components = URLComponents(string: "http://127.0.0.1:8000/recommend")!
        components.queryItems = [
            URLQueryItem(name: "keywords", value: keywords),
            URLQueryItem(name: "meal", value: meal),
            URLQueryItem(name: "personalize", value: personalize ? "true" : "false"),
            maxPrice.map { URLQueryItem(name: "max_price", value: "\($0)") }
        ].compactMap { $0 }

        URLSession.shared.dataTask(with: components.url!) { data, _, _ in
            let decoded = (try? JSONDecoder().decode([Restaurant].self, from: data ?? Data())) ?? []
            DispatchQueue.main.async { completion(decoded) }
        }.resume()
    }
    
    static func logInteraction(
        businessId: String,
        eventType: String,
        categories: String? = nil,
        priceLevel: Int? = nil
    ) {
        let url = URL(string: "http://127.0.0.1:8000/interact")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        var body: [String: Any] = [
            "business_id": businessId,
            "event_type": eventType
        ]
        if let cats = categories { body["categories"] = cats }
        if let price = priceLevel { body["price_level"] = price }
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request).resume()
    }
}
