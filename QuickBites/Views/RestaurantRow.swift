//
//  RestaurantRow.swift
//  CS125QuickBites
//
//  Created by Ivan Pham on 2/9/26.
//

import SwiftUI

struct RestaurantRow: View {
    let r: Restaurant

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(r.name).font(.headline)
            Text("⭐️ \(r.stars, specifier: "%.1f") • \(r.review_count) reviews")
            if let price = r.price_level {
                Text(String(repeating: "$", count: price))
            }
            if !r.matched_categories.isEmpty {
                Text(r.matched_categories)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }
}
