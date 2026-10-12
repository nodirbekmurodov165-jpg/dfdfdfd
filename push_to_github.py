import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
import webbrowser
from dulwich import porcelain

REPO_URL = "https://github.com/nodirbekmurodov165-jpg/dgdgdg.git"
USERNAME = "nodirbekmurodov165-jpg"
REPO_NAME = "dgdgdg"
CLIENT_ID = "178c6fc778ccc68e1d6a"


def stage_and_commit_latest() -> None:
    repo = porcelain.open_repo(".")
    cfg = repo.get_config()
    cfg.set((b"remote", b"origin"), b"url", REPO_URL.encode())
    cfg.write_to_path()

    files = [
        os.path.relpath(os.path.join(dp, f), ".")
        for dp, dn, fn in os.walk(".")
        for f in fn
        if not any(
            p in dp.replace("\\", "/").split("/")
            for p in [".git", "__pycache__", "data", "logs"]
        )
        and f not in [".env"]
    ]
    porcelain.add(repo, paths=files)
    sha = porcelain.commit(
        repo,
        message=b"Telegram AI Chatbot 24/7",
        author=b"Nodirbek Murodov <nodirbekmurodov165@gmail.com>",
        committer=b"Nodirbek Murodov <nodirbekmurodov165@gmail.com>",
    )
    repo.refs[b"refs/heads/main"] = sha
    repo.refs.set_symbolic_ref(b"HEAD", b"refs/heads/main")


def request_device_code() -> dict:
    req = urllib.request.Request(
        "https://github.com/login/device/code",
        data=f"client_id={CLIENT_ID}&scope=repo".encode(),
        headers={"Accept": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main() -> None:
    stage_and_commit_latest()
    dev = request_device_code()
    device_code = dev["device_code"]
    user_code = dev["user_code"]
    interval = int(dev.get("interval", 5)) + 1

    with open("logs/github_code.txt", "w", encoding="utf-8") as f:
        f.write(user_code)

    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", f'Set-Clipboard -Value "{user_code}"'], check=False)
        webbrowser.open("https://github.com/login/device")
    except Exception:
        pass

    print(f"GITHUB DEVICE CODE: {user_code}", flush=True)

    token_url = "https://github.com/login/oauth/access_token"
    payload = urllib.parse.urlencode(
        {
            "client_id": CLIENT_ID,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }
    ).encode()

    for _ in range(150):
        time.sleep(interval)
        req = urllib.request.Request(
            token_url,
            data=payload,
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())

        if "access_token" in data:
            token = data["access_token"]
            print("GitHub avtorizatsiyasi tasdiqlandi! Push qilinmoqda...", flush=True)
            auth_url = f"https://x-access-token:{token}@github.com/{USERNAME}/{REPO_NAME}.git"
            porcelain.push(".", auth_url, [b"refs/heads/main"])
            print(f"MUVAFFAQIYATLI PUSH QILINDI: {REPO_URL}", flush=True)
            return

        err = data.get("error")
        if err == "authorization_pending":
            continue
        elif err == "slow_down":
            interval += 5
            continue
        else:
            print("Xatolik:", data, flush=True)
            return


if __name__ == "__main__":
    main()
