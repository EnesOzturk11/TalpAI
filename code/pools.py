"""Curated pools of *specific* values for persona attributes.

Rule: name the thing ("rewatches the Guardians of the Galaxy trilogy"), never the
category ("likes sci-fi"). build_personas.py samples these least-used-first so 300
personas spread across the pools instead of converging.
"""

# Dossier groups, written exactly as in 13-kestrel-air.md. Shares are OUR assumption
# (no public split exists; see research/kestrel-real-world-grounding.md section 5).
GROUPS = {
    "families visiting relatives": 0.35,
    "vacationers": 0.30,
    "students": 0.15,
    "business travelers": 0.12,
    "travel agencies": 0.08,
}

BASES = ("MCO", "PHL")

# Kestrel network (fictional, consistent with the dossier: 75% US, 25% Mexico/Caribbean).
AIRPORTS = {
    "MCO": "Orlando", "PHL": "Philadelphia", "BOS": "Boston", "PVD": "Providence",
    "BDL": "Hartford", "LGA": "New York LaGuardia", "EWR": "Newark", "BWI": "Baltimore",
    "PIT": "Pittsburgh", "CLE": "Cleveland", "CMH": "Columbus", "DTW": "Detroit",
    "MDW": "Chicago Midway", "ATL": "Atlanta", "CLT": "Charlotte", "RDU": "Raleigh-Durham",
    "BNA": "Nashville", "TPA": "Tampa", "FLL": "Fort Lauderdale", "RSW": "Fort Myers",
    "DFW": "Dallas-Fort Worth", "IAH": "Houston", "DEN": "Denver", "LAS": "Las Vegas",
    "SJU": "San Juan", "CUN": "Cancun", "PUJ": "Punta Cana", "MBJ": "Montego Bay",
    "NAS": "Nassau", "AUA": "Aruba", "PVR": "Puerto Vallarta",
}
INTERNATIONAL = {"CUN", "PUJ", "MBJ", "NAS", "AUA", "PVR"}
LEISURE_DESTS = ["MCO", "CUN", "PUJ", "MBJ", "NAS", "AUA", "PVR", "SJU", "FLL", "TPA", "RSW", "LAS"]

