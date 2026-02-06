from flask import Flask, request, jsonify, render_template_string, redirect
from flask_cors import CORS
import requests
import re
import os

app = Flask(__name__)
CORS(app)

BLOCK_FILE = "blocked.txt"

if not os.path.exists(BLOCK_FILE):
    open(BLOCK_FILE, "w").close()


def load_blocked():
    with open(BLOCK_FILE, "r") as f:
        return [x.strip() for x in f if x.strip()]


def block_number(num):
    if num not in load_blocked():
        with open(BLOCK_FILE, "a") as f:
            f.write(num + "\n")


def unblock_number(num):
    nums = [x for x in load_blocked() if x != num]
    with open(BLOCK_FILE, "w") as f:
        f.write("\n".join(nums))


# ================= ADMIN PANEL =================
ADMIN_HTML = """
<!DOCTYPE html><html><head><title>ADMIN</title>
<style>
body{background:#000;color:#fff;font-family:monospace;padding:30px}
input,button{padding:10px;background:black;border:1px solid #333;color:white}
button{background:white;color:black;font-weight:bold}
</style></head><body>
<h2>ADMIN BLOCK PANEL</h2>
<form method="POST" action="/block">
<input name="number" placeholder="Number"/>
<button>BLOCK</button>
</form>
<ul>
{% for n in blocked %}
<li>{{n}} <a href="/unblock/{{n}}" style="color:red">[UNBLOCK]</a></li>
{% endfor %}
</ul>
<a href="/">BACK</a>
</body></html>
"""


# ================= MAIN UI =================
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>GURMAN OSINT</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:black;color:white;font-family:Consolas,monospace;height:100vh;overflow:hidden}

/* BOOT */
#boot{position:fixed;inset:0;background:black;z-index:99999}
.scan{position:absolute;width:100%;height:2px;background:white;animation:scan .12s linear infinite}
@keyframes scan{from{top:-10px}to{top:110%}}

/* AUTH */
#auth{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:black;z-index:9999}
#authbox{border:1px solid #222;padding:30px;width:300px}
input,button{width:100%;padding:10px;background:black;border:1px solid #333;color:white}
button{background:white;color:black;font-weight:bold;cursor:pointer}
#error{color:red;font-size:12px;margin-top:10px}

/* APP */
#app{display:none;height:100vh}
.left{width:340px;border-right:1px solid #111;padding:20px}
.right{flex:1;padding:20px;overflow:auto}
.console{height:140px;border:1px solid #222;padding:10px;font-size:12px;margin-top:10px}
.card{border:1px solid #111;padding:15px;margin-bottom:15px}
.label{color:#777;font-size:11px}
.value{margin-bottom:6px}
.no{color:red}

@media(max-width:768px){
#app{flex-direction:column}
.left{width:100%;border-right:none;border-bottom:1px solid #111}
}
</style>
</head>
<body>

<div id="boot"></div>

<div id="auth">
<div id="authbox">
<h3>AUTHORIZED ACCESS</h3><br>
<input id="pass" type="password" placeholder="PASSWORD">
<button onclick="login()">ENTER</button>
<div id="error"></div>
</div>
</div>

<div id="app">
<div class="left">
<h2>GURMAN OSINT</h2><br>
<input id="num" placeholder="TARGET NUMBER">
<button onclick="fetchData()">EXECUTE</button>
<div class="console" id="console">SYSTEM READY</div>
</div>
<div class="right" id="out"><div class="no">NO TARGET</div></div>
</div>

<script>
/* BOOT */
for(let i=0;i<40;i++){
 let s=document.createElement("div");
 s.className="scan";
 s.style.animationDelay=Math.random()+"s";
 boot.appendChild(s);
}
setTimeout(()=>boot.remove(),1500);

/* AUTH */
const USER="GURMANDADDY", ADMIN="GURMANADMIN";
function login(){
 let v=pass.value;
 if(v===ADMIN)location.href="/admin";
 else if(v===USER){auth.style.display="none";app.style.display="flex";}
 else error.textContent="ACCESS DENIED";
}

/* LOG */
const log=t=>{console.textContent+="\\n"+t;console.scrollTop=9999};

/* FETCH */
async function fetchData(){
 let n=num.value.trim();
 if(!n)return log("INVALID INPUT");
 log("QUERY "+n);
 let r=await fetch("/api/search",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({number:n})});
 let d=await r.json();
 if(d.status==="blocked")out.innerHTML='<div class="no">BLOCKED</div>';
 else if(d.status==="ok"){
  out.innerHTML=d.results.map(r=>`
   <div class="card">
   <b>${r.name||'-'}</b><br>
   <span class="label">MOBILE</span><div class="value">${r.mobile}</div>
   <span class="label">FATHER</span><div class="value">${r.fname}</div>
   <span class="label">CIRCLE</span><div class="value">${r.circle}</div>
   <span class="label">EMAIL</span><div class="value">${r.email}</div>
   <span class="label">ADDRESS</span><div class="value">${(r.address||'').replace(/!/g,", ")}</div>
   </div>`).join("");
 }else out.innerHTML='<div class="no">NO DATA</div>';
}
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(INDEX_HTML)


@app.route("/admin")
def admin():
    return render_template_string(ADMIN_HTML, blocked=load_blocked())


@app.route("/block", methods=["POST"])
def block_route():
    n = re.sub(r"\D", "", request.form.get("number", ""))[-10:]
    if n:
        block_number(n)
    return redirect("/admin")


@app.route("/unblock/<num>")
def unblock_route(num):
    unblock_number(num)
    return redirect("/admin")


@app.route("/api/search", methods=["POST"])
def api_search():
    number = re.sub(r"\D", "", (request.json or {}).get("number", ""))[-10:]

    if number in {"9891668332", "9953535271"} or number in load_blocked():
        return jsonify({"status": "blocked"})

    try:
        r = requests.get(
            f"https://api.paanel.shop/numapi.php?action=api&key=num_gscyber&number={number}",
            timeout=10
        )
        data = r.json()
    except:
        return jsonify({"status": "no_record"})

    if not isinstance(data, list) or not data:
        return jsonify({"status": "no_record"})

    results = [{
        "mobile": x.get("mobile",""),
        "name": x.get("name",""),
        "fname": x.get("father_name",""),
        "circle": x.get("circle",""),
        "email": x.get("email",""),
        "address": x.get("address","")
    } for x in data]

    return jsonify({"status": "ok", "results": results})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
