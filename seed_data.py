"""
Seed testdata till PickCheck-databasen.
Kör med: python seed_data.py
"""
import database as db

PALLETS = [
    {
        "sscc": "173308781029514906",
        "order": "2196231",
        "twoPallets": True,
        "port": "Port 2",
        "lines": [
            {"productNumber": "6617-44832", "product": "TRESemmé Balsam Rich Moisture 685ml x6 (S)", "gtin": "8710447448328", "gtinInner": "8710447448311", "picker": "0251", "pickedQty": 12, "pallet": "A", "correctPallet": "A", "location": "03-12-1A", "packageType": "Ytterbox"},
            {"productNumber": "A25PC017", "product": "Easy Bath Glove Kids Unicorn", "gtin": "5701234567890", "gtinInner": "5701234567883", "picker": "0251", "pickedQty": 12, "pallet": "A", "correctPallet": "A", "location": "03-14-1B", "packageType": "Innerbox"},
            {"productNumber": "HST2301", "product": "Brush Set 2pcs 25mm / 50mm Mixed Bristle", "gtin": "7312345678901", "gtinInner": "7312345678895", "picker": "0251", "pickedQty": 12, "pallet": "A", "correctPallet": "A", "location": "07-22-1C", "packageType": "Innerbox"},
            {"productNumber": "6617-46930", "product": "Duschgel Dove 720ml Dove", "gtin": "8710447469308", "gtinInner": "8710447469292", "picker": "0251", "pickedQty": 24, "pallet": "A", "correctPallet": "A", "location": "03-15-1A", "packageType": "Ytterbox"},
            {"productNumber": "7155", "product": "Flying Disc with Launcher", "gtin": "5412345678901", "gtinInner": "5412345678895", "picker": "0251", "pickedQty": 12, "pallet": "A", "correctPallet": "A", "location": "12-45-1B", "packageType": "Innerbox"},
            {"productNumber": "TK82865", "product": "Tvålkopp Kotikulta Fjord Ljusgrå Kotikulta", "gtin": "6410012345678", "gtinInner": "6410012345661", "picker": "0251", "pickedQty": 6, "pallet": "B", "correctPallet": "B", "location": "15-08-1A", "packageType": "Innerbox"},
            {"productNumber": "1041001K", "product": "Råttfälla Betesstation SuperCat SuperCat", "gtin": "4006123456789", "gtinInner": "4006123456772", "picker": "0251", "pickedQty": 10, "pallet": "A", "correctPallet": "B", "location": "15-10-1C", "packageType": "Ytterbox"},
            {"productNumber": "5138-89289", "product": "Tandkräm Oral B Kids 50ml Oral-B", "gtin": "8001090892898", "gtinInner": "8001090892881", "picker": "0251", "pickedQty": 12, "pallet": "A", "correctPallet": "A", "location": "08-33-1A", "packageType": "Innerbox"},
            {"productNumber": "560-71310", "product": "Wettex 10-pack Wettex", "gtin": "7310791713106", "gtinInner": "7310791713090", "picker": "0251", "pickedQty": 42, "pallet": "B", "correctPallet": "B", "location": "20-05-1B", "packageType": "Ytterbox"},
            {"productNumber": "6617-57529", "product": "Dove Advanced Stick 72h Cucumber 50ml", "gtin": "8710447575291", "gtinInner": "8710447575284", "picker": "0251", "pickedQty": 6, "pallet": "A", "correctPallet": "A", "location": "03-18-1A", "packageType": "Innerbox"},
            {"productNumber": "5661929-60322229405", "product": "Batteri CR2032 5p Tear Off Varta", "gtin": "4008496929405", "gtinInner": "4008496929399", "picker": "0251", "pickedQty": 20, "pallet": "A", "correctPallet": "A", "location": "25-60-1C", "packageType": "Innerbox"},
            {"productNumber": "69615", "product": "Pensel Pro 12mm softgrip Bristle Bristle", "gtin": "7391234567890", "gtinInner": "7391234567883", "picker": "0251", "pickedQty": 24, "pallet": "A", "correctPallet": "A", "location": "07-25-1A", "packageType": "Ytterbox"},
            {"productNumber": "6684-871869769966", "product": "Ljuskälla Philips LED 60W A60 E27", "gtin": "8718697699669", "gtinInner": "8718697699652", "picker": "0251", "pickedQty": 8, "pallet": "A", "correctPallet": "A", "location": "30-42-1B", "packageType": "Innerbox"},
            {"productNumber": "6617-14777", "product": "Zendium Sensitive 2-pack", "gtin": "8710447147771", "gtinInner": "8710447147764", "picker": "0251", "pickedQty": 25, "pallet": "A", "correctPallet": "A", "location": "03-20-1C", "packageType": "Ytterbox"},
            {"productNumber": "6617-26700", "product": "Deodorant Dove Mens Care 72h 50ml Dove Men", "gtin": "8710447267004", "gtinInner": "8710447266991", "picker": "0251", "pickedQty": 12, "pallet": "B", "correctPallet": "A", "location": "03-22-1A", "packageType": "Innerbox"},
            {"productNumber": "6617-27479", "product": "Deodorant Rexona Roll-On 50ml Rexona", "gtin": "8710447274798", "gtinInner": "8710447274781", "picker": "0251", "pickedQty": 12, "pallet": "B", "correctPallet": "B", "location": "03-24-1B", "packageType": "Innerbox"},
        ]
    },
    {
        "sscc": "173308781029514907",
        "order": "2196245",
        "twoPallets": False,
        "port": "Port 52",
        "lines": [
            {"productNumber": "6617-44832", "product": "TRESemmé Balsam Rich Moisture 685ml x6 (S)", "gtin": "8710447448328", "gtinInner": "8710447448311", "picker": "0312", "pickedQty": 6, "pallet": "A", "correctPallet": "A", "location": "03-12-1A", "packageType": "Ytterbox"},
            {"productNumber": "6617-46930", "product": "Duschgel Dove 720ml Dove", "gtin": "8710447469308", "gtinInner": "8710447469292", "picker": "0312", "pickedQty": 18, "pallet": "A", "correctPallet": "A", "location": "03-15-1A", "packageType": "Ytterbox"},
            {"productNumber": "560-71310", "product": "Wettex 10-pack Wettex", "gtin": "7310791713106", "gtinInner": "7310791713090", "picker": "0312", "pickedQty": 30, "pallet": "A", "correctPallet": "A", "location": "20-05-1B", "packageType": "Ytterbox"},
            {"productNumber": "5138-89289", "product": "Tandkräm Oral B Kids 50ml Oral-B", "gtin": "8001090892898", "gtinInner": "8001090892881", "picker": "0312", "pickedQty": 12, "pallet": "A", "correctPallet": "A", "location": "08-33-1A", "packageType": "Innerbox"},
            {"productNumber": "7155", "product": "Flying Disc with Launcher", "gtin": "5412345678901", "gtinInner": "5412345678895", "picker": "0312", "pickedQty": 9, "pallet": "A", "correctPallet": "A", "location": "12-45-1B", "packageType": "Innerbox"},
        ]
    },
    {
        "sscc": "173308781029514908",
        "order": "2196300",
        "twoPallets": False,
        "port": "Port 1",
        "lines": [
            {"productNumber": "6617-44832", "product": "TRESemmé Balsam Rich Moisture 685ml x6 (S)", "gtin": "8710447448328", "gtinInner": "8710447448311", "picker": "0415", "pickedQty": 24, "pallet": "A", "correctPallet": "A", "location": "03-12-1A", "packageType": "Ytterbox"},
            {"productNumber": "A25PC017", "product": "Easy Bath Glove Kids Unicorn", "gtin": "5701234567890", "gtinInner": "5701234567883", "picker": "0415", "pickedQty": 6, "pallet": "A", "correctPallet": "A", "location": "03-14-1B", "packageType": "Innerbox"},
            {"productNumber": "69615", "product": "Pensel Pro 12mm softgrip Bristle Bristle", "gtin": "7391234567890", "gtinInner": "7391234567883", "picker": "0415", "pickedQty": 12, "pallet": "A", "correctPallet": "A", "location": "07-25-1A", "packageType": "Ytterbox"},
        ]
    },
    {
        # Demo: stor order — A och B fylldes, overflow plockades på C-pall (Vardacco/IMI-scenario)
        "sscc": "173308781029514909",
        "order": "2196400",
        "twoPallets": True,
        "port": None,  # Ej skannad av outbound - vid plastmaskin
        "lines": [
            {"productNumber": "6617-44832", "product": "TRESemmé Balsam Rich Moisture 685ml x6 (S)", "gtin": "8710447448328", "gtinInner": "8710447448311", "picker": "0312", "pickedQty": 24, "pallet": "A", "correctPallet": "A", "location": "03-12-1A", "packageType": "Ytterbox"},
            {"productNumber": "6617-46930", "product": "Duschgel Dove 720ml Dove", "gtin": "8710447469308", "gtinInner": "8710447469292", "picker": "0312", "pickedQty": 18, "pallet": "A", "correctPallet": "A", "location": "03-15-1A", "packageType": "Ytterbox"},
            {"productNumber": "HST2301", "product": "Brush Set 2pcs 25mm / 50mm Mixed Bristle", "gtin": "7312345678901", "gtinInner": "7312345678895", "picker": "0312", "pickedQty": 12, "pallet": "A", "correctPallet": "A", "location": "07-22-1C", "packageType": "Innerbox"},
            {"productNumber": "5138-89289", "product": "Tandkräm Oral B Kids 50ml Oral-B", "gtin": "8001090892898", "gtinInner": "8001090892881", "picker": "0312", "pickedQty": 12, "pallet": "A", "correctPallet": "A", "location": "08-33-1A", "packageType": "Innerbox"},
            {"productNumber": "7155", "product": "Flying Disc with Launcher", "gtin": "5412345678901", "gtinInner": "5412345678895", "picker": "0312", "pickedQty": 12, "pallet": "A", "correctPallet": "A", "location": "12-45-1B", "packageType": "Innerbox"},
            {"productNumber": "560-71310", "product": "Wettex 10-pack Wettex", "gtin": "7310791713106", "gtinInner": "7310791713090", "picker": "0312", "pickedQty": 36, "pallet": "B", "correctPallet": "B", "location": "20-05-1B", "packageType": "Ytterbox"},
            {"productNumber": "TK82865", "product": "Tvålkopp Kotikulta Fjord Ljusgrå Kotikulta", "gtin": "6410012345678", "gtinInner": "6410012345661", "picker": "0312", "pickedQty": 12, "pallet": "B", "correctPallet": "B", "location": "15-08-1A", "packageType": "Innerbox"},
            {"productNumber": "6617-57529", "product": "Dove Advanced Stick 72h Cucumber 50ml", "gtin": "8710447575291", "gtinInner": "8710447575284", "picker": "0312", "pickedQty": 12, "pallet": "B", "correctPallet": "B", "location": "03-18-1A", "packageType": "Innerbox"},
            {"productNumber": "69615", "product": "Pensel Pro 12mm softgrip Bristle Bristle", "gtin": "7391234567890", "gtinInner": "7391234567883", "picker": "0312", "pickedQty": 18, "pallet": "B", "correctPallet": "B", "location": "07-25-1A", "packageType": "Ytterbox"},
            {"productNumber": "1041001K", "product": "Råttfälla Betesstation SuperCat SuperCat", "gtin": "4006123456789", "gtinInner": "4006123456772", "picker": "0312", "pickedQty": 10, "pallet": "C", "correctPallet": "C", "location": "15-10-1C", "packageType": "Ytterbox"},
            {"productNumber": "5661929-60322229405", "product": "Batteri CR2032 5p Tear Off Varta", "gtin": "4008496929405", "gtinInner": "4008496929399", "picker": "0312", "pickedQty": 20, "pallet": "C", "correctPallet": "C", "location": "25-60-1C", "packageType": "Innerbox"},
            {"productNumber": "A25PC017", "product": "Easy Bath Glove Kids Unicorn", "gtin": "5701234567890", "gtinInner": "5701234567883", "picker": "0312", "pickedQty": 6, "pallet": "C", "correctPallet": "C", "location": "03-14-1B", "packageType": "Innerbox"},
            {"productNumber": "6617-27479", "product": "Deodorant Rexona Roll-On 50ml Rexona", "gtin": "8710447274798", "gtinInner": "8710447274781", "picker": "0312", "pickedQty": 12, "pallet": "C", "correctPallet": "C", "location": "03-24-1B", "packageType": "Innerbox"},
        ]
    },
    {
        "sscc": "173308781029514920",
        "order": "2196411",
        "twoPallets": True,
        "palletLetter": "A",
        "status": "dropped",
        "port": None,
        "lines": [
            {"productNumber": "6617-44832", "product": "TRESemmé Balsam Rich Moisture 685ml x6 (S)", "gtin": "8710447448328", "gtinInner": "8710447448311", "picker": "0312", "pickedQty": 24, "pallet": "A", "correctPallet": "A", "location": "03-12-1A", "packageType": "Ytterbox"},
            {"productNumber": "6617-46930", "product": "Duschgel Dove 720ml Dove", "gtin": "8710447469308", "gtinInner": "8710447469292", "picker": "0312", "pickedQty": 18, "pallet": "A", "correctPallet": "A", "location": "03-15-1A", "packageType": "Ytterbox"},
        ]
    },
    {
        "sscc": "173308781029514921",
        "order": "2196411",
        "twoPallets": True,
        "palletLetter": "B",
        "status": "on_port",
        "port": "Port 53",
        "lines": [
            {"productNumber": "560-71310", "product": "Wettex 10-pack Wettex", "gtin": "7310791713106", "gtinInner": "7310791713090", "picker": "0312", "pickedQty": 36, "pallet": "B", "correctPallet": "B", "location": "20-05-1B", "packageType": "Ytterbox"},
            {"productNumber": "TK82865", "product": "Tvålkopp Kotikulta Fjord Ljusgrå Kotikulta", "gtin": "6410012345678", "gtinInner": "6410012345661", "picker": "0312", "pickedQty": 12, "pallet": "B", "correctPallet": "B", "location": "15-08-1A", "packageType": "Innerbox"},
        ]
    },
    {
        "sscc": "173308781029514922",
        "order": "2196411",
        "twoPallets": True,
        "palletLetter": "C",
        "status": "picking",
        "port": None,
        "lines": [
            {"productNumber": "1041001K", "product": "Råttfälla Betesstation SuperCat SuperCat", "gtin": "4006123456789", "gtinInner": "4006123456772", "picker": "0312", "pickedQty": 10, "pallet": "C", "correctPallet": "C", "location": "15-10-1C", "packageType": "Ytterbox"},
            {"productNumber": "7155", "product": "Flying Disc with Launcher", "gtin": "5412345678901", "gtinInner": "5412345678895", "picker": "0312", "pickedQty": 12, "pallet": "C", "correctPallet": "C", "location": "12-45-1B", "packageType": "Innerbox"},
        ]
    },
    {
        "sscc": "173308781029514923",
        "order": "2196411",
        "twoPallets": True,
        "palletLetter": "D",
        "status": "picking",
        "port": None,
        "lines": [
            {"productNumber": "6617-27479", "product": "Deodorant Rexona Roll-On 50ml Rexona", "gtin": "8710447274798", "gtinInner": "8710447274781", "picker": "0312", "pickedQty": 12, "pallet": "D", "correctPallet": "D", "location": "03-24-1B", "packageType": "Innerbox"},
            {"productNumber": "A25PC017", "product": "Easy Bath Glove Kids Unicorn", "gtin": "5701234567890", "gtinInner": "5701234567883", "picker": "0312", "pickedQty": 6, "pallet": "D", "correctPallet": "D", "location": "03-14-1B", "packageType": "Innerbox"},
        ]
    }
]