# Home metros. weight = share of personas living there (our assumption: bases over-weighted
# because 6 in 10 Kestrel flights touch MCO or PHL). places: (place, state, area type).
METROS = {
    "Orlando": {"airport": "MCO", "weight": 0.18,
        "places": [("Orlando (Thornton Park)", "FL", "city"), ("Winter Park", "FL", "suburb"),
                   ("Kissimmee", "FL", "suburb"), ("Sanford", "FL", "suburb"), ("Clermont", "FL", "small town"),
                   ("St. Cloud", "FL", "small town"), ("Apopka", "FL", "suburb"), ("rural Lake County near Umatilla", "FL", "rural")],
        "news": ["Orlando Sentinel app", "WFTV Channel 9 Eyewitness News", "WESH 2 News", "r/orlando", "Spectrum News 13", "the Nextdoor feed for their neighborhood"],
        "teams": ["Orlando Magic", "Orlando City SC", "UCF Knights football", "Orlando Pride"]},
    "Philadelphia": {"airport": "PHL", "weight": 0.22,
        "places": [("South Philadelphia", "PA", "city"), ("Fishtown, Philadelphia", "PA", "city"), ("Manayunk, Philadelphia", "PA", "city"),
                   ("Cherry Hill", "NJ", "suburb"), ("Upper Darby", "PA", "suburb"), ("King of Prussia", "PA", "suburb"),
                   ("Media", "PA", "small town"), ("Wilmington", "DE", "city"), ("rural Chester County near Oxford", "PA", "rural")],
        "news": ["Philadelphia Inquirer app", "NBC10 Philadelphia", "6abc Action News", "WHYY / NPR", "r/philadelphia", "Billy Penn newsletter", "KYW Newsradio 1060"],
        "teams": ["Philadelphia Eagles", "Philadelphia Phillies", "Philadelphia 76ers", "Philadelphia Flyers", "Philadelphia Union", "Villanova basketball"]},
    "Boston": {"airport": "BOS", "weight": 0.05,
        "places": [("Dorchester, Boston", "MA", "city"), ("Quincy", "MA", "suburb"), ("Worcester", "MA", "city"), ("Plymouth", "MA", "small town")],
        "news": ["Boston Globe app", "WCVB Channel 5", "WBUR", "r/boston", "Universal Hub"],
        "teams": ["Boston Red Sox", "New England Patriots", "Boston Celtics", "Boston Bruins"]},
    "Providence": {"airport": "PVD", "weight": 0.02,
        "places": [("Providence (Federal Hill)", "RI", "city"), ("Warwick", "RI", "suburb"), ("Fall River", "MA", "city")],
        "news": ["Providence Journal", "WPRI 12", "Boston Globe Rhode Island edition"],
        "teams": ["Boston Red Sox", "Providence College basketball", "New England Patriots"]},
    "Hartford": {"airport": "BDL", "weight": 0.03,
        "places": [("West Hartford", "CT", "suburb"), ("New Britain", "CT", "city"), ("Springfield", "MA", "city"), ("rural Tolland County", "CT", "rural")],
        "news": ["Hartford Courant", "NBC Connecticut", "WTNH News 8", "CT Mirror"],
        "teams": ["UConn Huskies women's basketball", "New York Yankees", "Hartford Yard Goats", "Boston Bruins"]},
    "New York": {"airport": "LGA", "weight": 0.06,
        "places": [("Astoria, Queens", "NY", "city"), ("Washington Heights, Manhattan", "NY", "city"), ("Bay Ridge, Brooklyn", "NY", "city"),
                   ("Yonkers", "NY", "suburb"), ("Hicksville, Long Island", "NY", "suburb")],
        "news": ["NY1 Spectrum News", "Gothamist", "New York Post", "r/nyc", "News 12 Long Island", "Hell Gate"],
        "teams": ["New York Mets", "New York Yankees", "New York Knicks", "New York Giants", "New York Liberty", "New York Islanders"]},
    "Newark": {"airport": "EWR", "weight": 0.03,
        "places": [("Newark (Ironbound)", "NJ", "city"), ("Edison", "NJ", "suburb"), ("Toms River", "NJ", "suburb"), ("Morristown", "NJ", "small town")],
        "news": ["NJ.com / Star-Ledger", "News 12 New Jersey", "NJ Spotlight News"],
        "teams": ["New York Giants", "New Jersey Devils", "Rutgers Scarlet Knights", "New York Jets"]},
    "Baltimore": {"airport": "BWI", "weight": 0.04,
        "places": [("Hampden, Baltimore", "MD", "city"), ("Columbia", "MD", "suburb"), ("Glen Burnie", "MD", "suburb"),
                   ("Silver Spring", "MD", "suburb"), ("Arlington", "VA", "suburb")],
        "news": ["Baltimore Banner", "WBAL-TV 11", "Washington Post app", "WTOP News", "r/baltimore"],
        "teams": ["Baltimore Ravens", "Baltimore Orioles", "Washington Capitals", "Washington Commanders"]},
    "Pittsburgh": {"airport": "PIT", "weight": 0.04,
        "places": [("Lawrenceville, Pittsburgh", "PA", "city"), ("Bethel Park", "PA", "suburb"), ("Greensburg", "PA", "small town"), ("rural Butler County", "PA", "rural")],
        "news": ["Pittsburgh Post-Gazette", "KDKA-TV", "WESA", "r/pittsburgh", "TribLive"],
        "teams": ["Pittsburgh Steelers", "Pittsburgh Penguins", "Pittsburgh Pirates", "Pitt Panthers"]},
    "Cleveland": {"airport": "CLE", "weight": 0.03,
        "places": [("Lakewood", "OH", "suburb"), ("Parma", "OH", "suburb"), ("Akron", "OH", "city"), ("Sandusky", "OH", "small town")],
        "news": ["Cleveland.com / Plain Dealer", "WKYC Channel 3", "Signal Cleveland", "Akron Beacon Journal"],
        "teams": ["Cleveland Browns", "Cleveland Cavaliers", "Cleveland Guardians", "Ohio State Buckeyes"]},
    "Columbus": {"airport": "CMH", "weight": 0.03,
        "places": [("Clintonville, Columbus", "OH", "city"), ("Dublin", "OH", "suburb"), ("Westerville", "OH", "suburb"), ("rural Delaware County", "OH", "rural")],
        "news": ["Columbus Dispatch", "NBC4 Columbus", "WOSU", "r/Columbus"],
        "teams": ["Ohio State Buckeyes", "Columbus Blue Jackets", "Columbus Crew", "Cincinnati Bengals"]},
    "Detroit": {"airport": "DTW", "weight": 0.03,
        "places": [("Corktown, Detroit", "MI", "city"), ("Dearborn", "MI", "suburb"), ("Royal Oak", "MI", "suburb"), ("Ypsilanti", "MI", "small town")],
        "news": ["Detroit Free Press", "WDIV Local 4", "Outlier Media text alerts", "WDET"],
        "teams": ["Detroit Lions", "Detroit Tigers", "Detroit Red Wings", "Michigan Wolverines", "Detroit Pistons"]},
    "Chicago": {"airport": "MDW", "weight": 0.04,
        "places": [("Pilsen, Chicago", "IL", "city"), ("Logan Square, Chicago", "IL", "city"), ("Oak Lawn", "IL", "suburb"),
                   ("Naperville", "IL", "suburb"), ("Joliet", "IL", "city")],
        "news": ["Chicago Tribune", "Block Club Chicago", "WGN-TV", "WBEZ", "Chicago Sun-Times"],
        "teams": ["Chicago Cubs", "Chicago White Sox", "Chicago Bears", "Chicago Bulls", "Chicago Sky"]},
    "Atlanta": {"airport": "ATL", "weight": 0.04,
        "places": [("East Atlanta Village", "GA", "city"), ("Decatur", "GA", "suburb"), ("Marietta", "GA", "suburb"), ("Lawrenceville", "GA", "suburb")],
        "news": ["Atlanta Journal-Constitution", "11Alive WXIA", "WSB-TV", "WABE"],
        "teams": ["Atlanta Braves", "Atlanta Falcons", "Atlanta Hawks", "Atlanta United", "Georgia Bulldogs"]},
    "Charlotte": {"airport": "CLT", "weight": 0.03,
        "places": [("NoDa, Charlotte", "NC", "city"), ("Matthews", "NC", "suburb"), ("Rock Hill", "SC", "suburb"), ("Mooresville", "NC", "small town")],
        "news": ["Charlotte Observer", "WBTV 3", "WFAE", "Axios Charlotte newsletter"],
        "teams": ["Carolina Panthers", "Charlotte Hornets", "Charlotte FC", "NASCAR (Hendrick Motorsports)"]},
    "Raleigh": {"airport": "RDU", "weight": 0.02,
        "places": [("Durham", "NC", "city"), ("Cary", "NC", "suburb"), ("Wake Forest", "NC", "small town")],
        "news": ["News & Observer", "WRAL", "WUNC"],
        "teams": ["Carolina Hurricanes", "UNC Tar Heels basketball", "NC State Wolfpack", "Duke basketball"]},
    "Nashville": {"airport": "BNA", "weight": 0.02,
        "places": [("East Nashville", "TN", "city"), ("Murfreesboro", "TN", "suburb"), ("Franklin", "TN", "suburb")],
        "news": ["The Tennessean", "WSMV 4", "Nashville Banner"],
        "teams": ["Tennessee Titans", "Nashville Predators", "Nashville SC", "Tennessee Volunteers"]},
    "Tampa": {"airport": "TPA", "weight": 0.03,
        "places": [("Seminole Heights, Tampa", "FL", "city"), ("Brandon", "FL", "suburb"), ("St. Petersburg", "FL", "city"), ("Plant City", "FL", "small town")],
        "news": ["Tampa Bay Times", "WFLA News Channel 8", "Bay News 9", "r/tampa"],
        "teams": ["Tampa Bay Buccaneers", "Tampa Bay Lightning", "Tampa Bay Rays"]},
    "South Florida": {"airport": "FLL", "weight": 0.03,
        "places": [("Hollywood", "FL", "suburb"), ("Little Havana, Miami", "FL", "city"), ("Pembroke Pines", "FL", "suburb"), ("Homestead", "FL", "small town")],
        "news": ["Miami Herald", "Sun Sentinel", "WSVN 7News", "Univision 23", "WLRN"],
        "teams": ["Miami Dolphins", "Miami Heat", "Florida Panthers", "Inter Miami CF", "Miami Hurricanes"]},
    "Dallas": {"airport": "DFW", "weight": 0.02,
        "places": [("Oak Cliff, Dallas", "TX", "city"), ("Plano", "TX", "suburb"), ("Arlington", "TX", "suburb")],
        "news": ["Dallas Morning News", "WFAA 8", "KERA"],
        "teams": ["Dallas Cowboys", "Dallas Mavericks", "Texas Rangers", "Dallas Stars"]},
    "Houston": {"airport": "IAH", "weight": 0.02,
        "places": [("The Heights, Houston", "TX", "city"), ("Katy", "TX", "suburb"), ("Pasadena", "TX", "suburb")],
        "news": ["Houston Chronicle", "KHOU 11", "Houston Public Media"],
        "teams": ["Houston Astros", "Houston Texans", "Houston Rockets", "Houston Dynamo"]},
    "Denver": {"airport": "DEN", "weight": 0.01,
        "places": [("Baker, Denver", "CO", "city"), ("Aurora", "CO", "suburb"), ("Longmont", "CO", "small town")],
        "news": ["Denver Post", "Denverite", "9News KUSA", "Colorado Public Radio"],
        "teams": ["Denver Broncos", "Denver Nuggets", "Colorado Avalanche", "Colorado Rockies"]},
    "San Juan": {"airport": "SJU", "weight": 0.01,
        "places": [("Santurce, San Juan", "PR", "city"), ("Bayamón", "PR", "suburb"), ("Carolina", "PR", "suburb")],
        "news": ["El Nuevo Día", "Telemundo Puerto Rico", "NotiCel"],
        "teams": ["Cangrejeros de Santurce (winter baseball)", "Puerto Rico national basketball team", "Criollos de Caguas"]},
}

