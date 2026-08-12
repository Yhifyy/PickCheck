"""
Seed testdata till PickCheck-databasen.
Kör med: python seed_data.py
"""
import database as db

PALLETS = [
    {
        "sscc": "173308781029514906",
        "order": "ORD-99231",
        "twoPallets": True,
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
        "order": "ORD-99245",
        "twoPallets": False,
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
        "order": "ORD-99300",
        "twoPallets": False,
        "lines": [
            {"productNumber": "6617-44832", "product": "TRESemmé Balsam Rich Moisture 685ml x6 (S)", "gtin": "8710447448328", "gtinInner": "8710447448311", "picker": "0415", "pickedQty": 24, "pallet": "A", "correctPallet": "A", "location": "03-12-1A", "packageType": "Ytterbox"},
            {"productNumber": "A25PC017", "product": "Easy Bath Glove Kids Unicorn", "gtin": "5701234567890", "gtinInner": "5701234567883", "picker": "0415", "pickedQty": 6, "pallet": "A", "correctPallet": "A", "location": "03-14-1B", "packageType": "Innerbox"},
            {"productNumber": "69615", "product": "Pensel Pro 12mm softgrip Bristle Bristle", "gtin": "7391234567890", "gtinInner": "7391234567883", "picker": "0415", "pickedQty": 12, "pallet": "A", "correctPallet": "A", "location": "07-25-1A", "packageType": "Ytterbox"},
        ]
    },
    {
        # Demo: stor order — A och B fylldes, overflow plockades på C-pall (Vardacco/IMI-scenario)
        "sscc": "173308781029514909",
        "order": "ORD-99400",
        "twoPallets": True,
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
    }
]


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
            lines=p["lines"]
        )
        print(f"  - {p['sscc']} ({p['order']}, {len(p['lines'])} rader)")

    print(f"\nKlart! {len(USERS)} användare och {len(PALLETS)} pallar tillagda.")
    print(f"Databas: {db.DB_PATH}")


if __name__ == "__main__":
    seed()
