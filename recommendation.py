def recommend_crops(nitrogen, phosphorus, potash, ph, moisture, crop_type, sowing_month, language='en', translations={}):
    recommendations = []
    warnings = []
    t = translations.get(language, translations['en'])

    # Crop suitability rules
    if nitrogen >= 50 and potash >= 40 and 6.0 <= ph <= 8.0 and moisture < 30:
        recommendations.append("Cotton")
    if nitrogen < 50 and ph < 6.5:
        recommendations.append("Finger Millet")
    if moisture > 40 and ph < 6.5:
        recommendations.append("Paddy")
    if nitrogen > 40 and ph >= 6.0 and moisture < 35:
        recommendations.append("Wheat")
    if nitrogen > 30 and phosphorus > 20 and moisture > 25:
        recommendations.append("Maize")
    if ph >= 6.5 and moisture < 30:
        recommendations.append("Groundnut")
    if moisture > 50 and ph >= 6.0:
        recommendations.append("Sugarcane")
    if nitrogen > 40 and moisture < 35:
        recommendations.append("Sunflower")
    if ph >= 6.0 and moisture < 40:
        recommendations.append("Soybean")
    if nitrogen < 50 and moisture < 30:
        recommendations.append("Chickpea")
    if nitrogen > 30 and ph >= 6.0:
        recommendations.append("Red Gram")
    if nitrogen < 40 and moisture < 35:
        recommendations.append("Green Gram")
    if nitrogen < 45 and moisture < 35:
        recommendations.append("Black Gram")

    # Warnings based on soil conditions
    if ph < 5.5 or ph > 8.5:
        warnings.append(t['warning_ph'])
    if moisture < 20:
        warnings.append(t['warning_moisture'])

    # Fallback if no crop matched
    if not recommendations:
        recommendations.append("Finger Millet")
        warnings.append("⚠️ " + t['warning_crop'].replace('ragi', crop_type))

    # Alert if intended crop is not among recommendations
    if crop_type not in recommendations:
        warnings.append(t['warning_crop'].replace('ragi', crop_type))

    return recommendations, warnings