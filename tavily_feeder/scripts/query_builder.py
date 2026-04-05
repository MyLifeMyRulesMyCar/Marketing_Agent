def build_queries(config):
    queries = []

    for product in config["products"]:
        for q in config["questions"]:
            queries.append(q.replace("{product}", product))

    return queries
