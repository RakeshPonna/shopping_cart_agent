import sqlite3
import os

DB_PATH = os.getenv(
    "DB_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources", "store.db"))
)


def create_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            description TEXT,
            is_organic INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            rating REAL,
            reviewer_name TEXT,
            review_text TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            ordered_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)


    # --- Dry Fruits, Nuts, Seeds & Berries (50 additional products) ---
    # Prices in INR | Organic flag: 0 = Not verified
    products = [
        # --- Almonds (6) ---
        (33, "Vedaka California Almonds", "nuts", 309.00,
         "Natural California almonds, 1kg pack", 0),

        (34, "Vedaka Premium Whole Almonds", "nuts", 775.00,
         "Premium Non-Pareil whole California almonds, 500g", 0),

        (35, "Happilo Premium California Almonds", "nuts", 302.00,
         "Premium California almond kernels, 200g", 0),

        (36, "Tata Sampann California Almonds", "nuts", 1249.00,
         "Premium whole California almonds, 1kg", 0),

        (37, "Nutraj Australian Almonds", "nuts", 549.00,
         "Premium Australian almond kernels, 500g", 0),

        (38, "Farmley Premium California Almonds", "nuts", 299.00,
         "Raw premium California almonds, 250g", 0),

        # --- Cashews (6) ---
        (39, "Vedaka Whole Cashews W320", "nuts", 257.00,
         "Premium whole cashew nuts, W320 grade, 500g", 0),

        (40, "Vedaka Broken Cashews", "nuts", 152.00,
         "Broken cashew kernels for cooking and snacking, 100g", 0),

        (41, "Tata Sampann Whole Cashews", "nuts", 573.00,
         "Premium whole cashew nuts, 500g", 0),

        (42, "Nutraj Premium Cashew Nuts", "nuts", 529.00,
         "Premium whole cashews, 500g pack", 0),

        (43, "Happilo Premium Whole Cashews", "nuts", 547.00,
         "Premium whole cashew kernels, 450g", 0),

        (44, "Daily Good Roasted Cashews", "nuts", 255.00,
         "W400 grade cashews, 200g pack", 0),

        # --- Pistachios (5) ---
        (45, "Vedaka Roasted Salted Pistachios", "nuts", 479.00,
         "Roasted and salted California pistachios in shell, 250g", 0),

        (46, "Vedaka California Pistachios", "nuts", 1029.00,
         "Premium unsalted pistachio kernels without shell", 0),

        (47, "Nutraj Roasted Salted Pistachios", "nuts", 215.00,
         "Roasted and salted premium pistachios, 100g", 0),

        (48, "Tata Sampann Salted Pistachios", "nuts", 1137.00,
         "Premium roasted and salted pista, 500g", 0),

        (49, "Daily Good Plain Pistachios", "nuts", 449.00,
         "Plain premium pistachios, 100g pack", 0),

        # --- Walnuts (5) ---
        (50, "Vedaka Inshell Walnuts", "nuts", 553.00,
         "Premium walnuts in shell, 500g pack", 0),

        (51, "Vedaka Walnut Kernels", "nuts", 525.00,
         "Premium shelled walnut kernels, 250g", 0),

        (52, "Nutraj Walnut Kernels", "nuts", 175.00,
         "Premium walnut kernels, 100g pack", 0),

        (53, "Daily Good Walnut Kernels", "nuts", 199.00,
         "Premium walnut kernels, 100g pack", 0),

        (54, "BigBasket Popular Walnut Kernels", "nuts", 309.00,
         "Premium walnut kernels, 200g", 0),

        # --- Raisins & Munakka (6) ---
        (55, "Vedaka Premium Raisins", "dry-fruits", 340.00,
         "Premium sweet and soft dried raisins, 500g", 0),

        (56, "Vedaka Natural Raisins", "dry-fruits", 286.00,
         "Natural dried grapes, 500g pack", 0),

        (57, "Tata Sampann Black Raisins", "dry-fruits", 234.00,
         "Seedless premium black raisins, 200g", 0),

        (58, "Nutraj Afghan Munakka", "dry-fruits", 227.00,
         "Premium Afghan dried munakka raisins, 200g", 0),

        (59, "Happilo Green Raisins", "dry-fruits", 130.00,
         "Premium seedless green raisins, 250g", 0),

        (60, "Farmley Gourmet Raisins", "dry-fruits", 178.00,
         "Natural gourmet raisins, 200g pack", 0),

        # --- Dates & Dried Fruits (6) ---
        (61, "Vedaka Fresh Dates", "dry-fruits", 299.00,
         "Naturally dried sweet dates, 500g pack", 0),

        (62, "Vedaka Premium Prunes", "dry-fruits", 219.00,
         "Dried prunes, 200g pack", 0),

        (63, "Vedaka Dried Apricots", "dry-fruits", 649.00,
         "Premium dried apricots, 500g pack", 0),

        (64, "Happilo Kimia Dates", "dry-fruits", 299.00,
         "Premium soft Kimia dates, naturally sweet", 0),

        (65, "Lion Dates", "dry-fruits", 185.00,
         "Naturally sweet dried dates, 500g pack", 0),

        (66, "BigBasket Popular Dried Figs", "dry-fruits", 525.00,
         "Premium dried figs or anjeer, 500g pack", 0),

        # --- Makhana & Seeds (6) ---
        (67, "Vedaka Raw Pumpkin Seeds", "seeds", 175.00,
         "Raw pumpkin seeds, 200g pack", 0),

        (68, "Daily Good Phool Makhana", "snacks", 169.00,
         "Premium fox nuts or popped lotus seeds, 100g", 0),

        (69, "Nutraj Phool Makhana", "snacks", 249.00,
         "Premium popped lotus seeds, 200g pack", 0),

        (70, "BigBasket Popular Phool Makhana", "snacks", 125.00,
         "Crunchy fox nuts, 100g pack", 0),

        (71, "Tata Sampann Pumpkin Seeds", "seeds", 226.59,
         "Raw and unroasted premium pumpkin seeds, 200g", 0),

        (72, "Khari Foods Pumpkin Seeds", "seeds", 234.20,
         "Raw pumpkin seeds, 200g pack", 0),

        # --- Dry Fruit Mixes & Gift Packs (6) ---
        (73, "Vedaka Dry Fruits Gift Box", "dry-fruits", 1299.00,
         "Assorted almonds, cashews, raisins, pistachios and cranberries, 1kg", 0),

        (74, "BB Royal Organic Dry Fruit Collection", "dry-fruits", 659.00,
         "Assorted almonds, cashews and raisins, 450g", 0),

        (75, "BB Royal Premium Dry Fruit Gift Box", "dry-fruits", 899.00,
         "Almonds, cashews, raisins, pistachios, cranberries and apricots, 650g", 0),

        (76, "Daily Good Panchmeva Mix", "dry-fruits", 215.00,
         "Traditional assorted dry fruit mix, 200g", 0),

        (77, "Nutraj Festive Dry Fruit Gift Box", "dry-fruits", 1050.00,
         "Premium assorted dry fruit gift hamper, 500g", 0),

        (78, "BB Royal Shagun Dry Fruit Thali", "dry-fruits", 639.00,
         "Assorted cashews, raisins, almonds and pistachios, 450g", 0),

        # --- More Nuts & Specialty Products (6) ---
        (79, "Vedaka Raw Peanuts", "nuts", 130.00,
         "Raw groundnut kernels, 500g pack", 0),

        (80, "Livyor Brazil Nuts", "nuts", 747.00,
         "Premium Brazil nuts for healthy snacking", 0),

        (81, "Chironji Premium Seeds", "seeds", 149.00,
         "Premium chironji or charoli seeds, 50g pack", 0),

        (82, "Farmley Premium Makhana", "snacks", 359.10,
         "Premium fox nuts or phool makhana, 200g", 0),
    ]
     
    cursor.executemany("INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?)", products)

    # Avg ratings (for reference):
    # Honey:      1→4.625✓  2→3.833  3→4.833($$)  4→3.5  5→4.625✓  6→4.167  7→4.75✓  8→4.0
    # Oils:       9→4.67   10→3.67  11→4.5        12→4.33
    # Nuts/Seeds: 13→4.75  14→4.0   15→4.5        16→3.75
    # Grains:     17→4.67  18→4.33  19→4.5        20→3.83
    # Tea/Coffee: 21→4.67  22→4.17  23→4.75       24→4.0
    # Snacks:     25→4.5   26→3.83  27→4.67       28→3.67
    # Dairy-alt:  29→4.5   30→4.33  31→4.5        32→3.67
    
    reviews = [
        # --- Almonds (6) ---
        (33, 5.0, "Rahul", "Fresh and crunchy almonds. Good quality for the price."),
        (34, 4.5, "Priya", "Premium quality almonds with a great taste."),
        (35, 5.0, "Arjun", "Loved the taste and freshness. Perfect for daily snacking."),
        (36, 4.5, "Sneha", "Good packaging and consistently sized almonds."),
        (37, 4.0, "Karthik", "Good quality Australian almonds. Slightly expensive."),
        (38, 5.0, "Ananya", "Fresh, crunchy and worth buying again."),

        # --- Cashews (6) ---
        (39, 5.0, "Vikram", "Whole cashews are fresh and delicious."),
        (40, 4.0, "Meera", "Useful for cooking and making sweets. Good value."),
        (41, 4.5, "Suresh", "Nice cashew quality with a natural creamy taste."),
        (42, 5.0, "Divya", "Excellent cashews. Perfect for everyday use."),
        (43, 4.5, "Manoj", "Fresh and crunchy. Packaging was also good."),
        (44, 4.0, "Pooja", "Good roasted cashews with a satisfying crunch."),

        # --- Pistachios (5) ---
        (45, 5.0, "Amit", "Very tasty roasted pistachios. Loved the freshness."),
        (46, 4.5, "Kavya", "Great quality pistachio kernels for desserts."),
        (47, 4.0, "Naveen", "Good roasted pista. Could have been slightly less salty."),
        (48, 5.0, "Ritika", "Excellent taste and premium quality."),
        (49, 4.5, "Harish", "Fresh pistachios with a nice natural flavor."),

        # --- Walnuts (5) ---
        (50, 4.5, "Neha", "Good quality walnuts. Shells were reasonably easy to crack."),
        (51, 5.0, "Deepak", "Fresh walnut kernels with a rich taste."),
        (52, 4.0, "Swathi", "Good product for adding to breakfast and smoothies."),
        (53, 4.5, "Ramesh", "Nice packaging and fresh walnut pieces."),
        (54, 5.0, "Lakshmi", "Excellent quality walnuts. Will purchase again."),

        # --- Raisins & Munakka (6) ---
        (55, 5.0, "Sanjay", "Sweet and soft raisins. Perfect for everyday snacking."),
        (56, 4.5, "Madhavi", "Natural taste and good quality raisins."),
        (57, 5.0, "Varun", "Loved the black raisins. Fresh and delicious."),
        (58, 4.0, "Geetha", "Good quality munakka. Useful for traditional recipes."),
        (59, 4.5, "Akash", "Sweet green raisins with a pleasant texture."),
        (60, 5.0, "Shalini", "Great taste and freshness. Good value for money."),

        # --- Dates & Dried Fruits (6) ---
        (61, 5.0, "Praveen", "Soft and naturally sweet dates. Great for snacking."),
        (62, 4.5, "Nisha", "Good quality prunes with a nice chewy texture."),
        (63, 5.0, "Abhishek", "Delicious dried apricots with excellent texture."),
        (64, 4.5, "Sowmya", "Very soft dates and naturally sweet."),
        (65, 4.0, "Rohit", "Good dates for daily consumption and desserts."),
        (66, 5.0, "Bhavana", "Fresh and tasty anjeer. Excellent quality."),

        # --- Makhana & Seeds (6) ---
        (67, 4.5, "Tejas", "Good quality pumpkin seeds. Easy to add to breakfast."),
        (68, 5.0, "Aishwarya", "Light and crunchy makhana. Perfect evening snack."),
        (69, 4.5, "Girish", "Fresh fox nuts with good size and texture."),
        (70, 4.0, "Keerthi", "Good quality makhana. Works well for roasting."),
        (71, 5.0, "Sandeep", "Fresh pumpkin seeds with a nice nutty flavor."),
        (72, 4.5, "Harika", "Good packaging and quality seeds."),

        # --- Dry Fruit Mixes & Gift Packs (6) ---
        (73, 5.0, "Aditya", "Beautiful gift box with a good assortment of dry fruits."),
        (74, 4.5, "Mounika", "Nice combination of nuts and raisins. Good quality."),
        (75, 5.0, "Tarun", "Premium packaging and a great dry fruit assortment."),
        (76, 4.0, "Srilatha", "Good traditional panchmeva mix for everyday use."),
        (77, 5.0, "Chaitanya", "Excellent festive gift hamper. Looks premium."),
        (78, 4.5, "Divakar", "Good variety and attractive gift packaging."),

        # --- Specialty Nuts & Products (4) ---
        (79, 4.5, "Mahesh", "Fresh peanuts with good quality kernels."),
        (80, 5.0, "Pallavi", "Rich and distinctive taste. Nice addition to a nut mix."),
        (81, 4.0, "Ravi", "Good quality chironji seeds for traditional sweets."),
        (82, 5.0, "Sushmita", "Crunchy and fresh makhana. Great snack option."),
    ]

    cursor.execute("DELETE FROM reviews")
    cursor.executemany(
        "INSERT INTO reviews (product_id, rating, reviewer_name, review_text) VALUES (?, ?, ?, ?)",
        reviews,
    )

    conn.commit()
    conn.close()
    print(f"Database created at: {DB_PATH}")


if __name__ == "__main__":
    create_database()
