import sys, json, urllib.request

TOKEN = sys.argv[1]

# Get latest runs
req = urllib.request.Request(
    "https://api.github.com/repos/kevalin/mermaid.nvim/actions/runs?per_page=5&branch=feat/full-overhaul-031",
    headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
)
data = json.loads(urllib.request.urlopen(req).read())

for r in data.get('workflow_runs', []):
    sha = r['head_sha'][:8]
    print(f"Run #{r['run_number']}: ID={r['id']} status={r['status']} conclusion={r.get('conclusion','?')} | {sha}")

# Get the latest failing run
latest = data['workflow_runs'][0]
run_id = latest['id']

# Try downloading logs
import ssl
ctx = ssl.create_default_context()
req2 = urllib.request.Request(
    f"https://api.github.com/repos/kevalin/mermaid.nvim/actions/runs/{run_id}/logs",
    headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}
)

try:
    resp = urllib.request.urlopen(req2, context=ctx)
    content_type = resp.headers.get('Content-Type', '')
    print(f"\nLogs Content-Type: {content_type}")
    
    # Save and inspect
    data = resp.read()
    with open('/tmp/gh_logs7.zip', 'wb') as f:
        f.write(data)
    
    import zipfile
    import io
    bio = io.BytesIO(data)
    zf = zipfile.ZipFile(bio)
    print(f"Zip OK: {len(zf.namelist())} files")
    
    for name in sorted(zf.namelist()):
        if 'luacheck' in name.lower() and '4_Run' in name:
            content = zf.read(name).decode('utf-8', errors='replace')
            print(f"\n=== LUACHECK ===")
            for l in content.split('\n')[-6:]:
                print(l)
        if '0.9' in name and 'Run tests' in name:
            content = zf.read(name).decode('utf-8', errors='replace')
            # Find failures
            failures = [l for l in content.split('\n') if 'Fail' in l and '||' in l]
            for f in failures:
                test = f.split('||')[1].strip() if '||' in f else f
                print(f"  FAIL: {test}")
            # Check for specific assertion failures
            for l in content.split('\n'):
                if 'Passed in:' in l or 'Expected:' in l:
                    print(f"    {l.strip()}")
except Exception as e:
    print(f"Error: {e}")
