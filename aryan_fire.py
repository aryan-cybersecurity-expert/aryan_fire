import argparse
import os
import string
import itertools
import pypdf
import pyzipper
from tqdm import tqdm
import msoffcrypto
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

# ANSI Colors
G = "\033[92m"   # Bright Green
Y = "\033[93m"   # Yellow
R = "\033[91m"   # Red
C = "\033[96m"   # Cyan
B = "\033[94m"   # Blue
W = "\033[97m"   # White
M = "\033[95m"   # Magenta
END = "\033[0m"

BANNER = f"""{G}
  █████╗ ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗
 ██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗████╗  ██║
 ███████║██████╔╝ ╚████╔╝ ███████║██╔██╗ ██║
 ██╔══██║██╔══██╗  ╚██╔╝  ██╔══██║██║╚██╗██║
 ██║  ██║██║  ██║   ██║   ██║  ██║██║ ╚████║
 ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝

{Y}     F I R E   P A S S W O R D   C R A C K E R{END}
{C}         v3.0  |  by ARYAN CYBERSECURITY EXPERT{END}
{G}===================================================={END}
"""

def show_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(BANNER)
    print(f"{Y}[!] DISCLAIMER - PADHO DHYAN SE{END}")
    print(f"{G}----------------------------------------------------{END}")
    print(f"{W}  Ye tool SIRF EDUCATIONAL PURPOSE ke liye hai.")
    print(f"  Apni hi file ka bhula hua password recover karne ke liye.{END}")
    print()
    print(f"{R}  * IT Act 2000 (Sec 43 & 66): Bina likhit permission")
    print(f"    kisi ki file crack karna CRIME hai. Jail ho sakti hai.{END}")
    print(f"{R}  * Sirf apni files ke liye use karo. Ethical raho.{END}")
    print(f"{G}===================================================={END}")
    print()