RELATIVES = [  # (who and where, airport they fly into)
    ("their mother in a 55+ community in The Villages, an hour from Orlando", "MCO"), ("grandparents in a condo in Kissimmee", "MCO"),
    ("a sister who just had twins in Winter Garden", "MCO"), ("their father, recently widowed, in Northeast Philadelphia", "PHL"),
    ("in-laws in a row house in South Philly", "PHL"), ("a brother stationed at MacDill Air Force Base in Tampa", "TPA"),
    ("their grandmother in Bayamón, Puerto Rico", "SJU"), ("cousins in Cherry Hill who host a big Christmas Eve dinner", "PHL"),
    ("an aunt in Fort Lauderdale who has hosted Christmas since 1998", "FLL"), ("their adult daughter in Atlanta", "ATL"),
    ("parents who retired to Port St. Lucie (fly into Orlando, drive 2 hours)", "MCO"), ("an uncle recovering from knee surgery in Pittsburgh", "PIT"),
    ("their son, who lives with his other parent in Charlotte (alternating holidays)", "CLT"), ("a godmother in Dorchester, Boston", "BOS"),
    ("their college-aged kids' grandparents in Columbus", "CMH"), ("a stepfather in Detroit they reconnected with last year", "DTW"),
    ("a grandfather turning 90 this holiday season in Clermont", "MCO"), ("a niece's first Christmas in Raleigh", "RDU"),
    ("parents in the Fishtown twin house they grew up in", "PHL"), ("in-laws who run a diner in Toms River", "EWR"),
    ("their twin brother's family in Naperville", "MDW"), ("an elderly mother in assisted living in Sanford", "MCO"),
    ("a great-aunt in Hartford who is 'probably hosting for the last time'", "BDL"), ("their older brother's new family in Nashville", "BNA"),
    ("a best friend who is practically family, in Houston", "IAH"), ("grandparents in Montego Bay, Jamaica", "MBJ"),
    ("cousins in Cancun who work in hotels", "CUN"), ("a father in Baltimore who just retired from the port", "BWI"),
]

