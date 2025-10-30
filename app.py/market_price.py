def get_crop_price(crop_name):
    crop_prices = {
        'Cotton': 65,
        'Finger Millet': 35,
        'Paddy': 22,
        'Wheat': 24,
        'Maize': 20,
        'Groundnut': 55,
        'Sugarcane': 3,
        'Sunflower': 45,
        'Soybean': 50,
        'Chickpea': 48,
        'Red Gram': 60,
        'Green Gram': 52,
        'Black Gram': 50
    }

    return crop_prices.get(crop_name, 25)  # Default price if not found