# Produkter som återanvänds till förslags-poolen (andra ID:n än kontrollistan)
_PRODUCTS = [
    {"productNumber": "6617-44832", "product": "TRESemmé Balsam Rich Moisture 685ml x6 (S)", "gtin": "8710447448328", "gtinInner": "8710447448311", "location": "03-12-1A", "packageType": "Ytterbox"},
    {"productNumber": "6617-46930", "product": "Duschgel Dove 720ml Dove", "gtin": "8710447469308", "gtinInner": "8710447469292", "location": "03-15-1A", "packageType": "Ytterbox"},
    {"productNumber": "560-71310", "product": "Wettex 10-pack Wettex", "gtin": "7310791713106", "gtinInner": "7310791713090", "location": "20-05-1B", "packageType": "Ytterbox"},
    {"productNumber": "5138-89289", "product": "Tandkräm Oral B Kids 50ml Oral-B", "gtin": "8001090892898", "gtinInner": "8001090892881", "location": "08-33-1A", "packageType": "Innerbox"},
    {"productNumber": "7155", "product": "Flying Disc with Launcher", "gtin": "5412345678901", "gtinInner": "5412345678895", "location": "12-45-1B", "packageType": "Innerbox"},
    {"productNumber": "A25PC017", "product": "Easy Bath Glove Kids Unicorn", "gtin": "5701234567890", "gtinInner": "5701234567883", "location": "03-14-1B", "packageType": "Innerbox"},
    {"productNumber": "69615", "product": "Pensel Pro 12mm softgrip Bristle Bristle", "gtin": "7391234567890", "gtinInner": "7391234567883", "location": "07-25-1A", "packageType": "Ytterbox"},
    {"productNumber": "TK82865", "product": "Tvålkopp Kotikulta Fjord Ljusgrå Kotikulta", "gtin": "6410012345678", "gtinInner": "6410012345661", "location": "15-08-1A", "packageType": "Innerbox"},
    {"productNumber": "1041001K", "product": "Råttfälla Betesstation SuperCat SuperCat", "gtin": "4006123456789", "gtinInner": "4006123456772", "location": "15-10-1C", "packageType": "Ytterbox"},
    {"productNumber": "6617-57529", "product": "Dove Advanced Stick 72h Cucumber 50ml", "gtin": "8710447575291", "gtinInner": "8710447575284", "location": "03-18-1A", "packageType": "Innerbox"},
    {"productNumber": "HST2301", "product": "Brush Set 2pcs 25mm / 50mm Mixed Bristle", "gtin": "7312345678901", "gtinInner": "7312345678895", "location": "07-22-1C", "packageType": "Innerbox"},
    {"productNumber": "6617-27479", "product": "Deodorant Rexona Roll-On 50ml Rexona", "gtin": "8710447274798", "gtinInner": "8710447274781", "location": "03-24-1B", "packageType": "Innerbox"},
]


