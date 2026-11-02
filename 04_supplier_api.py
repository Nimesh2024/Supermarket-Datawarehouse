from flask import Flask, jsonify

app = Flask(__name__)

suppliers = [
    {
        "supplier_id": 1,
        "supplier_name": "Lanka Rice Mills Ltd",
        "city": "Galle",
        "product_id": 1001,
        "supply_price": 180.0
    },
    {
        "supplier_id": 2,
        "supplier_name": "Fresh Dairy Lanka",
        "city": "Badulla",
        "product_id": 1002,
        "supply_price": 420.0
    },
    {
        "supplier_id": 3,
        "supplier_name": "Ceylon Sugar Traders",
        "city": "Jaffna",
        "product_id": 1003,
        "supply_price": 160.0
    },
    {
        "supplier_id": 4,
        "supplier_name": "Southern Oil Distributors",
        "city": "Kurunegala",
        "product_id": 1004,
        "supply_price": 310.0
    },
    {
        "supplier_id": 5,
        "supplier_name": "Sunlight Bakeries & Flour",
        "city": "Matara",
        "product_id": 1005,
        "supply_price": 150.0
    },
    {
        "supplier_id": 6,
        "supplier_name": "Highland Tea Exporters",
        "city": "Batticaloa",
        "product_id": 1006,
        "supply_price": 380.0
    },
    {
        "supplier_id": 7,
        "supplier_name": "Emerald Personal Care",
        "city": "Batticaloa",
        "product_id": 1007,
        "supply_price": 240.0
    },
    {
        "supplier_id": 8,
        "supplier_name": "Prima Grain Processing",
        "city": "Nuwara Eliya",
        "product_id": 1008,
        "supply_price": 190.0
    },
    {
        "supplier_id": 9,
        "supplier_name": "Royal Agro Foods",
        "city": "Ratnapura",
        "product_id": 1009,
        "supply_price": 320.0
    },
    {
        "supplier_id": 10,
        "supplier_name": "Ruhuna Agritech",
        "city": "Batticaloa",
        "product_id": 1010,
        "supply_price": 520.0
    },
    {
        "supplier_id": 11,
        "supplier_name": "Ocean Harvest Seafood",
        "city": "Matale",
        "product_id": 1011,
        "supply_price": 750.0
    },
    {
        "supplier_id": 12,
        "supplier_name": "Ceylon Spice Exports",
        "city": "Trincomalee",
        "product_id": 1012,
        "supply_price": 60.0
    },
    {
        "supplier_id": 13,
        "supplier_name": "Hilltop Tea Estates",
        "city": "Kurunegala",
        "product_id": 1013,
        "supply_price": 380.0
    },
    {
        "supplier_id": 14,
        "supplier_name": "Island Beverage Co",
        "city": "Matara",
        "product_id": 1014,
        "supply_price": 480.0
    },
    {
        "supplier_id": 15,
        "supplier_name": "Golden Harvest Oils",
        "city": "Negombo",
        "product_id": 1015,
        "supply_price": 420.0
    },
    {
        "supplier_id": 16,
        "supplier_name": "Metro Household Supplies",
        "city": "Kandy",
        "product_id": 1016,
        "supply_price": 850.0
    },
    {
        "supplier_id": 17,
        "supplier_name": "Kandy Valley Farms",
        "city": "Kurunegala",
        "product_id": 1017,
        "supply_price": 340.0
    },
    {
        "supplier_id": 18,
        "supplier_name": "Serendib Snacks Ltd",
        "city": "Matara",
        "product_id": 1018,
        "supply_price": 130.0
    },
    {
        "supplier_id": 19,
        "supplier_name": "Lanka Poultry Producers",
        "city": "Trincomalee",
        "product_id": 1019,
        "supply_price": 170.0
    },
    {
        "supplier_id": 20,
        "supplier_name": "Apex Milling Industries",
        "city": "Polonnaruwa",
        "product_id": 1020,
        "supply_price": 180.0
    },
    {
        "supplier_id": 21,
        "supplier_name": "Southern Dairy Cooperative",
        "city": "Matale",
        "product_id": 1021,
        "supply_price": 70.0
    },
    {
        "supplier_id": 22,
        "supplier_name": "Wayamba Agro Products",
        "city": "Polonnaruwa",
        "product_id": 1022,
        "supply_price": 160.0
    },
    {
        "supplier_id": 23,
        "supplier_name": "Central Spice Exporters",
        "city": "Nuwara Eliya",
        "product_id": 1023,
        "supply_price": 220.0
    },
    {
        "supplier_id": 24,
        "supplier_name": "Western Bakeries",
        "city": "Kurunegala",
        "product_id": 1024,
        "supply_price": 280.0
    },
    {
        "supplier_id": 25,
        "supplier_name": "Orient Salt & Chemicals",
        "city": "Batticaloa",
        "product_id": 1025,
        "supply_price": 280.0
    },
    {
        "supplier_id": 26,
        "supplier_name": "Lanka Organic Foods",
        "city": "Badulla",
        "product_id": 1026,
        "supply_price": 290.0
    },
    {
        "supplier_id": 27,
        "supplier_name": "Ceylon Coffee Roasters",
        "city": "Colombo",
        "product_id": 1027,
        "supply_price": 310.0
    },
    {
        "supplier_id": 28,
        "supplier_name": "Pearl Island Products",
        "city": "Negombo",
        "product_id": 1028,
        "supply_price": 90.0
    },
    {
        "supplier_id": 29,
        "supplier_name": "Silverline Personal Products",
        "city": "Matale",
        "product_id": 1029,
        "supply_price": 140.0
    },
    {
        "supplier_id": 30,
        "supplier_name": "Sun City Beverage Distributors",
        "city": "Matale",
        "product_id": 1030,
        "supply_price": 950.0
    },
    {
        "supplier_id": 31,
        "supplier_name": "Tropical Fruit Processing",
        "city": "Matara",
        "product_id": 1031,
        "supply_price": 820.0
    },
    {
        "supplier_id": 32,
        "supplier_name": "Lanka Cereal Mills",
        "city": "Trincomalee",
        "product_id": 1032,
        "supply_price": 1450.0
    },
    {
        "supplier_id": 33,
        "supplier_name": "Highland Dairy Products",
        "city": "Nuwara Eliya",
        "product_id": 1033,
        "supply_price": 920.0
    },
    {
        "supplier_id": 34,
        "supplier_name": "Southern Flour Mills",
        "city": "Kandy",
        "product_id": 1034,
        "supply_price": 680.0
    },
    {
        "supplier_id": 35,
        "supplier_name": "Ceylon Confectionery Co",
        "city": "Galle",
        "product_id": 1035,
        "supply_price": 120.0
    },
    {
        "supplier_id": 36,
        "supplier_name": "Greenfield Tea Producers",
        "city": "Ratnapura",
        "product_id": 1036,
        "supply_price": 150.0
    },
    {
        "supplier_id": 37,
        "supplier_name": "Island Clean Household Care",
        "city": "Jaffna",
        "product_id": 1037,
        "supply_price": 180.0
    },
    {
        "supplier_id": 38,
        "supplier_name": "Heritage Spices Sri Lanka",
        "city": "Colombo",
        "product_id": 1038,
        "supply_price": 140.0
    },
    {
        "supplier_id": 39,
        "supplier_name": "Apex Agro Suppliers",
        "city": "Kegalle",
        "product_id": 1039,
        "supply_price": 140.0
    },
    {
        "supplier_id": 40,
        "supplier_name": "Ceylon Golden Grain Ltd",
        "city": "Polonnaruwa",
        "product_id": 1040,
        "supply_price": 220.0
    },
    {
        "supplier_id": 41,
        "supplier_name": "Rajarata Grain Traders",
        "city": "Polonnaruwa",
        "product_id": 1041,
        "supply_price": 260.0
    },
    {
        "supplier_id": 42,
        "supplier_name": "Kandurata Agro Products",
        "city": "Kalutara",
        "product_id": 1042,
        "supply_price": 380.0
    },
    {
        "supplier_id": 43,
        "supplier_name": "Northern Sea Foods",
        "city": "Jaffna",
        "product_id": 1043,
        "supply_price": 140.0
    },
    {
        "supplier_id": 44,
        "supplier_name": "Southern Coast Distributing",
        "city": "Kegalle",
        "product_id": 1044,
        "supply_price": 110.0
    },
    {
        "supplier_id": 45,
        "supplier_name": "Lanka Pure Oils",
        "city": "Kegalle",
        "product_id": 1045,
        "supply_price": 95.0
    },
    {
        "supplier_id": 46,
        "supplier_name": "Ceylon Nature Herbal Care",
        "city": "Matara",
        "product_id": 1046,
        "supply_price": 160.0
    },
    {
        "supplier_id": 47,
        "supplier_name": "Pinnacle Dairy Lanka",
        "city": "Trincomalee",
        "product_id": 1047,
        "supply_price": 310.0
    },
    {
        "supplier_id": 48,
        "supplier_name": "Island Treat Confectionery",
        "city": "Kalutara",
        "product_id": 1048,
        "supply_price": 220.0
    },
    {
        "supplier_id": 49,
        "supplier_name": "Ceylon Pure Water Co",
        "city": "Matale",
        "product_id": 1049,
        "supply_price": 400.0
    },
    {
        "supplier_id": 50,
        "supplier_name": "Lanka Fresh Farms",
        "city": "Badulla",
        "product_id": 1050,
        "supply_price": 680.0
    }
]

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Supermarket Supplier API",
        "endpoint": "/api/suppliers",
        "total_suppliers": len(suppliers)
    })

@app.route("/api/suppliers", methods=["GET"])
def get_suppliers():
    return jsonify(suppliers)

@app.route("/api/suppliers/<int:supplier_id>", methods=["GET"])
def get_supplier(supplier_id):
    for supplier in suppliers:
        if supplier["supplier_id"] == supplier_id:
            return jsonify(supplier)
    return jsonify({"error": "Supplier not found"}), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
