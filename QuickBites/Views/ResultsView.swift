//
//  ResultsView.swift
//  CS125QuickBites
//
//  Created by Ivan Pham on 2/9/26.
//
import SwiftUI

struct ResultsView: View {
    @ObservedObject var vm: RecommendationViewModel

    var body: some View {
        NavigationStack {
            List(vm.results) { r in
                RestaurantRow(r: r)
            }
            .navigationTitle("QuickBites")
        }
    }
}

