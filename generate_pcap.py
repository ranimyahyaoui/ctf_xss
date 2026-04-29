from scapy.all import *
import random

packets = []
SERVER_IP = "172.16.0.10"
HACKER_IP = "10.0.0.42"
ADMIN_IP = "10.0.0.5"

# 1. Le Hacker essaie plein de faux codes PIN (Bruteforce)
faux_pins = ["0000", "1111", "1234", "9999", "4321", "5555", "7777"]
sport = 10000

for pin in faux_pins:
    sport += 1
    # Le Hacker envoie le faux code
    req = f"POST /api/maintenance/auth HTTP/1.1\r\nHost: {SERVER_IP}\r\n\r\n{{\"pin_code\": \"{pin}\"}}"
    pkt_req = IP(src=HACKER_IP, dst=SERVER_IP) / TCP(sport=sport, dport=5000, flags="PA") / Raw(load=req)
    
    # Le Serveur répond "ERREUR 401"
    resp = f"HTTP/1.1 401 Unauthorized\r\n\r\n{{\"status\": \"error\", \"message\": \"PIN invalide\"}}"
    pkt_resp = IP(src=SERVER_IP, dst=HACKER_IP) / TCP(sport=5000, dport=sport, flags="PA") / Raw(load=resp)
    
    packets.extend([pkt_req, pkt_resp])

# 2. Le Vrai Administrateur tape le bon code !
sport += 1
real_pin = "8492" # LE SEUL VRAI CODE

# L'Admin envoie le vrai code
req = f"POST /api/maintenance/auth HTTP/1.1\r\nHost: {SERVER_IP}\r\n\r\n{{\"pin_code\": \"{real_pin}\"}}"
pkt_req = IP(src=ADMIN_IP, dst=SERVER_IP) / TCP(sport=sport, dport=5000, flags="PA") / Raw(load=req)

# Le Serveur répond "SUCCÈS 200 OK"
resp = f"HTTP/1.1 200 OK\r\n\r\n{{\"status\": \"success\", \"message\": \"Terminal déverrouillé\"}}"
pkt_resp = IP(src=SERVER_IP, dst=ADMIN_IP) / TCP(sport=5000, dport=sport, flags="PA") / Raw(load=resp)

packets.extend([pkt_req, pkt_resp])

# 3. On sauvegarde le fichier
wrpcap("capture.pcap", packets)
print("Fichier 'capture.pcap' généré avec le piège HTTP 401 / 200 OK !")