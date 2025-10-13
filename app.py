from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from osintt import dark_osint

app = Flask(__name__)
CORS(app)

# Single-file HTML UI served by Flask (responsive hacker style).
INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Hacker-Style Mobile Search</title>
  <style>
    /* Simple responsive hacker-style terminal look */
    :root{
      --bg:#000;
      --panel:#071014;
      --accent:#35d27a;
      --muted:#7fbf9a;
      --glass: rgba(0,0,0,0.6);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", monospace;
    }
    html,body{height:100%;margin:0;background:linear-gradient(180deg,#000 0%, #021014 60%);color:var(--accent)}
    .wrap{min-height:100%;display:flex;align-items:center;justify-content:center;padding:18px}
    .card{width:100%;max-width:1100px;background:linear-gradient(180deg,var(--panel), #011) ;border:1px solid rgba(53,210,122,0.06);box-shadow:0 8px 30px rgba(0,0,0,0.7);border-radius:10px;overflow:hidden;display:grid;grid-template-columns:1fr 2fr;gap:12px;padding:16px}
    @media(max-width:880px){ .card{grid-template-columns:1fr;}}
    .left{padding:10px;border-right:1px solid rgba(53,210,122,0.04)}
    @media(max-width:880px){ .left{border-right:none;border-bottom:1px solid rgba(53,210,122,0.04)}}
    label{display:block;font-size:12px;color:var(--muted);margin-bottom:6px}
    input[type=text]{width:100%;padding:10px 12px;background:var(--glass);border:1px solid rgba(53,210,122,0.06);color:var(--accent);border-radius:6px;outline:none}
    .btn{margin-top:8px;display:inline-block;padding:10px 14px;border-radius:6px;border:none;background:transparent;color:#001; font-weight:700; background:linear-gradient(180deg,var(--accent), #17985b);cursor:pointer}
    .small{font-size:12px;color:var(--muted);margin-top:8px}
    .console{height:140px;background:#000;padding:10px;border-radius:6px;overflow:auto;border:1px solid rgba(53,210,122,0.06);color:var(--muted);font-size:13px}
    .right{padding:10px;display:flex;flex-direction:column;gap:8px}
    .output{flex:1;background:#000;padding:12px;border-radius:6px;overflow:auto;border:1px solid rgba(53,210,122,0.06);min-height:220px;color:var(--muted)}
    pre{white-space:pre-wrap;word-break:break-word;color:var(--accent);font-size:13px}
    .meta{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:var(--muted)}
    .no-record{color:#ff6b6b}
    .ok-record{color:var(--accent)}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card" role="main" aria-label="Hacker style mobile search">
      <div class="left">
        <form id="searchForm" onsubmit="return false;">
          <label for="number">Enter mobile number</label>
          <input id="number" type="text" placeholder="+9198XXXXXXXX" />
          <button id="fetchBtn" class="btn">FETCH</button>
        </form>
        <div class="small">Use international format for best results. Backend calls: <code>dark_osint.search_mobile(\"number\")</code></div>
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
        <div class="meta"><div style="font-size:11px;color:var(--muted)">Responsive • Hacker-style</div><div id="last" style="font-size:11px;color:var(--muted)">—</div></div>
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

    try:
        # --- your exact call here ---
        results = dark_osint.search_mobile(number)
        # --------------------------------
        # Interpret the result:
        # If results is falsy (None, empty list, empty dict, empty string) -> no record
        if not results:
            return jsonify({"status": "no_record"}), 200
        # else return as-is
        return jsonify({"status": "ok", "results": results}), 200

    except Exception as e:
        # return the error message (keep for debugging)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Run with: python this_file.py
    app.run(host="0.0.0.0", port=5000, debug=True)
