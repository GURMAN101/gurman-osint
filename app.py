from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>GURMAN OSINT TOOL</title>

<style>
:root {
  --bg:#020617;
  --panel:#02091f;
  --accent:#38bdf8;
  --accent-strong:#0ea5e9;
  --muted:#94a3b8;
  --danger:#fb7185;
  --radius-lg:18px;
  --radius-sm:10px;
}

*{box-sizing:border-box;margin:0;padding:0;}
body {
  background: #020617;
  color:white;
  font-family: system-ui, sans-serif;
  display:flex;
  height:100vh;
  overflow:hidden;
}

/* LEFT PANEL — STICKY COMMAND CENTER */
.left-panel {
  width:350px;
  min-width:300px;
  background:var(--panel);
  border-right:1px solid rgba(56,189,248,0.4);
  padding:18px;
  display:flex;
  flex-direction:column;
  gap:18px;
  position:sticky;
  top:0;
  height:100vh;
  overflow-y:auto;
}

.brand {
  display:flex;
  flex-direction:column;
  gap:4px;
}
.brand-title {
  font-weight:800;
  font-size:20px;
  color:var(--accent);
  letter-spacing:.11em;
}
.brand-sub {
  font-size:12px;
  color:var(--muted);
}

/* INPUT */
label {
  font-size:12px;
  margin-bottom:6px;
  color:var(--muted);
  text-transform:uppercase;
}
.input-box {
  width:100%;
  padding:12px 14px;
  border-radius:var(--radius-sm);
  border:1px solid rgba(56,189,248,0.4);
  background:#000;
  color:white;
}
.btn {
  width:100%;
  padding:10px;
  background:var(--accent);
  color:#000;
  font-weight:700;
  border-radius:var(--radius-sm);
  cursor:pointer;
  text-transform:uppercase;
  margin-top:8px;
}

/* Console */
.console {
  height:160px;
  background:#000;
  padding:10px;
  font-size:12px;
  color:#38bdf8;
  border-radius:var(--radius-sm);
  overflow-y:auto;
  border:1px solid rgba(56,189,248,0.3);
}

/* RIGHT PANEL */
.right-panel {
  flex:1;
  padding:18px;
  overflow-y:auto;
}
.results-header {
  font-size:14px;
  color:var(--muted);
  margin-bottom:10px;
}

.results-grid {
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(310px,1fr));
  gap:18px;
}

.record-card {
  background:#031327;
  padding:14px;
  border-radius:var(--radius-lg);
  border:1px solid rgba(56,189,248,0.3);
}

.record-name {
  font-size:16px;
  font-weight:700;
  color:var(--accent-strong);
  margin-bottom:10px;
}

.field-label {
  font-size:11px;
  text-transform:uppercase;
  color:var(--muted);
}
.field-value {
  font-size:13px;
  margin-bottom:6px;
}

.no-record {
  color:var(--danger);
}

/* Login Screen */
#authScreen {
  position:fixed;
  top:0;left:0;
  width:100%; height:100%;
  background:#010915;
  display:flex;
  justify-content:center; align-items:center;
  flex-direction:column;
  z-index:9999;
}
#authInput {
  padding:12px;
  width:250px;
  text-align:center;
  background:#000;
  border-radius:10px;
  border:1px solid var(--accent);
  color:white;
  margin-bottom:10px;
}
#authBtn {
  padding:10px 20px;
  background:var(--accent);
  color:#001;
  font-weight:700;
  border-radius:10px;
  cursor:pointer;
}
#authError {
  color:var(--danger);
  margin-top:10px;
  font-size:14px;
}

/* Mobile */
@media(max-width:768px){
  body {flex-direction:column;}
  .left-panel{
    width:100%;
    height:auto;
    position:relative;
    border-right:none;
    border-bottom:1px solid rgba(56,189,248,0.4);
  }
}
</style>
</head>


<body>

<!-- PASSWORD LOCK -->
<div id="authScreen">
  <h2 style="color:var(--accent); font-weight:700; margin-bottom:20px;">AUTHORIZATION REQUIRED</h2>
  <input id="authInput" type="password" placeholder="Enter password"/>
  <button id="authBtn" onclick="checkAuth()">UNLOCK</button>
  <div id="authError"></div>
</div>


<!-- LEFT PANEL -->
<section class="left-panel">
  <div class="brand">
    <div class="brand-title">GURMAN OSINT</div>
    <div class="brand-sub">Mobile Intelligence Scanner</div>
  </div>

  <label>Mobile Number</label>
  <input id="number" class="input-box" placeholder="9953535271"/>
  <button id="fetchBtn" class="btn">Fetch</button>

  <div class="console" id="console">READY.</div>
</section>

<section class="right-panel">
  <div class="results-header">Results: <span id="recordCount">0</span></div>
  <div id="output"><div class="no-record">Enter number to begin query</div></div>
</section>

<script>
const PASSWORD = "GURMANDADDY";

function checkAuth(){
  const val = document.getElementById("authInput").value;
  if(val === PASSWORD){
    document.getElementById("authScreen").style.display="none";
  } else {
    document.getElementById("authError").textContent = "Incorrect Password";
  }
}

const log=(msg)=>{
  let c=document.getElementById('console');
  c.textContent+="\\n"+msg;
  c.scrollTop=c.scrollHeight;
}

function renderCards(data){
  let html='<div class="results-grid">';
  data.forEach((r,i)=>{
    html+=`
      <div class="record-card">
      <div class="record-name">${r.name||'-'}</div>
      <div class="field-label">Mobile</div><div class="field-value">${r.mobile||'-'}</div>
      <div class="field-label">Father</div><div class="field-value">${r.fname||'-'}</div>
      <div class="field-label">Circle</div><div class="field-value">${r.circle||'-'}</div>
      <div class="field-label">Email</div><div class="field-value">${r.email||'-'}</div>
      <div class="field-label">Address</div><div class="field-value">${(r.address||'-').replace(/!/g,', ')}</div>
      </div>`;
  });
  html+='</div>';
  return html;
}

async function doFetch(){
  let num=document.getElementById('number').value.trim();
  if(!num) return log("ERROR: Empty Number");

  log("> Fetching: "+num);

  const res=await fetch('/api/search',{
    method:"POST", headers:{"Content-Type":"application/json"},
    body:JSON.stringify({number:num})
  });
  const data=await res.json();
  log("> Response received");

  let rec=document.getElementById('recordCount');
  let out=document.getElementById('output');

  if(data.status==="ok"){
    rec.textContent=data.results.length;
    out.innerHTML=renderCards(data.results);
  } else {
    rec.textContent="0";
    out.innerHTML='<div class="no-record">No record found</div>';
  }
}
document.getElementById('fetchBtn').onclick=doFetch;
document.getElementById('number').addEventListener('keydown',(e)=>{ if(e.key==="Enter") doFetch(); });
</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(INDEX_HTML)


@app.route("/api/search", methods=["POST"])
def api_search():
    body = request.get_json() or {}
    number = body.get("number", "").strip()
    if not number:
        return jsonify({"error": "Missing number"}), 400

    url = f"https://rushvx.tiiny.io/?key=RushVx&number={number}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
    except:
        return jsonify({"status": "no_record"}), 200

    if data.get("status") != "success":
        return jsonify({"status": "no_record"}), 200

    results = [v for k,v in data.items() if re.match(r"data[0-9]+$", k)]
    if not results:
        return jsonify({"status": "no_record"}), 200

    return jsonify({"status": "ok", "results": results}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
