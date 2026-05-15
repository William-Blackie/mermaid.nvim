import sys, json, urllib.request, ssl, zipfile, io

TOKEN = sys.argv[1]

req = urllib.request.Request(
    "https://api.github.com/repos/kevalin/mermaid.nvim/actions/runs?per_page=1&branch=feat/full-overhaul-031",
    headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
)
data = json.loads(urllib.request.urlopen(req).read())
run_id = data['workflow_runs'][0]['id']

ctx = ssl.create_default_context()
req2 = urllib.request.Request(
    f"https://api.github.com/repos/kevalin/mermaid.nvim/actions/runs/{run_id}/logs",
    headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}
)
resp = urllib.request.urlopen(req2, context=ctx)
bio = io.BytesIO(resp.read())
zf = zipfile.ZipFile(bio)

for name in sorted(zf.namelist()):
    if '0.9' in name and 'Run tests' in name:
        content = zf.read(name).decode('utf-8', errors='replace')
        lines = content.split('\n')
        printing = False
        print_count = 0
        for line in lines:
            if 'Fail' in line and '||' in line:
                if 'format-ignore case-insensitive' in line:
                    printing = True
                    print_count = 0
                elif 'Could not parse' in line:
                    printing = True
                    print_count = 0
                elif 'xychart-beta' in line:
                    printing = True
                    print_count = 0
                elif 'panel close' in line or 'panel open replaces' in line:
                    printing = True
                    print_count = 0
            if printing:
                print(line.rstrip())
                print_count += 1
                if print_count > 30:
                    printing = False
                    print("---")
