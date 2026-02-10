//
//  ResultsView.swift
//  CS125QuickBites
//
//  Created by Ivan Pham on 2/9/26.
//

import SwiftUI

struct ResultsView: View {
    @StateObject private var vm = RecommendationViewModel()

    var body: some View {
        List(vm.results) { r in
            RestaurantRow(r: r)
        }
        .navigationTitle("QuickBites")
        .onAppear {
            vm.search(keywords: "breakfast,bakery", maxPrice: 2, meal: "morning")
        }
    }
}
