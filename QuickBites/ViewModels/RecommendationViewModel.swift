//
//  RecommendationViewModel.swift
//  CS125QuickBites
//
//  Created by Ivan Pham on 2/9/26.
//
import Combine

import SwiftUI

class RecommendationViewModel: ObservableObject {
    @Published var results: [Restaurant] = []

    func search(keywords: String, maxPrice: Int?, meal: String?) {
        APIService.fetchRecommendations(
            keywords: keywords,
            maxPrice: maxPrice,
            meal: meal
        ) { self.results = $0 }
    }
}
