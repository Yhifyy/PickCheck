// Testdata för PickCheck. När en riktig backend kopplas på ersätts detta
// av API-anrop, men strukturen per produktrad bör vara densamma.
//
// Fält per produktrad:
//   sscc           - pallens SSCC/pallnummer som raden tillhör
//   productNumber  - artikelnummer
//   product        - produktnamn
//   picker         - plockrad / plockare (ex "0251")
//   pickedQty      - antal som plockaren registrerat
//   pallet         - PLOCKAD pall: där plockaren faktiskt la produkten ("A"/"B")
//   correctPallet  - RÄTT pall: där produkten BORDE ligga enligt ordern ("A"/"B")
//                    Om pallet !== correctPallet => produkten ligger på FEL PALL.
//                    (för order med bara en pall är allt "A")

const PALLETS = {
  "173308781029514906": {
    sscc: "173308781029514906",
    order: "ORD-99231",
    twoPallets: true, // ordern består av A- och B-pall
    lines: [
      { productNumber: "6617-44832", product: "TRESemmé Balsam Rich Moisture 685ml x6 (S)", picker: "0251", pickedQty: 12, pallet: "A", correctPallet: "A" },
      { productNumber: "A25PC017",   product: "Easy Bath Glove Kids Unicorn",               picker: "0251", pickedQty: 12, pallet: "A", correctPallet: "A" },
      { productNumber: "HST2301",    product: "Brush Set 2pcs 25mm / 50mm Mixed Bristle",    picker: "0251", pickedQty: 12, pallet: "A", correctPallet: "A" },
      { productNumber: "6617-46930", product: "Duschgel Dove 720ml Dove",                    picker: "0251", pickedQty: 24, pallet: "A", correctPallet: "A" },
      { productNumber: "7155",       product: "Flying Disc with Launcher",                   picker: "0251", pickedQty: 12, pallet: "A", correctPallet: "A" },
      { productNumber: "TK82865",    product: "Tvålkopp Kotikulta Fjord Ljusgrå Kotikulta",  picker: "0251", pickedQty: 6,  pallet: "B", correctPallet: "B" },
      // FEL PALL: plockad på A men ska egentligen ligga på B-pallen
      { productNumber: "1041001K",   product: "Råttfälla Betesstation SuperCat SuperCat",    picker: "0251", pickedQty: 10, pallet: "A", correctPallet: "B" },
      { productNumber: "5138-89289", product: "Tandkräm Oral B Kids 50ml Oral-B",            picker: "0251", pickedQty: 12, pallet: "A", correctPallet: "A" },
      { productNumber: "560-71310",  product: "Wettex 10-pack Wettex",                       picker: "0251", pickedQty: 42, pallet: "B", correctPallet: "B" },
      { productNumber: "6617-57529", product: "Dove Advanced Stick 72h Cucumber 50ml",       picker: "0251", pickedQty: 6,  pallet: "A", correctPallet: "A" },
      { productNumber: "5661929-60322229405", product: "Batteri CR2032 5p Tear Off Varta",   picker: "0251", pickedQty: 20, pallet: "A", correctPallet: "A" },
      { productNumber: "69615",      product: "Pensel Pro 12mm softgrip Bristle Bristle",    picker: "0251", pickedQty: 24, pallet: "A", correctPallet: "A" },
      { productNumber: "6684-871869769966", product: "Ljuskälla Philips LED 60W A60 E27",    picker: "0251", pickedQty: 8,  pallet: "A", correctPallet: "A" },
      { productNumber: "6617-14777", product: "Zendium Sensitive 2-pack",                    picker: "0251", pickedQty: 25, pallet: "A", correctPallet: "A" },
      // FEL PALL: plockad på B men ska egentligen ligga på A-pallen
      { productNumber: "6617-26700", product: "Deodorant Dove Mens Care 72h 50ml Dove Men",  picker: "0251", pickedQty: 12, pallet: "B", correctPallet: "A" },
      { productNumber: "6617-27479", product: "Deodorant Rexona Roll-On 50ml Rexona",        picker: "0251", pickedQty: 12, pallet: "B", correctPallet: "B" }
    ]
  },
  "173308781029514907": {
    sscc: "173308781029514907",
    order: "ORD-99245",
    twoPallets: false,
    lines: [
      { productNumber: "6617-44832", product: "TRESemmé Balsam Rich Moisture 685ml x6 (S)", picker: "0312", pickedQty: 6,  pallet: "A", correctPallet: "A" },
      { productNumber: "6617-46930", product: "Duschgel Dove 720ml Dove",                    picker: "0312", pickedQty: 18, pallet: "A", correctPallet: "A" },
      { productNumber: "560-71310",  product: "Wettex 10-pack Wettex",                       picker: "0312", pickedQty: 30, pallet: "A", correctPallet: "A" },
      { productNumber: "5138-89289", product: "Tandkräm Oral B Kids 50ml Oral-B",            picker: "0312", pickedQty: 12, pallet: "A", correctPallet: "A" },
      { productNumber: "7155",       product: "Flying Disc with Launcher",                   picker: "0312", pickedQty: 9,  pallet: "A", correctPallet: "A" }
    ]
  }
};