COLLEGES = [  # (college, airport) for students
    ("University of Central Florida, Orlando", "MCO"), ("Temple University, Philadelphia", "PHL"),
    ("Drexel University, Philadelphia", "PHL"), ("University of Florida, Gainesville (drives to MCO)", "MCO"),
    ("Penn State University Park (bus to PHL)", "PHL"), ("Rollins College, Winter Park", "MCO"),
    ("Rowan University, Glassboro NJ", "PHL"), ("Valencia College, Orlando (community college)", "MCO"),
    ("Community College of Philadelphia", "PHL"), ("Full Sail University, Winter Park", "MCO"),
    ("West Chester University", "PHL"), ("Embry-Riddle Aeronautical University, Daytona Beach", "MCO"),
    ("Saint Joseph's University, Philadelphia", "PHL"), ("Stetson University, DeLand", "MCO"),
    ("University of Delaware, Newark DE", "PHL"), ("Florida A&M University, Tallahassee (drives to MCO)", "MCO"),
]
STUDENT_MAJORS = [
    "mechanical engineering", "nursing (BSN, clinicals start in January)", "film production", "accounting",
    "aerospace engineering", "hospitality management (works at a Disney resort)", "biology, pre-med",
    "computer science", "criminal justice", "elementary education", "graphic design", "kinesiology",
    "music business", "marketing", "political science", "architecture", "game design", "dental hygiene",
]

OCCUPATIONS = {  # by group; (occupation, employment status, employer type)
    "families visiting relatives": [
        ("ICU nurse at AdventHealth Orlando", "full-time", "private"), ("USPS letter carrier", "full-time", "federal government"),
        ("SEPTA bus operator", "full-time", "state or local government"), ("dental office manager", "full-time", "private"),
        ("HVAC technician", "full-time", "private"), ("third-grade teacher", "full-time", "state or local government"),
        ("Amazon warehouse shift lead", "full-time", "private"), ("pharmacy technician at CVS", "full-time", "private"),
        ("electrician (IBEW Local 98)", "full-time", "private"), ("medical billing specialist, works from home", "full-time", "private"),
        ("school bus driver", "part-time", "state or local government"), ("hair stylist renting a chair", "self-employed", "self"),
        ("retired Philadelphia firefighter", "retired", "state or local government"), ("Uber and DoorDash driver", "gig", "self"),
        ("Walmart assistant store manager", "full-time", "private"), ("TSA officer", "full-time", "federal government"),
        ("retired Ford assembly worker", "retired", "private"), ("bank teller at Wells Fargo", "full-time", "private"),
        ("home health aide", "part-time", "private"), ("VA hospital lab technician", "full-time", "federal government"),
        ("stay-at-home parent, sells crochet blankets on Etsy", "part-time", "self"), ("Comcast field technician", "full-time", "private"),
        ("insurance claims adjuster", "full-time", "private"), ("restaurant line cook", "full-time", "private"),
    ],
    "vacationers": [
        ("retired high-school chemistry teacher", "retired", "state or local government"), ("software QA tester", "full-time", "private"),
        ("real-estate agent at Keller Williams", "self-employed", "self"), ("physical therapist", "full-time", "private"),
        ("bartender at a Center City hotel", "full-time", "private"), ("retired Navy chief petty officer", "retired", "federal government"),
        ("Disney cast member (Magic Kingdom attractions)", "full-time", "private"), ("paralegal", "full-time", "private"),
        ("wedding photographer", "self-employed", "self"), ("dental hygienist", "part-time", "private"),
        ("Verizon store manager", "full-time", "private"), ("county 911 dispatcher", "full-time", "state or local government"),
        ("freelance UX designer", "self-employed", "self"), ("retired UPS driver", "retired", "private"),
        ("personal trainer at Planet Fitness", "part-time", "private"), ("payroll specialist", "full-time", "private"),
        ("nail salon owner", "self-employed", "self"), ("Philadelphia public-school counselor", "full-time", "state or local government"),
        ("traveling ultrasound tech", "full-time", "private"), ("semi-retired accountant doing tax season only", "part-time", "self"),
        ("Starbucks shift supervisor", "full-time", "private"), ("plumber", "self-employed", "self"),
    ],
    "students": [("student", "student", "private"), ("student with a part-time campus job", "student", "state or local government"),
                 ("student working weekends at Target", "student", "private"), ("student doing DoorDash between classes", "student", "self")],
    "business travelers": [
        ("owner of a 6-person landscaping company", "self-employed", "self"), ("regional sales rep for a dental-supply distributor", "full-time", "private"),
        ("independent IT consultant (small-business networks)", "self-employed", "self"), ("food-truck owner scouting a second location", "self-employed", "self"),
        ("event AV technician (trade shows)", "gig", "self"), ("franchise owner of two Jersey Mike's", "self-employed", "self"),
        ("travel nurse recruiter", "full-time", "private"), ("solar-panel installation project manager", "full-time", "private"),
        ("owner of a custom-cabinet shop", "self-employed", "self"), ("pharmaceutical sales rep", "full-time", "private"),
        ("wedding DJ who books destination gigs", "self-employed", "self"), ("construction safety inspector", "full-time", "private"),
        ("bookkeeper with 14 small-business clients", "self-employed", "self"), ("commercial-kitchen equipment installer", "full-time", "private"),
    ],
    "travel agencies": [
        ("owner of a 3-person storefront travel agency", "self-employed", "self"), ("group-travel coordinator at a home-based agency (host agency affiliate)", "self-employed", "self"),
        ("youth-sports tournament travel planner", "full-time", "private"), ("senior-center trip organizer (paid part-time)", "part-time", "state or local government"),
        ("destination-wedding planner who books guest blocks", "self-employed", "self"), ("school band and choir trip agent", "full-time", "private"),
    ],
}

