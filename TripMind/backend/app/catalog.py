"""
app/catalog.py
--------------
ONE source of truth for every destination TripMind can plan. Both the seeder
(seed_data.py) and the planner (planner.py) read from here, so the data in the
database and the matching logic can never drift apart again (that mismatch is
what made "a trip to Ahmedabad" silently return Jaipur).

Each destination has: vibes (keywords we match against), good_months, map
coordinates, a flight price base, a hotel nightly base, and a short guide.
"""

# Cities travellers can fly FROM.
ORIGINS = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata",
           "Hyderabad", "Pune", "Ahmedabad"]

# name: (vibes, good_months, lat, lon, flight_base, hotel_base, guide)
DESTINATIONS = {
    "Goa":        (["beach","warm","party","nightlife","coastal","sea","relaxed"], [11,12,1,2,3], 15.2993, 74.1240, 4200, 2600,
        "Goa is India's favourite beach break, warm and dry from November to March. North Goa is lively; the south is calm and green."),
    "Kochi":      (["backwater","kerala","warm","culture","coastal","quiet"], [10,11,12,1,2], 9.9312, 76.2673, 5200, 2400,
        "Kochi mixes backwaters, Chinese fishing nets and colonial Fort Kochi, and is the gateway to Kerala's houseboats."),
    "Munnar":     (["hills","tea","cool","nature","romantic","quiet","mountains"], [9,10,11,12,1,2,3], 10.0889, 77.0595, 5400, 2200,
        "Munnar is a cool hill station wrapped in emerald tea plantations in the Western Ghats, great for couples and nature lovers."),
    "Alleppey":   (["backwater","houseboat","quiet","kerala","romantic","nature"], [11,12,1,2], 9.4981, 76.3388, 5300, 2600,
        "Alleppey is the heart of Kerala's backwaters, best experienced on an overnight houseboat gliding past palms and paddy fields."),
    "Jaipur":     (["heritage","forts","culture","city","shopping","palaces","history"], [10,11,12,1,2,3], 26.9124, 75.7873, 3800, 2300,
        "Jaipur, the Pink City, is full of Rajput forts, palaces and bazaars, best from October to March."),
    "Udaipur":    (["lakes","romantic","heritage","palaces","quiet","culture"], [10,11,12,1,2,3], 24.5854, 73.7125, 4300, 2800,
        "Udaipur is India's most romantic city, built around Lake Pichola with palaces reflected in the water."),
    "Jaisalmer":  (["desert","forts","heritage","camels","dunes","history"], [10,11,12,1,2], 26.9157, 70.9083, 4800, 2200,
        "Jaisalmer is the golden desert city, famous for its living fort and camel safaris into the Thar dunes."),
    "Agra":       (["heritage","monuments","history","taj","culture"], [10,11,12,1,2,3], 27.1767, 78.0081, 3500, 1800,
        "Agra is home to the Taj Mahal, Agra Fort and Fatehpur Sikri, best visited in the cooler winter months."),
    "Ahmedabad":  (["heritage","culture","city","food","history","architecture"], [10,11,12,1,2], 23.0225, 72.5714, 3600, 1900,
        "Ahmedabad is a UNESCO World Heritage city known for its old-town pols, stepwells, street food and Sabarmati riverfront."),
    "Varanasi":   (["spiritual","culture","ghats","history","river","temples"], [10,11,12,1,2], 25.3176, 82.9739, 4200, 1700,
        "Varanasi is one of the world's oldest living cities, famous for its Ganga ghats and the evening aarti ceremony."),
    "Rishikesh":  (["adventure","yoga","river","rafting","spiritual","nature"], [9,10,11,2,3,4], 30.0869, 78.2676, 4000, 1800,
        "Rishikesh on the Ganga is the yoga capital and an adventure hub with white-water rafting and riverside cafes."),
    "Manali":     (["mountains","snow","cold","adventure","hills","trekking"], [12,1,2,3,4,5,6], 32.2432, 77.1892, 5000, 2200,
        "Manali is the classic Himalayan getaway: snow in winter, meadows in summer and adventure sports around Solang Valley."),
    "Shimla":     (["hills","cool","colonial","snow","mountains","views"], [3,4,5,6,12,1], 31.1048, 77.1734, 4800, 2400,
        "Shimla, the old summer capital, offers colonial charm, the Mall Road and toy-train rides through pine hills."),
    "Leh":        (["mountains","adventure","ladakh","monasteries","cold","bikes"], [5,6,7,8,9], 34.1526, 77.5771, 8000, 2500,
        "Leh in Ladakh is a high-altitude desert of stark mountains, blue lakes and Buddhist monasteries, best in summer."),
    "Darjeeling": (["hills","tea","mountains","views","cool","quiet"], [3,4,5,10,11], 27.0360, 88.2627, 4600, 2200,
        "Darjeeling is famous for tea gardens, the toy train and sunrise views of Kanchenjunga from Tiger Hill."),
    "Shillong":   (["hills","waterfalls","nature","cool","music","green"], [3,4,5,9,10,11], 25.5788, 91.8933, 6000, 2200,
        "Shillong, the 'Scotland of the East', is a green hill town of waterfalls, lakes and a lively music scene."),
    "Coorg":      (["hills","coffee","nature","green","quiet","romantic"], [9,10,11,12,1,2], 12.3375, 75.8069, 4500, 2600,
        "Coorg is a misty landscape of coffee estates and forests in Karnataka, perfect for a quiet green escape."),
    "Mysore":     (["heritage","palaces","culture","city","history"], [8,9,10,11,12,1,2], 12.2958, 76.6394, 4200, 2000,
        "Mysore is known for its dazzling illuminated palace, silk, sandalwood and the grand Dasara festival."),
    "Amritsar":   (["heritage","spiritual","food","history","culture"], [10,11,12,1,2,3], 31.6340, 74.8723, 3900, 1900,
        "Amritsar is home to the Golden Temple and the moving Wagah border ceremony, with legendary Punjabi food."),
    "Andaman":    (["beach","warm","island","diving","sea","quiet","coastal"], [11,12,1,2,3,4], 11.6234, 92.7265, 7800, 3400,
        "The Andaman Islands offer some of India's clearest waters, white-sand beaches and world-class scuba diving."),
    "Pondicherry":(["beach","quiet","french","relaxed","coastal","warm","cafes"], [10,11,12,1,2], 11.9416, 79.8083, 3900, 2500,
        "Pondicherry blends French-colonial streets and cafes with a seaside promenade and the nearby Auroville."),
    "Bangkok":    (["city","street","food","nightlife","shopping","temples","warm","budget"], [11,12,1,2], 13.7563, 100.5018, 9000, 2600,
        "Bangkok is a buzzing city of street food, glittering temples and vibrant nightlife, and very budget-friendly."),
    "Bali":       (["beach","tropical","warm","wellness","temples","rice","island","relaxed"], [4,5,6,7,8,9], -8.4095, 115.1889, 13000, 2800,
        "Bali pairs beaches and surf with rice terraces, temples and a strong wellness and cafe culture."),
    "Dubai":      (["city","luxury","shopping","desert","warm","modern","family"], [11,12,1,2,3], 25.2048, 55.2708, 14000, 4000,
        "Dubai is a futuristic city of record-breaking towers, desert safaris, malls and beaches, best in winter."),
    "Singapore":  (["city","modern","food","family","shopping","clean","gardens"], [11,12,1,2,6,7], 1.3521, 103.8198, 15000, 4500,
        "Singapore is a spotless, green city-state of hawker food, futuristic gardens and family attractions."),
    "Maldives":   (["beach","luxury","island","honeymoon","diving","warm","relaxed"], [11,12,1,2,3,4], 3.2028, 73.2207, 22000, 8000,
        "The Maldives is a string of overwater-villa islands with turquoise lagoons and superb diving and snorkelling."),
    "Kathmandu":  (["mountains","spiritual","trekking","culture","temples","adventure"], [3,4,10,11], 27.7172, 85.3240, 8000, 2000,
        "Kathmandu is Nepal's cultural heart, a warren of temples and markets and the launchpad for Himalayan treks."),
}

# Convenience views the planner uses.
DESTINATION_META = {
    name: {"vibes": v, "good_months": m, "lat": lat, "lon": lon}
    for name, (v, m, lat, lon, fb, hb, doc) in DESTINATIONS.items()
}
DEST_NAMES = list(DESTINATIONS.keys())
