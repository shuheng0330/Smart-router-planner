from route_handler import get_route_info
status, route = get_route_info("Sunway Pyramid", "KL Sentral", mode="transit")
print(status)
print(route)
