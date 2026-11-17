#!/usr/bin/env python3
"""Segunda conferência, independente da conversão: relê a loja convertida e falha se algum app escapou
das regras (o GitHub Actions não publica a loja quando isto falha).

Uso: python3 garimpo/confere.py <pasta da loja convertida>
"""
import json
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from converter import ARQUIVOS_LIVRES, ID_RE, SEGREDO_RE, Recusa, confere_servico, le  # noqa: E402

ORIGENS_OK = ("${APP_DATA_DIR}/data", "${ROOT_FOLDER_HOST}/media/")


def volume_ok(v):
    if isinstance(v, dict):
        return v.get("type") == "tmpfs"
    partes = str(v).split(":")
    if len(partes) == 1:
        return partes[0].startswith("/")  # volume anônimo dentro do container
    o = partes[0]
    if ".." in o.split("/"):
        return False
    return o in ARQUIVOS_LIVRES or o.startswith("/dev/dri") or o == "${APP_DATA_DIR}/data" or any(o.startswith(p) for p in ORIGENS_OK)


def confere_loja(pasta):
    erros = []
    apps = os.path.join(pasta, "apps")
    portas = {}
    for d in sorted(os.listdir(apps)):
        base = os.path.join(apps, d)
        if not ID_RE.match(d):
            erros.append(f"{d}: nome inválido")
            continue
        try:
            cfg = json.loads(le(os.path.join(base, "config.json")))
            comp = yaml.safe_load(le(os.path.join(base, "docker-compose.yml")))
        except Exception as e:
            erros.append(f"{d}: não deu para ler ({e})")
            continue
        if cfg.get("id") != d:
            erros.append(f"{d}: id diferente da pasta")
        for nome in ("config.json", "docker-compose.yml", os.path.join("metadata", "description.md")):
            p = os.path.join(base, nome)
            if os.path.isfile(p) and SEGREDO_RE.search(le(p)):
                erros.append(f"{d}: {nome} tem algo com cara de chave secreta")
        p = cfg.get("port")
        if p in portas:
            erros.append(f"{d}: porta {p} repetida com {portas[p]}")
        portas[p] = d
        if not os.path.isfile(os.path.join(base, "metadata", "logo.jpg")) or not os.path.isfile(os.path.join(base, "metadata", "description.md")):
            erros.append(f"{d}: falta logo ou descrição")
        servicos = comp.get("services") or {}
        if d not in servicos:
            erros.append(f"{d}: falta o serviço com o nome do app")
        if sum(1 for s in servicos.values() if (s.get("x-runtipi") or {}).get("is_main")) != 1:
            erros.append(f"{d}: precisa de exatamente um serviço principal")
        if set(comp) - {"services", "x-runtipi", "configs", "secrets"}:
            erros.append(f"{d}: chave inesperada no compose: {sorted(set(comp) - {'services', 'x-runtipi', 'configs', 'secrets'})}")
        for n, s in servicos.items():
            try:
                confere_servico(n, s)
            except Recusa as e:
                erros.append(f"{d}: {e.args[0]}")
            if s.get("network_mode") and not str(s["network_mode"]).startswith("service:"):
                erros.append(f"{d}: o serviço {n} mexe na rede ({s['network_mode']})")
            for v in s.get("volumes") or []:
                if not volume_ok(v):
                    erros.append(f"{d}: o serviço {n} monta {v}")
            if re.search(r"docker\.sock", json.dumps(s)):
                erros.append(f"{d}: o serviço {n} cita o socket do Docker")
    return erros


if __name__ == "__main__":
    erros = confere_loja(sys.argv[1])
    for e in erros:
        print("ERRO", e)
    print(f"{len(erros)} problema(s)")
    sys.exit(1 if erros else 0)
