from flask import Flask, jsonify

app = Flask(__name__)

suppliers = [
    {
        "supplier_id": 1,
        "supplier_name": "Lanka Rice Mills Ltd",
        "city": "Polonnaruwa",
        "product_id": 1001,
        "supply_price": 180.00
    },
    {
        "supplier_id": 2,
        "supplier_name": "Fresh Dairy Lanka",
        "city": "Galle",
        "product_id": 1002,
        "supply_price": 320.00
    },
    {
        "supplier_id": 3,
        "supplier_name": "Ceylon Sugar Traders",
        "city": "Matara",
        "product_id": 1003,
        "supply_price": 130.00
    },
    {
        "supplier_id": 4,
        "supplier_name": "Southern Oil Distributors",
        "city": "Colombo",
        "product_id": 1004,
        "supply_price": 950.00
    },
    {
        "supplier_id": 5,
        "supplier_name": "Sunlight Bakeries & Flour",
        "city": "Colombo",
        "product_id": 1005,
        "supply_price": 250.00
    },
    {
        "supplier_id": 6,
        "supplier_name": "Highland Tea Exporters",
        "city": "Kandy",
        "product_id": 1006,
        "supply_price": 400.00
    },
    {
        "supplier_id": 7,
        "supplier_name": "Emerald Personal Care",
        "city": "Colombo",
        "product_id": 1007,
        "supply_price": 120.00
    },
    {
        "supplier_id": 8,
        "supplier_name": "Prima Grain Processing",
        "city": "Trincomalee",
        "product_id": 1008,
        "supply_price": 140.00
    },
    {
        "supplier_id": 9,
        "supplier_name": "Royal Agro Foods",
        "city": "Kurunegala",
        "product_id": 1009,
        "supply_price": 420.00
    },
    {
        "supplier_id": 10,
        "supplier_name": "Ruhuna Agritech",
        "city": "Hambantota",
        "product_id": 1010,
        "supply_price": 160.00
    }
]

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Supermarket Supplier API",
        "endpoint": "/api/suppliers"
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
