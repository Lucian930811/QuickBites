//
//  ContentView.swift
//  QuickBites
//
//  Created by Ivan Pham on 2/4/26.
//
import SwiftUI
import MapKit
import Foundation

struct ContentView: View {
    @State private var distanceWeight: Double = 0.5  // 0 = ignore distance, 1 = distance is everything
    @State private var showProfile = false
    @State private var query: String = ""
    @State private var isVegan = false
    @State private var isOpenNow = true
    @State private var priceRange = 2
    @State private var meal: String = ""
    @State private var isPersonalized = false
    @State var locationManager = LocationManager()
    @State private var origin: String = "current"
    
    @ObservedObject var vm: RecommendationViewModel
    
    var body: some View {
        NavigationStack {
            ZStack {
                Rectangle()
                    .fill(Color.teal)
                    .ignoresSafeArea()
                VStack {
                    Image("Bites-Icon")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 200, height: 200, alignment: .topLeading)
                        .border(.blue)
                    Text("Quick Bites")
                        .foregroundColor(.black)
                        .font(.system(size: 32, weight: .bold, design: .serif))
                    
                    TextField("Enter your food descriptions here", text: $query)
                        .font(.system(size: 20))
                        .background(.white)
                        .frame(alignment: .center)
                        .multilineTextAlignment(.center)
                        .cornerRadius(15, antialiased: false)
                        .padding(10)
                    
                    Toggle("Vegan", isOn: $isVegan)
                    Toggle("Open Now", isOn: $isOpenNow)
                    Toggle("Personalize (Beta)", isOn: $isPersonalized)
                        .tint(.purple)
                    
                    Picker("Meal", selection: $meal) {
                        Text("Any").tag("")
                        Text("Breakfast").tag("breakfast")
                        Text("Lunch").tag("lunch")
                        Text("Dinner").tag("dinner")
                    }
                    .pickerStyle(.segmented)
                    
                    Picker("Distance From", selection: $origin) {
                        Text("📍 Current").tag("current")
                        Text("🚗 Commute").tag("commute")
                    }
                    .pickerStyle(.segmented)
                    
                    VStack(alignment: .leading) {
                        Text("Distance vs Quality: \(distanceWeight < 0.3 ? "Quality First" : distanceWeight > 0.7 ? "Closest First" : "Balanced")")
                            .font(.caption)
                        Slider(value: $distanceWeight, in: 0...1, step: 0.1)
                    }
                    
                    Stepper("Price Range: \(priceRange)", value: $priceRange, in: 1...4)
                    
                    Button {
                        print("Location:", locationManager.userLocation ?? "nil")
                        Task {
                            await vm.search(
                                keywords: query,
                                maxPrice: priceRange,
                                meal: meal,
                                isVegan: isVegan,
                                isOpenNow: isOpenNow,
                                personalize: isPersonalized,
                                lat: locationManager.userLocation?.coordinate.latitude,
                                lon: locationManager.userLocation?.coordinate.longitude,
                                origin: origin,
                                distanceWeight: distanceWeight
                            )
                        }
                    } label: {
                        Text("Search")
                            .font(.system(size: 20, weight: .medium, design: .serif))
                            .foregroundColor(.black)
                            .padding(10)
                            .border(.black)
                            .background(.white)
                    }
                }
                .padding()
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbarBackground(Color.teal, for: .navigationBar)
            .toolbarBackground(.visible, for: .navigationBar)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showProfile = true
                    } label: {
                        Image(systemName: "person.circle")
                            .foregroundStyle(.white)
                            .font(.title2)
                    }
                }
            }
            .sheet(isPresented: $showProfile) {
                ProfileView()
            }
        }
    }
}
