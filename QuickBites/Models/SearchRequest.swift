//
//  SearchRequest.swift
//  CS125QuickBites
//
//  Created by Ivan Pham on 2/9/26.
//

struct SearchRequest: Codable {
    let query: String
    let preferences: Preferences
    let latitude: Double
    let longitude: Double
}

struct Preferences: Codable {
    let vegan: Bool
    let open_now: Bool
    let price_range: Int
}