AGENCY_GROUPS = [  # (the group, destination airport)
    ("a 24-person high-school marching band performing at a theme-park holiday parade", "MCO"),
    ("18 retirees from a Delaware County senior center starting a Caribbean cruise in San Juan", "SJU"),
    ("a 30-guest destination wedding in Punta Cana", "PUJ"),
    ("a 16-player U12 girls' soccer team going to a showcase tournament near Orlando", "MCO"),
    ("12 nurses from the same hospital unit taking a post-holiday trip to Cancun", "CUN"),
    ("a 22-person family reunion in Montego Bay", "MBJ"),
    ("14 members of a running club going to a runDisney race weekend", "MCO"),
    ("20 high-school seniors and 4 chaperones on a college-visit trip to Philadelphia", "PHL"),
    ("a 10-person roofing crew on a company reward trip to Nassau", "NAS"),
    ("26 members of a Pittsburgh bowling league on their annual Las Vegas trip", "LAS"),
    ("a 15-person cheer squad competing at a winter cheer championship in Orlando", "MCO"),
    ("a 19-guest quinceañera group flying to San Juan", "SJU"),
    ("a 28-person community chorus singing a holiday concert in Philadelphia", "PHL"),
    ("a 12-person bachelorette group going to Aruba", "AUA"),
]

BUSINESS_PURPOSES = [  # (purpose, destination airport)
    ("meeting a new commercial client in Tampa", "TPA"), ("an equipment trade show in Orlando", "MCO"),
    ("installing a network for a client chain in Atlanta", "ATL"), ("visiting a supplier warehouse near Philadelphia", "PHL"),
    ("a franchise-owner training week in Charlotte", "CLT"), ("a site survey for a solar job in Fort Myers", "RSW"),
    ("pitching a restaurant group in Boston", "BOS"), ("a year-end client dinner in New York", "LGA"),
    ("running AV for a corporate holiday party in Nashville", "BNA"), ("a two-day certification course in Columbus", "CMH"),
    ("inspecting a construction site in Newark", "EWR"), ("closing a lease for a second shop in Kissimmee", "MCO"),
    ("a distributor meeting in Philadelphia's Navy Yard", "PHL"), ("a hotel-renovation bid walk-through in Orlando", "MCO"),
    ("a client audit in Pittsburgh", "PIT"), ("a resort-supply sales trip to Cancun", "CUN"),
]

