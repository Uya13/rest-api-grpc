import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "screenshots"
OUT.mkdir(exist_ok=True)


def run(command):
    completed = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )
    return f"$ {command}\n{completed.stdout}{completed.stderr}\n"


checks = []
checks.append(run("curl http://localhost:8080/health"))
checks.append(run("curl http://localhost:8080/auth/health"))
checks.append(run("curl http://localhost:8080/todos/"))

login_command = (
    "curl -s -X POST http://localhost:8080/auth/login "
    "-H \"Content-Type: application/json\" "
    "-d \"{\\\"username\\\":\\\"student\\\",\\\"password\\\":\\\"student123\\\"}\""
)
login_output = subprocess.check_output(login_command, shell=True, text=True, encoding="utf-8")
checks.append(f"$ {login_command}\n{login_output}\n")
token = json.loads(login_output)["token"]

checks.append(run(f"curl http://localhost:8080/todos/ -H \"Authorization: Bearer {token}\""))
checks.append(run(
    "curl -X POST http://localhost:8080/todos/ "
    "-H \"Content-Type: application/json\" "
    f"-H \"Authorization: Bearer {token}\" "
    "-d \"{\\\"title\\\":\\\"Task created through Nginx API Gateway\\\"}\""
))

(OUT / "nginx-gateway-curl-results.txt").write_text("\n".join(checks), encoding="utf-8")
print(f"Saved: {OUT / 'nginx-gateway-curl-results.txt'}")
