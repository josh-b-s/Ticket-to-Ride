import random

def main():
    routes = [
        "Melbourne to Sydney",
        "Perth to Adelaide",
        "Brisbane to Cairns",
        "Hobart to Launceston"
    ]

    print("Random Route Selector")
    input("Press Enter to generate a route: ")

    selected_route = random.choice(routes)
    print("Selected route:", selected_route)

if __name__ == "__main__":
    main()