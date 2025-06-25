from mitmproxy import http
import requests

ASSET_URLS = [
    "https://game-assets.brawlstarsgame.com/",
    "https://game-assets.squadbustersgame.com/",
    "https://game-assets.clashroyaleapp.com",
    "https://game-assets.haydaygame.com",
    "https://game-assets.clashofclans.com"
]

class Data:
    data: dict = {}
    sha: str = ""

def make_entry(name: str, href: str, is_folder=False) -> str:
    icon = "📁" if is_folder else "📄"
    target = "" if is_folder else 'target="_blank"'
    return f'<tr><td><a href="{href}" {target}>{icon} {name}</a></td></tr>'

def make_html(title: str, entries: list[str]) -> str:
    return f"""<html><head><title>SupercellAssetExplorer</title>
    <style>
        body {{ background:#111; color:#eee; font-family:sans-serif }}
        table {{ width:100%; border-collapse:collapse }}
        th,td {{ padding:8px; border-bottom:1px solid #444 }}
        th {{ background:#222 }}
        h1 {{ border-bottom:2px solid #555 }}
        h2 {{ font-size: 40px; text-align: center; margin: 0px }}
    </style></head><body>
    <h2>SupercellAssetExplorer by kubune</h2>
    <h1>Contents of: {title}</h1>
    <table><tr><th>List of available files</th></tr>{''.join(entries)}</table>
    </body></html>"""

def build_entries(prefix: str) -> list[str]:
    seen, folders, files = set(), [], []
    for f in Data.data.get("files", []):
        path = f["file"]
        if path.startswith(prefix):
            remainder = path[len(prefix):]
            if "/" in remainder:
                folder = remainder.split("/")[0]
                if folder not in seen:
                    seen.add(folder)
                    folders.append(make_entry(folder, f"{folder}/", is_folder=True))
            elif remainder and remainder not in seen:
                seen.add(remainder)
                files.append(make_entry(remainder, remainder))
    return sorted(folders) + sorted(files)

def do_request(flow: http.HTTPFlow) -> None:
    url = flow.request.pretty_url
    try:
        if url.endswith("/"):
            prefix = "/".join(url.split("/")[4:-1])
            prefix = f"{prefix}/" if prefix else ""
            entries = build_entries(prefix)
            flow.response = http.Response.make(200, make_html(prefix.rstrip("/"), entries), {"Content-Type": "text/html"})

        elif "fingerprint.json" not in url and len(url.split("/")) <= 4:
            base = url.rstrip("/")
            Data.sha = base
            resp = requests.get(f"{base}/fingerprint.json", verify=False, proxies={"http": None, "https": None})
            resp.raise_for_status()
            Data.data = resp.json()
            path = base.split("/")[-1]

            entries = []
            seen, folders, files = set(), [], []
            for f in Data.data.get("files", []):
                parts = f["file"].split("/")
                if len(parts) > 1:
                    folder = parts[0]
                    if folder not in seen:
                        seen.add(folder)
                        folders.append(make_entry(folder, f"{path}/{folder}/", is_folder=True))
                else:
                    files.append(make_entry(parts[0], f"{path}/{parts[0]}"))
            entries = sorted(folders) + sorted(files)
            flow.response = http.Response.make(200, make_html(path, entries), {"Content-Type": "text/html"})

    except Exception:
        flow.response = http.Response.make(502, "wrong fingerprint", {"Content-Type": "text/html"})

def request(flow: http.HTTPFlow) -> None:
    if any(flow.request.pretty_url.startswith(url) for url in ASSET_URLS):
        do_request(flow)
