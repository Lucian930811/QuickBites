struct Restaurant: Identifiable, Decodable, Equatable {
    let business_id: String
    let name: String
    let stars: Double
    let review_count: Int
    let score: Double
    let matched_categories: String
    let latitude: Double
    let longitude: Double
    let price_level: Int?
    let address: String?
    let city: String?
    let state: String?
    let hours: String?
    let good_for_meal: String?
    let is_vegan: Bool?  

    var id: String { business_id }

    static func == (lhs: Restaurant, rhs: Restaurant) -> Bool {
        return lhs.id == rhs.id
    }
}
