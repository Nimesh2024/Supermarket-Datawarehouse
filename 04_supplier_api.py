
from flask import Flask, jsonify

app = Flask(__name__)

suppliers = [
    {
        "supplier_id": 1,
        "supplier_name": "Lanka Rice Suppliers",
        "city": "Colombo",
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
