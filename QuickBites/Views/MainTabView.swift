//
//  MainTabView.swift
//  CS125QuickBites
//
//  Created by Ivan Pham on 2/10/26.
//


import SwiftUI

struct MainTabView: View {
    @StateObject private var vm = RecommendationViewModel()

    var body: some View {
        TabView {
            ContentView(vm: vm)
                .tabItem {
                    Label("Search", systemImage: "magnifyingglass")
                }

            ResultsView(vm: vm)
                .tabItem {
                    Label("Results", systemImage: "list.bullet")
                }
            MapResultsView(vm: vm)
                           .tabItem {
                               Label("Map", systemImage: "map")
                           }
        }
    }
}
