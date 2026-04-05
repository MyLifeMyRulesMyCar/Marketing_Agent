def simplify_trends(raw_data):
    if not raw_data:
        return None

    interest = raw_data.get("interest_over_time", {})
    timeline = interest.get("timeline_data", [])

    parsed = []

    for point in timeline:
        parsed.append({
            "date": point.get("date"),
            "value": point.get("values", [{}])[0].get("value")
        })

    return parsed