TV_SHOWS = [
    "rewatches The Office (US) every winter", "is mid-way through Severance season 2", "never misses Love Island USA",
    "watches every episode of Abbott Elementary (it's set in Philly)", "binges Grey's Anatomy from season 1 again",
    "follows The Bear on Hulu", "watches Jeopardy! with their mom every night", "is obsessed with Ted Lasso",
    "watches 90 Day Fiancé ironically, then sincerely", "keeps Yellowstone on in the background", "rewatches Gilmore Girls each fall",
    "loves Bluey (watches it with their kid and secretly alone)", "follows The Last of Us on HBO", "watches Wheel of Fortune at 7pm sharp",
    "stays up for Saturday Night Live cold opens", "is rewatching Breaking Bad with their partner", "follows Shark Tank for business ideas",
    "watches Below Deck Mediterranean", "is hooked on Squid Game", "watches The Golden Bachelor", "loves Great British Bake Off",
    "watches Diners, Drive-Ins and Dives reruns", "follows Hell's Kitchen", "rewatches Friends on Max", "watches Survivor every season since 2001",
    "watches Only Murders in the Building", "binges Bridgerton the day it drops", "watches The Rookie on ABC", "follows Outer Banks on Netflix",
    "rewatches Parks and Recreation", "watches Chopped while meal-prepping", "follows the Real Housewives of New Jersey",
    "watches Unsolved Mysteries on Netflix", "follows Fixer Upper reruns on Magnolia", "watches Bob's Burgers with their teenager",
    "is into Shōgun on FX", "watches Hacks on Max", "follows Married at First Sight", "watches Dateline NBC on Fridays",
    "loves It's Always Sunny in Philadelphia", "rewatches The Sopranos once a year", "watches Ghosts on CBS",
    "follows Stranger Things", "watches Wednesday on Netflix", "watches HGTV's House Hunters International and dreams",
    "watches Top Chef", "watches The Kardashians on Hulu", "follows The Walking Dead spin-offs", "watches Station 19 reruns",
    "watches Tracker on CBS", "loves Schitt's Creek", "watches Love Is Blind", "watches Monk reruns", "watches Ancient Aliens on History",
    "watches Cobra Kai", "watches Andor", "watches The Boys on Prime Video", "watches Reacher on Prime Video", "watches Dancing with the Stars",
]

FILMS = [
    "has seen every Marvel Cinematic Universe film in release order, favorite is Guardians of the Galaxy Vol. 3",
    "rewatches the Fast & Furious saga, ride-or-die for Fast Five", "watches Home Alone every December 23rd",
    "can quote all of Elf", "owns the Lord of the Rings extended editions on Blu-ray", "loves Pixar's Coco",
    "saw Wicked in theaters three times", "watches the Harry Potter series every Thanksgiving weekend",
    "is a John Wick franchise fan", "loves Top Gun: Maverick and watches it on every flight it's offered",
    "rewatches The Devil Wears Prada", "a Star Wars original-trilogy purist", "loves Christopher Nolan's Interstellar",
    "watches A Christmas Story marathon on TBS", "watches Mean Girls every October 3rd", "loves Everything Everywhere All at Once",
    "rewatches Rocky and Creed (Philly pride)", "watches Hallmark Christmas movies from November 1", "loves the Spider-Verse animated films",
    "watches Jurassic Park with their kids", "rewatches The Godfather Part II", "loves Barbie (2023)", "loves Oppenheimer",
    "watches National Lampoon's Christmas Vacation every year", "loves the Mission: Impossible series", "watches Encanto on repeat with a toddler",
    "loves Moana and Moana 2", "a horror fan: the Conjuring universe", "loves Dune: Part Two", "rewatches Bad Boys with Will Smith",
    "loves Talladega Nights", "watches The Holiday every Christmas Eve", "a Tyler Perry Madea movies fan", "loves the Shrek films",
    "watches the Toy Story films with their nephew", "loves Pitch Perfect", "watches Die Hard every Christmas (it IS a Christmas movie)",
    "loves Remember the Titans", "rewatches The Notebook", "loves Ocean's Eleven", "a Studio Ghibli fan, Spirited Away first",
    "loves Inside Out 2", "watches Avatar: The Way of Water in 3D whenever possible", "loves Grease", "rewatches Clueless",
]

MUSIC = [
    "Taylor Swift (went to the Eras Tour in Philadelphia)", "Bad Bunny", "Morgan Wallen", "Beyoncé's Cowboy Carter", "Zach Bryan",
    "SZA", "Drake", "Luke Combs", "Olivia Rodrigo", "Kendrick Lamar", "Bruce Springsteen", "Billy Joel", "Fleetwood Mac",
    "Karol G", "Chris Stapleton", "Sabrina Carpenter", "Post Malone's country album", "Metallica", "Foo Fighters",
    "Pearl Jam", "Lizzo", "Stevie Wonder", "Earth, Wind & Fire", "Jill Scott (Philly soul)", "Boyz II Men", "The Roots",
    "Marc Anthony", "Romeo Santos", "Celia Cruz", "Jimmy Buffett and the Coral Reefer Band", "Kenny Chesney", "Dolly Parton",
    "Frank Sinatra Christmas records", "Mariah Carey (from November 1)", "Pentatonix holiday albums", "BTS", "NewJeans",
    "Hozier", "Noah Kahan", "Phoebe Bridgers", "Tyler, the Creator", "Travis Scott", "Doja Cat", "Ariana Grande", "Harry Styles",
    "Ed Sheeran", "The Weeknd", "Coldplay", "Imagine Dragons", "Green Day", "Blink-182", "Paramore", "Lana Del Rey",
    "Chappell Roan", "Shaboozey", "Lainey Wilson", "Jelly Roll", "Garth Brooks", "Bob Marley", "Rebelution (reggae rock)",
    "Gregory Alan Isakov", "lo-fi hip-hop study beats on YouTube", "Yo-Yo Ma", "Wu-Tang Clan", "Meek Mill",
    "Lil Uzi Vert", "Jazmine Sullivan", "Peso Pluma", "Grupo Frontera", "Shakira", "Selena (Quintanilla)", "Gloria Estefan",
]

