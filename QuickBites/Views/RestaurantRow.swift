//
//  RestaurantRow.swift
//  CS125QuickBites
//
//  Created by Ivan Pham on 2/9/26.
//

import SwiftUI

struct RestaurantRow: View {
    let r: Restaurant
    @ObservedObject var vm: RecommendationViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(r.name).font(.headline)

            Text("⭐️ \(r.stars, specifier: "%.1f") • \(r.review_count) reviews")

            if let price = r.price_level {
                Text(String(repeating: "$", count: price))
            }

            if let address = r.address {
                Text("\(address), \(r.city ?? ""), \(r.state ?? "")")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            if r.is_vegan == true {
                Text("🌱 Vegan").font(.caption).foregroundStyle(.green)
            }

            let mealInfo = vm.parseMealInfo(r.good_for_meal)
            HStack(spacing: 4) {
                if mealInfo["breakfast"] == true { Text("Breakfast ✅").font(.caption) }
                if mealInfo["lunch"] == true { Text("Lunch ✅").font(.caption) }
                if mealInfo["dinner"] == true { Text("Dinner ✅").font(.caption) }
            }

            if let hours = r.hours {
                let hoursDict = vm.parseHours(hours)
                Text(hoursDict.map { "\($0.key): \($0.value)" }.joined(separator: " • "))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }

            if !r.matched_categories.isEmpty {
                Text(r.matched_categories)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            
            if let explanation = r.explanation {
                Text("✨ \(explanation)")
                    .font(.caption)
                    .foregroundStyle(.purple)
                    .padding(.top, 2)
            }
        }
        .padding(4)
        .onTapGesture {
            vm.logInteraction(restaurant: r, eventType: "click")
        }
    }
}
