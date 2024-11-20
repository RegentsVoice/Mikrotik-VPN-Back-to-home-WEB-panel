import re

def read_server_config(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        ip_match = re.search(r'GServerIp\s*=\s*"(.*?)"', content)
        port_match = re.search(r'GServerPort\s*=\s*(\d+)', content)
        ip = ip_match.group(1) if ip_match else None
        port = port_match.group(1) if port_match else None
        return ip, port

if __name__ == "__main__":
    import sys
    file_path = sys.argv[1]
    server_ip, server_port = read_server_config(file_path)
    if server_ip:
        print(f"IP={server_ip}")
    else:
        print("GServerIp not found")
    if server_port:
        print(f"PORT={server_port}")
    else:
        print("GServerPort not found")