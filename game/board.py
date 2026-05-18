from route import Route, RouteColor

C = RouteColor


class Board:
    def __init__(self):
        self.cities: dict[str, tuple[int, int]] = {
            "King's Cross": (200, 50),
            "Regent's Park": (100, 50),
            "Baker Street": (40, 100),
            "The Charterhouse": (300, 100),
            "Brick Lane": (450, 110),
            "British Museum": (200, 140),
            "St Paul's": (340, 170),
            "Tower of London": (460, 220),
            "Piccadilly Circus": (150, 200),
            "Covent Garden": (220, 200),
            "Trafalgar Square": (200, 250),
            "Globe Theatre": (350, 240),
            "Waterloo": (270, 260),
            "Hyde Park": (60, 270),
            "Buckingham Palace": (120, 300),
            "Big Ben": (220, 300),
            "Elephant & Castle": (340, 330),
        }

        self.routes: list[Route] = [
            # Blue
            Route("Regent's Park", "Baker Street", 2, C.BLUE),
            Route("Waterloo", "Big Ben", 1, C.BLUE),
            Route("The Charterhouse", "British Museum", 4, C.BLUE),
            Route("Brick Lane", "Tower of London", 3, C.BLUE),
            # Green
            Route("King's Cross", "Regent's Park", 3, C.GREEN),
            Route("Buckingham Palace", "Big Ben", 2, C.GREEN),
            Route("Globe Theatre", "Elephant & Castle", 2, C.GREEN),
            Route("Brick Lane", "The Charterhouse", 3, C.GREEN),
            # Black
            Route("King's Cross", "British Museum", 2, C.BLACK),
            Route("Baker Street", "Hyde Park", 4, C.BLACK),
            Route("The Charterhouse", "St Paul's", 1, C.BLACK),
            # Ferry: Tower of London → Elephant & Castle — 1 loco required
            Route("Tower of London", "Elephant & Castle", 4, C.BLACK, ferry_locos=1),
            # Yellow
            Route("Regent's Park", "British Museum", 3, C.YELLOW),
            Route("Big Ben", "Elephant & Castle", 3, C.YELLOW),
            # Orange
            Route("Baker Street", "British Museum", 4, C.ORANGE),
            Route("Waterloo", "Elephant & Castle", 2, C.ORANGE),
            Route("Brick Lane", "St Paul's", 3, C.ORANGE),
            # Pink
            Route("Buckingham Palace", "Piccadilly Circus", 2, C.PINK),
            Route("Waterloo", "Globe Theatre", 2, C.PINK),
            Route("The Charterhouse", "King's Cross", 3, C.PINK),
            # Gray (no color — wild)
            Route("Baker Street", "Piccadilly Circus", 4),
            Route("Buckingham Palace", "Trafalgar Square", 2),
            Route("Piccadilly Circus", "British Museum", 2),
            # Ferry: Trafalgar Square → Waterloo — 1 loco required
            Route("Trafalgar Square", "Waterloo", 2, ferry_locos=1),
            Route("Trafalgar Square", "Big Ben", 1),
            # Ferry: Globe Theatre → Tower of London — 2 locos required
            Route("Globe Theatre", "Tower of London", 3, ferry_locos=2),
            # Double routes
            Route("Hyde Park", "Piccadilly Circus", 2),
            Route("Hyde Park", "Piccadilly Circus", 2, C.BLUE),
            Route("Hyde Park", "Buckingham Palace", 1, C.ORANGE),
            Route("Hyde Park", "Buckingham Palace", 1, C.YELLOW),
            Route("Piccadilly Circus", "Covent Garden", 1, C.GREEN),
            Route("Piccadilly Circus", "Covent Garden", 1, C.YELLOW),
            Route("Piccadilly Circus", "Trafalgar Square", 1, C.BLUE),
            Route("Piccadilly Circus", "Trafalgar Square", 1, C.ORANGE),
            Route("Covent Garden", "British Museum", 1),
            Route("Covent Garden", "British Museum", 1),
            Route("Covent Garden", "Trafalgar Square", 1, C.BLACK),
            Route("Covent Garden", "Trafalgar Square", 1, C.PINK),
            Route("Globe Theatre", "St Paul's", 1),
            Route("Globe Theatre", "St Paul's", 1),
            Route("St Paul's", "Tower of London", 3, C.YELLOW),
            Route("St Paul's", "Tower of London", 3, C.PINK),
            Route("St Paul's", "Covent Garden", 3),
            Route("St Paul's", "Covent Garden", 3),
        ]

    def get_routes(self, city_a: str, city_b: str) -> list[Route]:
        return [r for r in self.routes if r.connects(city_a, city_b)]

    def get_bounds(self) -> tuple[int, int, int, int]:
        xs = [x for x, _ in self.cities.values()]
        ys = [y for _, y in self.cities.values()]
        return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)