PODCASTS = [
    "The Points Guy podcast", "Call Her Daddy", "The Joe Rogan Experience", "Crime Junkie", "Serial", "The Daily (NYT)",
    "Up First (NPR)", "Smartless", "New Heights (Jason & Travis Kelce)", "The Bill Simmons Podcast", "Pod Save America",
    "The Ramsey Show (Dave Ramsey)", "Planet Money", "Armchair Expert", "Stuff You Should Know", "My Favorite Murder",
    "Morbid", "This American Life", "Freakonomics Radio", "The Mel Robbins Podcast", "Wait Wait... Don't Tell Me!",
    "The Breakfast Club", "Club Shay Shay", "Pardon My Take", "The Herd with Colin Cowherd", "Dateline: Missing in America",
    "Huberman Lab", "How I Built This", "Conan O'Brien Needs a Friend", "Hidden Brain", "Radiolab", "The Moth",
    "Las Culturistas", "Bad Friends", "Two Hot Takes", "Unlocking Us (Brené Brown)", "Dumb Blonde", "Office Ladies",
    "Disney Dish with Jim Hill", "WDW Radio", "Chris Hogan's Retire Inspired", "Rick Steves Travel Talks",
    "Zero to Travel", "Extra Pack of Peanuts (travel deals)", "The Dan Patrick Show", "Hard Knocks recap pods (Eagles-focused: Birds 365)",
    "Phillies Talk", "The Basement Yard", "The Ezra Klein Show", "Making Sense",
]

ONLINE_COMMUNITIES = [
    "r/travel", "r/awardtravel", "r/disney", "r/WaltDisneyWorld", "r/Flights", "r/delta (though they fly ULCCs)", "r/personalfinance",
    "r/Frugal", "r/povertyfinance", "r/eagles", "r/phillies", "r/OrlandoMagic", "r/college", "r/nursing", "r/smallbusiness",
    "r/Entrepreneur", "r/TravelHacks", "r/onebag", "r/Parenting", "r/daddit", "r/Mommit", "r/Cruise", "r/cancun", "r/puertorico",
    "Facebook group 'Disney World Moms Planning'", "Facebook group 'Cheap Flights from PHL'", "Facebook group 'Orlando Locals'",
    "Facebook group 'Kestrel Air Flyers (unofficial)'", "Going (formerly Scott's Cheap Flights) email alerts", "Thrifty Traveler newsletter",
    "FlyerTalk forums", "TikTok #airporttok", "TikTok #disneytok", "TikTok #nursetok", "Instagram @dealsinaflash", "X (Twitter) aviation accounts",
    "YouTube channel 'Kara and Nate'", "YouTube channel 'Sam Chui'", "YouTube channel 'Wendover Productions'", "Nextdoor",
    "a 40-person family WhatsApp group", "the company Slack #random channel", "a neighborhood parents GroupMe", "Discord server for their gaming clan",
    "Threads", "BlueSky", "LinkedIn (posts weekly)", "Pinterest boards for trip planning", "Snapchat streaks with college friends", "the Ring Neighbors app",
]