class AryanFire:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"[!] File '{file_path}' not found!")

        self.filename = os.path.basename(file_path)
        self.base_name = os.path.splitext(self.filename)[0]
        self.extension = os.path.splitext(file_path)[1].lower()

        if self.extension not in ['.pdf', '.pptx', '.zip', '.rar', '.docx', '.xlsx']:
            raise ValueError(f"[!] Unsupported: {self.extension}")

        self.found_password = None
        self.lock = threading.Lock()
        self.checked = 0

    def _check_pdf(self, pw):
        try:
            r = pypdf.PdfReader(self.file_path)
            if r.is_encrypted:
                return bool(r.decrypt(pw))
        except Exception:
            pass
        return False

    def _check_zip(self, pw):
        try:
            with pyzipper.AESZipFile(self.file_path) as zf:
                zf.setpassword(pw.encode('utf-8'))
                zf.namelist()
                return True
        except Exception:
            return False

    def _check_office(self, pw):
        try:
            with open(self.file_path, 'rb') as f:
                office = msoffcrypto.OfficeFile(f)
                office.load_key(password=pw)
                return True
        except Exception:
            return False

    def try_password(self, pw):
        if self.found_password:
            return
        found = False
        if self.extension == '.pdf':
            found = self._check_pdf(pw)
        elif self.extension in ['.zip', '.rar']:
            found = self._check_zip(pw)
        else:
            found = self._check_office(pw)

        with self.lock:
            self.checked += 1
            if found and not self.found_password:
                self.found_password = pw

    def generate_smart_words(self):
        # Remove common tags
        base = self.base_name
        for token in ['_protected', '-protected', '_locked', '-locked',
                      '_password', '.protected']:
            base = base.replace(token, ' ')
        # Split by spaces, underscore, dash
        for sep in ['_', '-', '.']:
            base = base.replace(sep, ' ')
        words = [w for w in base.split() if len(w) > 1]

        print(f"{C}[*] Filename : {W}{self.filename}{END}")
        print(f"{C}[*] Keywords : {W}{words}{END}")

        cands = set()
        suffixes = ['', '1', '12', '123', '1234', '12345', '007', '786',
                    '2024', '2025', '2026', '@123', '#123', '!123', '_123']
        symbols = ['@', '#', '!', '$', '_', '*', '&']

        for w in words:
            cands.add(w); cands.add(w.lower()); cands.add(w.upper())
            cands.add(w.capitalize()); cands.add(w.title())
            for s in suffixes:
                cands.add(w + s); cands.add(w.lower() + s)
                cands.add(w.upper() + s); cands.add(w.capitalize() + s)
            for sym in symbols:
                cands.add(w + sym); cands.add(sym + w)

        # Consecutive word joins
        n = len(words)
        for i in range(n):
            for j in range(i + 2, n + 1):
                joined = ''.join(words[i:j])
                cands.add(joined)
                cands.add(joined.lower())
                cands.add(joined.upper())
                cands.add(joined.capitalize())
                for s in suffixes:
                    cands.add(joined + s)
                    cands.add(joined.upper() + s)

        # Leetspeak
        leet = {'a':'@','e':'3','i':'1','o':'0','s':'$','t':'7','g':'9','b':'8'}
        for w in words:
            x = w.lower()
            for k, v in leet.items():
                x = x.replace(k, v)
            cands.add(x)

        return list(cands)

    def run_smart(self, workers=4):
        print(f"\n{G}[*] MODE: SMART ATTACK (Filename-Based){END}")
        cands = self.generate_smart_words()
        print(f"{C}[*] Smart guesses : {W}{len(cands)}{END}")
        print(f"{C}[*] Threads       : {W}{workers}{END}\n")

        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(self.try_password, p) for p in cands]
            for f in tqdm(as_completed(futs), total=len(futs),
                          desc="Cracking", colour="green"):
                if self.found_password:
                    break
        return self.found_password

    def run_dict(self, wl, workers=4, limit=500000):
        if not os.path.exists(wl):
            print(f"{R}[!] Wordlist not found: {wl}{END}")
            return None
        print(f"\n{G}[*] MODE: DICTIONARY ATTACK{END}")
        print(f"{C}[*] Wordlist : {W}{wl}{END}")
        with open(wl, 'r', encoding='utf-8', errors='ignore') as f:
            pws = [l.strip() for l in f if l.strip()][:limit]
        print(f"{C}[*] Passwords: {W}{len(pws)}{END}")
        print(f"{C}[*] Threads  : {W}{workers}{END}\n")
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(self.try_password, p) for p in pws]
            for f in tqdm(as_completed(futs), total=len(futs),
                          desc="Cracking", colour="green"):
                if self.found_password:
                    break
        return self.found_password


def main():
    show_banner()

    p = argparse.ArgumentParser(description="Aryan Fire - Password Cracker")
    p.add_argument("file", help="Locked file (.pdf, .zip, .pptx)")
    p.add_argument("-w", "--wordlist", default=None)
    p.add_argument("-t", "--threads", type=int, default=4)
    p.add_argument("--mode", choices=['smart', 'dict'], default='smart')
    args = p.parse_args()

    try:
        tool = AryanFire(args.file)
        t0 = time.time()

        if args.mode == 'dict' and args.wordlist:
            r = tool.run_dict(args.wordlist, args.threads)
        else:
            r = tool.run_smart(args.threads)
            if not r:
                rockyou = "/usr/share/wordlists/rockyou.txt"
                if os.path.exists(rockyou):
                    print(f"\n{Y}[*] Smart attack fail. Trying top 5 lakh of rockyou.txt...{END}")
                    r = tool.run_dict(rockyou, args.threads, limit=500000)

        e = time.time() - t0
        print("\n" + G + "=" * 60 + END)
        if r:
            print(f"{G}[+] ✅ SUCCESS! Password : {W}{r}{END}")
            print(f"{G}[+] Time              : {e:.2f} seconds{END}")
        else:
            print(f"{R}[-] ❌ Password not found.{END}")
            print(f"{Y}[-] Time: {e:.2f} seconds{END}")
            print(f"{Y}[!] Tip: Password strong ho sakta hai, ya list me nahi hai.{END}")
        print(G + "=" * 60 + END)

    except Exception as ex:
        print(f"{R}Error: {ex}{END}")


if __name__ == "__main__":
    main()
