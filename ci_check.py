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
    print(f"Run #{r['run_number']}: {r['status']}/{r.get('conclusion','?')} | {sha}")

    # Get jobs for latest
    if r['head_sha'].startswith('53683a7'):
        req2 = urllib.request.Request(
            r['jobs_url'],
            headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
        )
        jobs = json.loads(urllib.request.urlopen(req2).read())
        for j in jobs.get('jobs', []):
            print(f"  Job: {j['name']} | {j['status']}/{j.get('conclusion','?')}")
            for s in j.get('steps', []):
                c = s.get('conclusion')
                if c == 'failure':
                    print(f"    Step: {s['name']} (number {s.get('number','?')})")

        # Try to get logs
        for fmt in [f"https://api.github.com/repos/kevalin/mermaid.nvim/actions/runs/{r['id']}/attempts/1/jobs"]:
            try:
                req3 = urllib.request.Request(
                    fmt,
                    headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
                )
                jobs2 = json.loads(urllib.request.urlopen(req3).read())
                for j in jobs2.get('jobs', []):
                    for s in j.get('steps', []):
                        c = s.get('conclusion')
                        if c == 'failure' and s.get('number') in [4, 5]:
                            print(f"\n  Step {s['number']}: {s['name']}")
                            print(f"  Started: {s.get('started_at','?')}")
            except Exception as e:
                print(f"  (can't get logs: {e})")
