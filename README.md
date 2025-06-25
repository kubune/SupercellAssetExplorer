# SupercellAssetExplorer
File-like explorer for Supercell game-assets servers using mitmproxy made in python.

## Requirements
- Python 3.12 (I used it, I don't know which version is the lowest required lol)
- mitmproxy

## Inner workings
The script uses a `fingerprint.json` to actually list all files and directories. You donwload them from supercell servers directly.

It should work on all Supercell games except rouge (mo.co) as it doesn't provide `fingerprint.json` in the game-assets server.

## How to use
Install mitmproxy 10+ and use `mitmproxy -s .\main.py` to start the proxy.

Remember to actually setup the proxy in your system `127.0.0.1:8080`

Go to any game assets server and boom, you have a nice file-like explorer!

