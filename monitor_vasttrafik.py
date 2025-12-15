import os
import requests
from datetime import datetime

CLIENT_ID = os.environ["VT_KEY"]
CLIENT_SECRET = os.environ["VT_SECRET"]

STOP_GID = "9021014001960000"
STOP_NAME = "Centralstationen, Göteborg"


def get_token() -> str:
    """Hämta access token från Västtrafik."""
    url = "https://ext-api.vasttrafik.se/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    resp = requests.post(url, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]



def get_departures(token: str, stop_gid: str):
    """Hämta avgångar för en stop-area."""
    url = f"https://ext-api.vasttrafik.se/pr/v4/stop-areas/{stop_gid}/departures"
    params = {
        "timeSpanInMinutes": 60,
        "maxDeparturesPerLineAndDirection": 2,
        "limit": 10,
        "offset": 0,
        "includeOccupancy": "false",
    }
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    results = resp.json()["results"]

    clean = []
    for d in results:
        sj = d.get("serviceJourney")
        if not sj:
            continue
        if "line" not in sj:
            continue
        clean.append(d)

    return clean



def format_time(ts: str) -> str:
    """Gör om API-tid till HH:MM."""
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.strftime("%H:%M")

def get_departures_for_stop(stop_gid: str):
    token = get_token()
    departures = get_departures(token, stop_gid)

    deps = []
    for d in departures:
        sj = d.get("serviceJourney")
        sp = d.get("stopPoint")
        if not sj or not sp:
            continue

        planned = d["plannedTime"]
        estimated = d.get("estimatedTime") or d.get("estimatedOtherwisePlannedTime") or planned

        planned_str = format_time(planned)
        est_str = format_time(estimated)

        deps.append({
            "line": sj["line"]["shortName"],
            "direction": sj["directionDetails"]["shortDirection"],
            "platform": sp.get("platform", "?"),
            "time": est_str,
            "planned": planned_str,
            "isCancelled": d.get("isCancelled", False),
            "bg": sj["line"].get("backgroundColor"),
            "fg": sj["line"].get("foregroundColor"),
        })

    return deps




def main():
    print(f"Avgångar från {STOP_NAME} (nästa 60 min):\n")

    token = get_token()
    departures = get_departures(token, STOP_GID)

    for d in departures:
        sj = d.get("serviceJourney")
        sp = d.get("stopPoint")

        if not sj or not sp:
            continue

        line = sj["line"]["shortName"]
        direction = sj["directionDetails"]["shortDirection"]
        stop_point = sp.get("platform", "?")

        planned = d["plannedTime"]
        estimated = d.get("estimatedTime") or d.get("estimatedOtherwisePlannedTime") or planned

        planned_str = format_time(planned)
        est_str = format_time(estimated)

        delay = ""
        if est_str != planned_str:
            delay = f" (plan {planned_str})"

        print(f"Linje {line} mot {direction} – Läge {stop_point} – {est_str}{delay}")
        

if __name__ == "__main__":
    main()
