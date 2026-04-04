def remove_duplicates(entries):
    seen = set()
    unique = []

    for e in entries:
        key = e["title"].lower()

        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique
