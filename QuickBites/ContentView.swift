//
//  ContentView.swift
//  QuickBites
//
//  Created by Ivan Pham on 2/4/26.
//

import SwiftUI
import MapKit

struct ContentView: View {
    @State private var query: String = ""
    @FocusState private var queryFocused: Bool
    @State private var position: MapCameraPosition = .userLocation(fallback: .automatic)
    
    var body: some View {
        ZStack{
            Rectangle()
                .fill(Color.teal)
            VStack {
                Map (position:$position){
                }
                .mapControls {
                    MapUserLocationButton()
                    MapPitchToggle()
                }
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
                    .focused($queryFocused)
                Button {
                    
                } label: {
                    Text("Fetch Location")
                        .font(.system(size: 20, weight: .medium, design: .serif))
                        .foregroundColor(.black)
                        .padding(10)
                        .border(.black)
                        .background(.white)
                }
                NavigationStack {
                    ResultsView()
                }
                
            }
            .padding()
            .onAppear(){
                CLLocationManager().requestWhenInUseAuthorization()
            }
        }
    }

}


#Preview {
    ContentView()
}
