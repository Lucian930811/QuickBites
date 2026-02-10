//
//  Restaurant
//  CS125QuickBites
//
//  Created by Ivan Pham on 2/9/26.
//
import Foundation

struct Restaurant: Identifiable, Decodable {
    let business_id: String
    let name: String
    let stars: Double
    let review_count: Int
    let score: Double
    let matched_categories: String
    let latitude: Double?
    let longitude: Double?
    let price_level: Int?

    var id: String { business_id }
}