def _lines(picker, letter, count, offset=0):
    qtys = (6, 8, 10, 12, 18, 24)
    out = []
    for i in range(count):
        src = _PRODUCTS[(offset + i) % len(_PRODUCTS)]
        out.append({
            **src,
            "picker": picker,
            "pickedQty": qtys[i % len(qtys)],
            "pallet": letter,
            "correctPallet": letter,
        })
    return out


def _sscc(n):
    return f"1733087810295{n:05d}"


# Pool med andra plockar-ID:n — används av auto-förslag när kontrollistans ID:n
# inte har pallar på port. Dessa läggs INTE på kontrollistan.
# picker, order, port, letter, antal rader, ev. extra pallar (letter, port)
_SUGGESTION_SPECS = [
    ("0199", "2197101", "Port 50", "A", 5),
    ("0477", "2197102", "Port 51", "A", 4),
    ("0088", "2197103", "Port 54", "A", 6),
    ("0124", "2197104", "Port 55", "A", 3),
    ("0183", "2197105", "Port 56", "A", 5),
    ("0220", "2197106", "Port 57", "A", 4),
    ("0338", "2197107", "Port 58", "A", 7),
    ("0366", "2197108", "Port 59", "A", 3),
    ("0444", "2197109", "Port 60", "A", 5),
    ("0501", "2197110", "Port 61", "A", 4),
    ("0555", "2197111", "Port 62", "A", 6),
    ("0622", "2197112", "Port 63", "A", 3),
    ("0670", "2197113", "Port 64", "A", 5),
    ("0714", "2197114", "Port 65", "A", 4),
    ("0777", "2197115", "Port 66", "A", 6),
    ("0802", "2197116", "Port 67", "A", 3),
    ("0844", "2197117", "Port 68", "A", 5),
    ("0888", "2197118", "Port 69", "A", 4),
    ("0910", "2197119", "Port 3",  "A", 4),
    ("0988", "2197120", "Port 50", "A", 5),
    ("1023", "2197121", "Port 51", "A", 3),
    ("1105", "2197122", "Port 54", "A", 6),
    ("1188", "2197123", "Port 55", "A", 4),
    ("1240", "2197124", "Port 56", "A", 5),
    ("1302", "2197125", "Port 57", "A", 3),
    ("1377", "2197126", "Port 58", "A", 7),
    ("1420", "2197127", "Port 59", "A", 4),
    ("1488", "2197128", "Port 60", "A", 5),
    ("1533", "2197129", "Port 61", "A", 3),
    ("1601", "2197130", "Port 62", "A", 6),
]

