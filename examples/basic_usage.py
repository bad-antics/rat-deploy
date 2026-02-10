from rat_deploy.core import RATDetector
d = RATDetector()
findings = d.scan_connections()
print(f"Suspicious connections: {len(findings)}")
for f in findings: print(f"  Port {f['port']}: {f['description']}")
