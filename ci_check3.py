import sys, json, urllib.request, ssl, zipfile, io

TOKEN = sys.argv[1]

req = urllib.request.Request(
    "https://api.github.com/repos/kevalin/mermaid.nvim/actions/runs?per_page=1&branch=feat/full-overhaul-031",
    headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
)
data = json.loads(urllib.request.urlopen(req).read())
run_id = data['workflow_runs'][0]['id']

# Download logs
ctx = ssl.create_default_context()
req2 = urllib.request.Request(
    f"https://api.github.com/repos/kevalin/mermaid.nvim/actions/runs/{run_id}/logs",
    headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}
)
resp = urllib.request.urlopen(req2, context=ctx)
bio = io.BytesIO(resp.read())
zf = zipfile.ZipFile(bio)

# Find and print all test failures with actual vs expected
for name in sorted(zf.namelist()):
    if '0.9' in name and 'Run tests' in name:
        content = zf.read(name).decode('utf-8', errors='replace')
        relevant = False
        for line in content.split('\n'):
            stripped = line.strip()
            if 'Fail' in stripped and '||' in stripped:
                test = stripped.split('||')[1].strip() if '||' in stripped else stripped
                print(f"\n=== {test} ===")
                relevant = True
            elif relevant and ('Passed in:' in stripped or 'Expected:' in stripped):
                print(f"  {stripped}")
                if 'Passed in:' in stripped:
                    # Extract the actual string value
                    idx = stripped.find('Passed in:')
                    val = stripped[idx+10:].strip()
                    print(f"  GOT: {val}")
                if 'Expected:' in stripped:
                    idx = stripped.find('Expected:')
                    val = stripped[idx+9:].strip()
                    print(f"  EXP: {val}")
            elif relevant and stripped == '':
                relevant = False