# Extra B-pallar på samma order (så förslaget kan ha A+B)
_SUGGESTION_B = [
    ("0199", "2197101", "Port 50", 4),
    ("0088", "2197103", "Port 54", 5),
    ("0338", "2197107", "Port 58", 4),
    ("0555", "2197111", "Port 62", 3),
    ("0777", "2197115", "Port 66", 5),
    ("1105", "2197122", "Port 54", 4),
    ("1377", "2197126", "Port 58", 3),
    ("1601", "2197130", "Port 62", 4),
]


def build_suggestion_pallets():
    pallets = []
    n = 15001
    for picker, order, port, letter, count in _SUGGESTION_SPECS:
        pallets.append({
            "sscc": _sscc(n),
            "order": order,
            "twoPallets": False,
            "palletLetter": letter,
            "status": "on_port",
            "port": port,
            "lines": _lines(picker, letter, count, offset=n),
        })
        n += 1
    for picker, order, port, count in _SUGGESTION_B:
        pallets.append({
            "sscc": _sscc(n),
            "order": order,
            "twoPallets": True,
            "palletLetter": "B",
            "status": "on_port",
            "port": port,
            "lines": _lines(picker, "B", count, offset=n),
        })
        n += 1
    # Markera A-pallar som twoPallets om samma order har B
    b_orders = {order for _, order, _, _ in _SUGGESTION_B}
    for p in pallets:
        if p["order"] in b_orders:
            p["twoPallets"] = True
    return pallets


