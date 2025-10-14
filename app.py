from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from osintt import dark_osint

app = Flask(__name__)
CORS(app)

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GURMAN OSINT TOOL</title>
    <style>
        body {
            background-color: #000;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        input {
            background: black;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 10px;
            width: 260px;
            margin-bottom: 10px;
        }
        button {
            background: #00ff00;
            color: black;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background: #00cc00;
        }
        #output {
            margin-top: 20px;
            text-align: left;
            width: 90%;
            max-width: 600px;
            background: #000;
            border: 1px solid #00ff00;
            padding: 10px;
            border-radius: 10px;
            overflow-wrap: anywhere;
        }
    </style>
</head>
<body>
    <h2>📞 GURMAN OSINT TOOL</h2>
    <input type="text" id="number" placeholder="Enter Number (with country code)">
    <button onclick="fetchData()">Fetch Info</button>
    <div id="output"></div>

    <script>
        async function fetchData() {
            const num = document.getElementById("number").value.trim();
            const output = document.getElementById("output");
            output.innerHTML = "<b>Fetching info...</b>";

            try {
                const res = await fetch("/api/search", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ number: num })
                });

                const data = await res.json();

                if (data.status === "blocked") {
                    output.innerHTML = "<b>❌ This number is blocked.</b>";
                } else if (data.status === "no_record") {
                    output.innerHTML = "<b>No record found.</b>";
                } else if (data.status === "ok" && data.results && data.results.length > 0) {
                    output.innerHTML = data.results.map((item, i) => `
                        <b>Result ${i + 1}</b><br>
                        Name: ${item.name || "N/A"}<br>
                        Father: ${item.father_name || "N/A"}<br>
                        Mobile: ${item.mobile || "N/A"}<br>
                        Alt Mobile: ${item.alt_mobile || "N/A"}<br>
                        ID: ${item.id_number || "N/A"}<br>
                        Circle: ${item.circle || "N/A"}<br>
                        Address: ${item.address || "N/A"}<br>
                        Email: ${item.email || "N/A"}<br><hr>
                    `).join('');
                } else {
                    output.innerHTML = "<b>No record found.</b>";
                }
            } catch (err) {
                output.innerHTML = "<b>Error fetching data.</b>";
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html_code)

@app.route("/api/search", methods=["POST"])
def api_search():
    body = request.get_json() or {}
    number = body.get("number", "").strip()

    if not number:
        return jsonify({"error": "empty_number"}), 400

    # 🚫 Block only these specific numbers
    blocked_numbers = ["9891668332", "9953535271"]
    if number in blocked_numbers:
        return jsonify({"status": "blocked"}), 200

    try:
        results = dark_osint.search_mobile(number)
        if not results or len(results) == 0:
            return jsonify({"status": "no_record"}), 200
        return jsonify({"status": "ok", "results": results}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
