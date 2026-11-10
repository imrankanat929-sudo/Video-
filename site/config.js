// Edit this file to set up your store. No coding knowledge needed:
// change the text between the quotes and the numbers.
window.STORE_CONFIG = {
  brandName: "HIDE & HUSTLE",
  currency: "USD",
  currencySymbol: "$",

  // WhatsApp number in international format, digits only (no +, spaces or dashes).
  whatsappNumber: "447700900123",
  // Telegram username without the @.
  telegramUsername: "hideandhustle",

  // Orders at or above this total ship free; below it, flatShipping is added.
  freeShippingFrom: 100,
  flatShipping: 6.9,
  // Price of hot-stamped initials, per item.
  initialsPrice: 7,

  // Replace every image with your own product photos (put them in site/img/).
  products: [
    {
      id: "cardholder",
      name: "Minimal Cardholder",
      tagline: "4 cards + cash. Fits any pocket.",
      price: 29,
      compareAt: 35,
      leather: "Full-grain · 1.4 mm",
      badge: "Bestseller",
      colors: ["Black", "Cognac"],
      image:
        "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=800&q=70",
    },
    {
      id: "messenger",
      name: "City Messenger",
      tagline: "13\" laptop, books, everything.",
      price: 99,
      compareAt: 119,
      leather: "Top-grain · 1.6 mm",
      badge: "Founding price",
      colors: ["Black", "Dark Brown"],
      image:
        "https://images.unsplash.com/photo-1473188588951-666fce8e7c68?auto=format&fit=crop&w=800&q=70",
    },
    {
      id: "backpack",
      name: "Everyday Backpack",
      tagline: "16\" laptop sleeve. Built for 10 years.",
      price: 119,
      compareAt: 139,
      leather: "Full-grain · 1.8 mm",
      badge: "Founding price",
      colors: ["Black", "Cognac"],
      image:
        "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=800&q=70",
    },
    {
      id: "duffel",
      name: "Weekender Duffel",
      tagline: "Cabin-size. Shoe pocket. Brass hardware.",
      price: 189,
      compareAt: 219,
      leather: "Full-grain · 2.0 mm",
      badge: "Limited",
      colors: ["Dark Brown"],
      image: "img/placeholder-duffel.svg",
    },
  ],
};
