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
    @State private var query: String = ""
    @State private var isVegan = false
    @State private var isOpenNow = true
    @State private var priceRange = 2
    @State private var meal = "morning"
    
    @ObservedObject var vm: RecommendationViewModel
    
    var body: some View {
        ZStack{
            Rectangle()
                .fill(Color.teal)
            VStack {
                Image("Bites-Icon")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 200, height: 200, alignment: .topLeading)
                    .border(.blue)
                Text("Quick Bites")
                    .foregroundColor(.black)
                    .font(.system(size: 32, weight: .bold, design: .serif))
                
                TextField("Enter your food descriptions here",text:$query)
                {}
                    .font(.system(size: 20))
                    .background(.white)
                    .frame(alignment: .center)
                    .multilineTextAlignment(.center)
                    .cornerRadius(15, antialiased: false)
                    .padding(10)
                Toggle("Vegan", isOn: $isVegan)
                Toggle("Open Now", isOn: $isOpenNow)
                Stepper("Price Range: \(priceRange)", value: $priceRange, in: 1...4)

                Button {
                    Task {
                        await vm.search(
                            keywords: query,
                            maxPrice: priceRange,
                            meal: meal
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
            .onAppear(){
                CLLocationManager().requestWhenInUseAuthorization()
            }
        }
    }


}




//#Preview {
//    ContentView()
//}
