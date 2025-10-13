from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from osintt import dark_osint
import os

app = Flask(__name__)
CORS(app)

INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>GURMAN OSINT TOOL</title>
  <style>
    :root{
      --bg:#000;
      --panel:#071014;
      --accent:#35d27a;
      --muted:#7fbf9a;
      --glass: rgba(0,0,0,0.6);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", monospace;
    }

    html,body{height:100%;margin:0;background:linear-gradient(180deg,#000 0%, #021014 60%);color:var(--accent);font-size:18px;}
    .wrap{min-height:100%;display:flex;align-items:center;justify-content:center;padding:24px;}
    .card{width:100%;max-width:1400px;background:linear-gradient(180deg,var(--panel), #011);border:1px solid rgba(53,210,122,0.06);box-shadow:0 10px 40px rgba(0,0,0,0.8);border-radius:12px;overflow:hidden;display:grid;grid-template-columns:1fr 2fr;gap:16px;padding:24px;min-height:500px;}
    @media(max-width:1024px){.card{grid-template-columns:1fr;}}
    .left{padding:16px;border-right:1px solid rgba(53,210,122,0.04);}
    @media(max-width:1024px){.left{border-right:none;border-bottom:1px solid rgba(53,210,122,0.04);}}
    label{display:block;font-size:16px;color:var(--muted);margin-bottom:8px;}
    input[type=text]{width:100%;padding:14px 16px;background:var(--glass);border:1px solid rgba(53,210,122,0.06);color:var(--accent);border-radius:8px;outline:none;font-size:16px;}
    .btn{margin-top:12px;display:inline-block;padding:12px 18px;border-radius:8px;border:none;background:linear-gradient(180deg,var(--accent), #17985b);color:#001;font-weight:700;font-size:16px;cursor:pointer;}
    .small{font-size:14px;color:var(--muted);margin-top:10px;}
    .console{height:200px;background:#000;padding:12px;border-radius:8px;overflow:auto;border:1px solid rgba(53,210,122,0.06);color:var(--muted);font-size:14px;}
    .right{padding:16px;display:flex;flex-direction:column;gap:12px;}
    .output{flex:1;background:#000;padding:16px;border-radius:8px;overflow:auto;border:1px solid rgba(53,210,122,0.06);min-height:300px;color:var(--muted);font-size:14px;}
    pre{white-space:pre-wrap;word-break:break-word;color:var(--accent);font-size:14px;}
    .meta{display:flex;justify-content:space-between;align-items:center;font-size:14px;color:var(--muted);}
    .no-record{color:#ff6b6b}
    .ok-record{color:var(--accent)}
    @media(max-width:768px){html, body{font-size:16px;}.card{padding:16px; gap:12px;}.left, .right{padding:12px;}input[type=text], .btn{font-size:14px; padding:10px 12px;}.console, .output{font-size:13px;}}
    @media(max-width:480px){html, body{font-size:14px;}.card{padding:12px; gap:10px;}input[type=text], .btn{font-size:13px; padding:8px 10px;}.console, .output{font-size:12px; height:150px;}}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card" role="main" aria-label="OSINT MADE BY GURMAN">
      <div class="left">
        <form id="searchForm" onsubmit="return false;">
          <label for="number">Enter mobile number</label>
          <input id="number" type="text" placeholder="+91" />
          <button id="fetchBtn" class="btn">FETCH</button>
        </form>
        <div class="small">99$ for More tools</div>
        <div style="margin-top:10px">
          <div class="small">Console</div>
          <div id="console" class="console">READY.</div>
        </div>
      </div>
      <div class="right">
        <div class="meta">
          <div>Search output</div>
          <div id="status">status: idle</div>
        </div>
        <div id="output" class="output"><div class="hint">No results yet — enter a number and click FETCH</div></div>
        <div class="meta"><div style="font-size:13px;color:var(--muted)">GURMAN OSINT TOOL</div><div id="last" style="font-size:13px;color:var(--muted)">—</div></div>
      </div>
    </div>
  </div>

<script>
const consoleEl = document.getElementById('console');
const outputEl = document.getElementById('output');
const statusEl = document.getElementById('status');
const lastEl = document.getElementById('last');
const btn = document.getElementById('fetchBtn');

function pushLog(msg){
  consoleEl.innerText += '\\n' + msg;
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

async function doFetch(){
  const num = document.getElementById('number').value.trim();
  if(!num){ pushLog('ERROR: empty input'); statusEl.innerText='status: idle'; return; }
  pushLog('> initiating search for ' + num);
  statusEl.innerText = 'status: fetching...';
  outputEl.innerHTML = '<div style="color:var(--muted)">fetching...</div>';
  lastEl.innerText = new Date().toLocaleString();

  try{
    const resp = await fetch('/api/search', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ number: num })
    });

    if(!resp.ok){
      const txt = await resp.text();
      pushLog('> server error: ' + resp.status + ' ' + txt);
      statusEl.innerText='status: error';
      outputEl.innerHTML = '<div class="no-record">Server error: '+resp.status+'</div>';
      return;
    }

    const data = await resp.json();
    if(data.status === 'no_record'){
      pushLog('> no record found');
      statusEl.innerText = 'status: no record';
      outputEl.innerHTML = '<div class="no-record">No record found for '+num+'</div>';
    } else if(data.status === 'ok'){
      pushLog('> record found');
      statusEl.innerText = 'status: record';
      const pretty = JSON.stringify(data.results, null, 2);
      outputEl.innerHTML = '<pre>'+ pretty +'</pre>';
    } else if(data.error){
      pushLog('> backend error: ' + data.error);
      statusEl.innerText = 'status: error';
      outputEl.innerHTML = '<div class="no-record">Error: '+data.error+'</div>';
    } else {
      pushLog('> unexpected response');
      statusEl.innerText = 'status: unknown';
      outputEl.innerHTML = '<pre>'+JSON.stringify(data, null,2)+'</pre>';
    }
  }catch(err){
    pushLog('> fetch failed: '+ err.message);
    statusEl.innerText='status: offline';
    outputEl.innerHTML = '<div class="no-record">Network error</div>';
  }
}

btn.addEventListener('click', doFetch);
document.getElementById('number').addEventListener('keydown', (e)=>{ if(e.key==='Enter'){ doFetch(); }});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/api/search", methods=["POST"])
def api_search():
    body = request.get_json() or {}
    number = body.get("number", "").strip()
    
    if not number:
        return jsonify({"error": "empty_number"}), 400

    # Block specific numbers
    blocked_numbers = ["9891668332", "9953535271"]
    if number in blocked_numbers:
        return jsonify({"status": "no_record"}), 200

    try:
        results = dark_osint.search_mobile(number)
        if not results:
            return jsonify({"status": "no_record"}), 200
        return jsonify({"status": "ok", "results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
