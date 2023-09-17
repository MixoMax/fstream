import time
import requests
from termcolor import colored

# Cloudflare API key
with open("cloudflare.token", "r") as f:
    token = f.read().strip()

def get_ext_ip():
    return requests.get("https://checkip.amazonaws.com").text.strip()
    


zone_id = "7cb01306b6b39f8c6b467115e5d1948e"

def update_dns(subdomain, proxied=True):
    headers = {
        "X-Auth-Email": "linushorn@gmx.net",
        "X-Auth-Key": token,
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": subdomain + ".linushorn.dev",
        "content": get_ext_ip(),
        "proxied": proxied
    }
    
    # put request
    #https://api.cloudflare.com/client/v4/zones/{zone_identifier}/dns_records/{identifier}
    if subdomain == "linushorn.dev" or subdomain == "@": # root domain
        full_domain = "linushorn.dev"
    else:
        full_domain = subdomain + ".linushorn.dev"
        
    identifier = requests.get("https://api.cloudflare.com/client/v4/zones/" + zone_id + "/dns_records?name=" + full_domain, headers=headers).json()["result"][0]["id"]
    r = requests.put("https://api.cloudflare.com/client/v4/zones/" + zone_id + "/dns_records/" + identifier, headers=headers, json=data)
    success = r.json()["success"]
    if success:
        print(colored("Successfully updated " + full_domain + " to " + get_ext_ip() + ".", "green"))
    elif r.json()["errors"][0]["code"] == 81058:
        print(colored("No changes made to " + full_domain + ".", "yellow"))
    else:
        print(colored("Failed to update " + full_domain + " to " + get_ext_ip() + ".", "red"))
        print(r.json())
    return success
   
while True:
    time.sleep(1)
    try:
        update_dns("@", proxied=True)
        update_dns("ssh", proxied=False)
    except Exception as e:
        print(colored("Error: " + str(e), "red"))
        continue