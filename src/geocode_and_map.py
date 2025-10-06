import argparse, os, time
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from .config import DATA_DIR, OUT_DIR, GEOCODER, GOOGLE_MAPS_API_KEY

def geocode_free(df):
    geolocator = Nominatim(user_agent="la-food-scenes-map")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    lats, lngs = [], []
    for name, hood in zip(df["name"], df["neighborhood"].fillna("")):
        query = f"{name}, {hood}, Los Angeles, CA"
        try:
            loc = geocode(query)
            if loc:
                lats.append(loc.latitude); lngs.append(loc.longitude)
            else:
                lats.append(None); lngs.append(None)
        except Exception:
            lats.append(None); lngs.append(None)
    df["lat"] = lats; df["lng"] = lngs
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=["nominatim","google"], default="nominatim")
    args = ap.parse_args()

    csv_path = os.path.join(DATA_DIR, "mentions_clean.csv")
    df = pd.read_csv(csv_path)

    if args.provider == "nominatim":
        df = geocode_free(df)
    else:
        # Placeholder for Google Maps Geocoding (requires API key)
        import requests
        key = GOOGLE_MAPS_API_KEY
        if not key:
            raise RuntimeError("GOOGLE_MAPS_API_KEY is missing for provider=google")
        lats, lngs = [], []
        for name, hood in zip(df["name"], df["neighborhood"].fillna("")):
            query = f"{name}, {hood}, Los Angeles, CA"
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={requests.utils.quote(query)}&key={key}"
            resp = requests.get(url).json()
            if resp.get("results"):
                loc = resp["results"][0]["geometry"]["location"]
                lats.append(loc["lat"]); lngs.append(loc["lng"])
            else:
                lats.append(None); lngs.append(None)
        df["lat"] = lats; df["lng"] = lngs

    # Make a Folium map
    import folium
    m = folium.Map(location=[34.0522, -118.2437], zoom_start=10)
    for _, r in df.iterrows():
        if pd.notna(r.get("lat")) and pd.notna(r.get("lng")):
            popup = f"<b>{r['name']}</b><br>{r.get('cuisine','') or ''} — {r.get('neighborhood','') or ''}<br>Buzz: {int(r['score_buzz'])} • Trend: {round(r['score_trend'],2)}"
            folium.Marker([r["lat"], r["lng"]], popup=popup).add_to(m)
    out_html = os.path.join(OUT_DIR, "la_food_map.html")
    m.save(out_html)
    df.to_csv(os.path.join(DATA_DIR, "mentions_geocoded.csv"), index=False)
    print(f"Saved map -> {out_html}")

if __name__ == "__main__":
    main()