HOBBIES = [
    "restores 1980s Schwinn BMX bikes in the garage", "plays pickleball 4 mornings a week at a public court", "bakes sourdough and names the starters",
    "runs half-marathons (last one: Broad Street Run)", "collects Funko Pops of Marvel villains", "fishes for snook off a kayak in the Indian River Lagoon",
    "plays Fortnite with their nephews on weekends", "does Peloton classes with Cody Rigsby", "gardens tomatoes and peppers in raised beds",
    "crochets amigurumi animals for a holiday craft fair", "builds LEGO Star Wars UCS sets", "plays in a Tuesday-night dart league",
    "brews IPA at home", "goes to Disney's EPCOT Food & Wine Festival every weekend it runs", "scuba-diving certification (PADI Advanced)",
    "competitive barbecue (Kansas City style ribs)", "photographs birds at Merritt Island refuge", "plays Pokémon GO raids",
    "salsa dancing on Thursday nights", "coaches their kid's rec-league basketball team", "collects vintage Phillies memorabilia",
    "paints miniatures for Warhammer 40K", "thrifts and resells clothes on Depop", "keeps a reef aquarium", "plays bass in a 90s cover band",
    "does CrossFit at a local box", "volunteers at a dog shelter on Saturdays", "plays Wordle and Connections every morning, posts streaks",
    "drives for fun on the Blue Ridge Parkway", "trains Brazilian jiu-jitsu (blue belt)", "builds custom mechanical keyboards",
    "plays golf on municipal courses at twilight rates", "makes TikToks about budget travel", "does stand-up open mics",
    "quilts with a weekly group", "rides a Harley Sportster on weekends", "plays chess on chess.com (1450 rapid)", "grows orchids",
    "plays in a co-ed softball league", "solves 1000-piece jigsaw puzzles", "volunteers as a Big Brother/Big Sister", "trains for Spartan races",
    "skateboards at a DIY park", "geocaching", "plays Magic: The Gathering at a local game store on Fridays", "does genealogy on Ancestry.com",
    "cosplays at MegaCon Orlando", "collects vinyl at Philly record stores", "does woodworking (cutting boards for gifts)", "goes to drag brunch",
    "surfs at Cocoa Beach", "watches and rates every new Wawa hoagie", "competitive Mario Kart", "paddleboard yoga", "collects sneakers (Jordan 1s)",
    "volunteers as a youth wrestling ref", "races RC cars", "does flower arranging for friends' weddings", "learning Italian on Duolingo (412-day streak)",
    "rebuilding a 1997 Jeep Wrangler", "plays piano at a senior center", "hunts deer in Pennsylvania rifle season", "makes candles to sell at markets",
    "attends every Orlando City home match with a supporters' group", "does trivia nights at the same bar every Wednesday", "keeps backyard chickens",
    "practices tai chi in a park", "plays Animal Crossing", "plays Call of Duty: Warzone late at night", "line dancing at a country bar",
]

PETS = [
    "a 9-year-old beagle", "two rescue cats", "a French bulldog with breathing issues (never flies)", "a bearded dragon", "no pets",
    "no pets (allergic)", "a golden retriever puppy", "a senior chihuahua", "a parakeet", "two guinea pigs", "a pit bull mix from a shelter",
    "a Maine coon", "a goldfish the kids won at a fair", "a German shepherd", "a corn snake", "no pets (landlord rule)", "a rescue greyhound",
    "backyard chickens", "a dachshund who needs a sitter whenever they travel", "a tuxedo cat", "an emotional-support corgi",
]

COFFEE = [
    "Dunkin' medium iced regular", "Wawa French vanilla", "Starbucks venti oat-milk latte", "black, from the office Keurig", "doesn't drink coffee",
    "Café Bustelo at home", "Starbucks Pink Drink (no coffee)", "a cortado from an independent café", "gas-station coffee with 3 creamers",
    "Wawa hazelnut with whole milk", "Dunkin' caramel swirl", "cold brew from a can", "La Colombe draft latte", "Folgers from a drip pot",
    "Dutch Bros (when visiting family)", "Café con leche", "matcha latte", "Celsius energy drink instead", "Diet Coke instead", "espresso, 2 shots",
]

PHONES = ["iPhone 16", "iPhone 15 Pro", "iPhone 13 mini", "iPhone 12 (cracked screen)", "iPhone SE", "Samsung Galaxy S24",
          "Samsung Galaxy A15", "Google Pixel 8a", "Motorola Moto G", "Samsung Galaxy Z Flip", "iPhone 14 Plus", "OnePlus 12"]

PAST_BAD_EXPERIENCES = [
    "was stranded 2 nights in Fort Lauderdale when Spirit shut down on May 2, 2026",
    "lost a checked bag on a Kestrel flight in 2024; it arrived 3 days later, missing a gift",
    "sat on a tarmac for 4 hours at PHL during a 2023 thunderstorm, with no water handed out",
    "got bumped from an oversold flight to Cancun and took a voucher they never used",
    "missed a grandmother's funeral because of a canceled connection in Charlotte",
    "had a wheelchair request ignored on arrival in Orlando; their father waited 50 minutes",
    "paid a $99 gate bag fee on a ULCC and still resents it",
    "was on hold 3 hours with an airline during a 2022 holiday meltdown",
    "had a smooth refund from Kestrel in 2025 after a schedule change (a good experience)",
    "none worth mentioning",
    "none; has never had a flight canceled",
    "a hotel 'free' voucher turned out to be 40 minutes from the airport",
    "missed a cruise departure from San Juan because of a delayed flight",
    "got a rude gate agent response when asking about a missed connection",
    "a delayed flight caused them to miss a paid shift and lose $210 in wages",
    "their child flew as an unaccompanied minor and the handoff was disorganized",
    "had a Kestrel credit expire before they could use it",
    "had a great experience: a Kestrel agent rebooked them in 5 minutes during a 2024 hurricane",
]

LIFE_EVENTS = [
    "new job started in October", "moved apartments in September", "got married in June", "had a baby in August",
    "retired in the spring", "was laid off in September and is job hunting", "divorced last year", "first grandchild born in July",
    "kid started college in August", "bought their first house", "lost a parent this year", "recovered from surgery in the summer",
    "got promoted", "started a small business", "no major change this year", "took on a second job for the holidays",
]

VALUES_MOST = ["family", "saving money", "security", "freedom", "convenience", "status", "time with friends", "personal growth", "reliability"]