SUGGESTION_PALLETS = build_suggestion_pallets()


USERS = [
    {"username": "admin", "password": "admin123", "display_name": "Administrator", "role": "admin"},
    {"username": "krenart", "password": "test", "display_name": "Krenart", "role": "user"},
    {"username": "plockare1", "password": "test", "display_name": "Anna Andersson", "role": "user"},
    {"username": "plockare2", "password": "test", "display_name": "Erik Eriksson", "role": "user"},
]


def seed():
    print("Initierar databas...")
    db.init_db()

    print("Lägger in testanvändare...")
    for u in USERS:
        try:
            db.register_user(u["username"], u["password"], u["display_name"], u["role"])
            print(f"  - {u['username']} ({u['display_name']}, {u['role']})")
        except Exception as e:
            print(f"  - {u['username']} finns redan")

    print("\nLägger in testpallar...")
    for p in PALLETS:
        db.save_pallet(
            sscc=p["sscc"],
            order_number=p["order"],
            two_pallets=p["twoPallets"],
            lines=p["lines"],
            port=p.get("port"),
            status=p.get("status"),
            pallet_letter=p.get("palletLetter")
        )
        port_txt = p.get("port") or "Plastmaskin"
        print(f"  - {p['sscc']} ({p['order']}, {len(p['lines'])} rader, {port_txt})")

    print("\nLägger in förslagspool (andra ID:n på port)...")
    for p in SUGGESTION_PALLETS:
        db.save_pallet(
            sscc=p["sscc"],
            order_number=p["order"],
            two_pallets=p["twoPallets"],
            lines=p["lines"],
            port=p.get("port"),
            status=p.get("status"),
            pallet_letter=p.get("palletLetter")
        )
        picker = p["lines"][0]["picker"]
        print(f"  - ID {picker} · {p['order']} · {p['palletLetter']}-pall · {p['port']}")

    print("\nLägger in kontrollista (demo)...")
    db.add_check_target("0312", note="Ny via bemanning", added_by="admin")
    db.add_check_target("0415", note="Heltid bemanning", added_by="admin")
    db.add_check_target("0251", note="Slumpmässig kontroll", added_by="admin")
    print("  - 0312 (Ny via bemanning)")
    print("  - 0415 (Heltid bemanning)")
    print("  - 0251 (Slumpmässig kontroll)")

    print(f"\nKlart! {len(USERS)} användare, {len(PALLETS)} kontrollpallar och {len(SUGGESTION_PALLETS)} förslagspallar.")
    print(f"Databas: {db.DB_PATH}")


if __name__ == "__main__":
    seed()
