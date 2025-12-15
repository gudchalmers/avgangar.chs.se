from flask import Flask, render_template_string
from monitor_vasttrafik import get_departures_for_stop

STOP_ID = "9021014001960000"  # Chalmers, Göteborg (stoparea gid)
REFRESH_SECONDS = 30

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Avgångar – Chalmers</title>
  <meta http-equiv="refresh" content="{{ refresh }}">
  <style>
    :root{
      --bg:#000;
      --text:#fff;
      --muted:rgba(255,255,255,.65);
      --rowA:rgba(255,255,255,.03);
      --rowB:rgba(255,255,255,.06);
      --shadow: rgba(0,0,0,.5);
      --barTrack: rgba(255,255,255,.12);
      --barFill: rgba(255,255,255,.35);
    }
    *{ box-sizing:border-box; }
    body{
      margin:0;
      background:var(--bg);
      color:var(--text);
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    }
    .wrap{
      padding: 32px 40px 72px;
      max-width: 1200px;
      margin: 0 auto;
    }
    h1{
      margin:0 0 18px;
      font-size: 56px;
      letter-spacing: .5px;
      font-weight: 800;
    }
    .sub{
      margin: -6px 0 18px;
      color: var(--muted);
      font-size: 18px;
    }
    table{
      width:100%;
      border-collapse: collapse;
      font-size: 28px;
    }
    thead th{
      text-align:left;
      color: var(--muted);
      font-weight: 650;
      padding: 14px 14px;
      border-bottom: 1px solid rgba(255,255,255,.08);
    }
    tbody tr:nth-child(odd){ background: var(--rowA); }
    tbody tr:nth-child(even){ background: var(--rowB); }
    td{
      padding: 16px 14px;
      vertical-align: middle;
    }

    .line-pill{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      min-width: 74px;
      height: 44px;
      padding: 0 14px;
      border-radius: 999px;
      font-weight: 800;
      box-shadow: 0 8px 24px var(--shadow);
    }
    .dest{
      font-weight: 650;
    }
    .platform{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      min-width: 44px;
      height: 44px;
      border-radius: 14px;
      background: rgba(255,255,255,.08);
      border: 1px solid rgba(255,255,255,.10);
      font-weight: 750;
    }
    .time {
    text-align: right;
    white-space: nowrap;
    }

    .time-main {
    font-size: 1.6rem;
    font-weight: 600;
    }

    .time-planned {
    font-size: 0.9rem;
    color: #9aa0a6;      
    margin-top: 2px;
    }
    .time small{
      color: var(--muted);
      font-weight: 650;
      margin-left: 10px;
    }

    .progress-wrap{
      position: fixed;
      left: 50%;
      transform: translateX(-50%);
      bottom: 18px;
      width: 320px;
      height: 6px;
      background: var(--barTrack);
      border-radius: 999px;
      overflow: hidden;
      filter: drop-shadow(0 6px 18px rgba(0,0,0,.55));
    }
    .progress-fill{
      height: 100%;
      width: 0%;
      background: var(--barFill);
      border-radius: 999px;
      transition: width .2s linear;
    }

    .cancel{
      color:#ffb3b3;
      font-weight: 750;
      margin-left: 10px;
      font-size: 20px;
      vertical-align: middle;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Chalmers, Göteborg</h1>
    <div class="sub">Uppdateras var {{ refresh }} s</div>

    <table>
      <thead>
        <tr>
          <th style="width:140px;">Linje</th>
          <th>Destination</th>
          <th style="width:160px;">Läge</th>
          <th style="width:220px; text-align:right;">Tid</th>
        </tr>
      </thead>
      <tbody>
        {% for d in deps %}
        <tr>
          <td>
            <span class="line-pill" style="background: {{ d.bg }}; color: {{ d.fg }};">
              {{ d.line }}
            </span>
          </td>
          <td class="dest">
            {{ d.direction }}
            {% if d.isCancelled %}
              <span class="cancel">INSTÄLLD</span>
            {% endif %}
          </td>
          <td><span class="platform">{{ d.platform }}</span></td>
         <td class="time">
                <div class="time-main">{{ d.time }}</div>
                {% if d.planned and d.planned != d.time %}
                    <div class="time-planned">{{ d.planned }}</div>
                {% endif %}
                </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <div class="progress-wrap" aria-hidden="true">
    <div class="progress-fill" id="bar"></div>
  </div>

  <script>
    // Diskret progress mot nästa refresh
    const refresh = {{ refresh|int }};
    const bar = document.getElementById("bar");
    const start = Date.now();

    function tick(){
      const elapsed = (Date.now() - start) / 1000;
      const p = Math.max(0, Math.min(1, elapsed / refresh));
      bar.style.width = (p * 100).toFixed(1) + "%";
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    deps = get_departures_for_stop(STOP_ID)
    return render_template_string(TEMPLATE, deps=deps, refresh=REFRESH_SECONDS)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
