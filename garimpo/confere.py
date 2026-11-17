#!/usr/bin/env python3
"""Segunda conferência, independente da conversão: relê a loja convertida e falha se algum app escapou
das regras (o GitHub Actions não publica a loja quando isto falha).

Desde a decisão 62 do BrunOS (17/11/2026) apps que pedem poderes sobre o servidor entram na loja, mas
TODOS precisam estar no privilegios.json com a lista certa: é por ela que o README avisa, e um app com
privilégio escondido é exatamente o que esta conferência existe para pegar. Também confere o que não
funcionaria (rede de outro container, volumes_from, runtime estranho), chaves secretas escritas, portas
repetidas, logo, descrição e o formato da loja.

Uso: python3 garimpo/confere.py <pasta da loja convertida>
"""
import json
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from converter import ID_RE, SEGREDO_RE, Recusa, confere_servico, le, privilegios  # noqa: E402

ORIGENS_VARIAVEIS = ("${APP_DATA_DIR}", "${ROOT_FOLDER_HOST}/media")


def volume_ok(v):
    """Volume que o Runtipi sabe montar: sem '..' e sem variável que ele não preenche."""
    if isinstance(v, dict):
        if v.get("type") == "tmpfs":
            return True
        o = str(v.get("source") or "")
    else:
        partes = str(v).split(":")
        if len(partes) == 1:
            return partes[0].startswith("/")  # volume anônimo dentro do container
        o = partes[0]
    if ".." in o.split("/"):
        return False
    if "$" in o:
        return any(o == p or o.startswith(p + "/") for p in ORIGENS_VARIAVEIS)
    return True


def confere_loja(pasta):
    erros = []
    apps = os.path.join(pasta, "apps")
    portas = {}
    try:
        lista = json.loads(le(os.path.join(pasta, "privilegios.json")))
    except (OSError, ValueError):
        lista = None
        erros.append("falta o privilegios.json (ou está com erro)")
    vistos = set()
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
            rede = str(s.get("network_mode") or "")
            if rede and rede != "host" and not rede.startswith("service:"):
                erros.append(f"{d}: o serviço {n} usa a rede {rede}")
            for v in s.get("volumes") or []:
                if not volume_ok(v):
                    erros.append(f"{d}: o serviço {n} monta {v}")
        # privilégios: recalculados aqui e conferidos com a lista publicada (nada pode ficar escondido)
        tem = privilegios(comp)
        if lista is not None:
            declarados = lista.get(d) or []
            if sorted(tem) != sorted(declarados):
                erros.append(f"{d}: privilégios não batem com o privilegios.json (receita: {tem}; lista: {declarados})")
            if tem:
                vistos.add(d)
        # socket do Docker citado em qualquer lugar da receita: só se estiver na lista de privilégios
        if "docker.sock" in json.dumps(comp) and not any("socket do Docker" in t for t in tem):
            erros.append(f"{d}: cita o socket do Docker fora de um volume")
    for d in sorted(set(lista or {}) - vistos):
        erros.append(f"{d}: está no privilegios.json, mas não existe na loja (ou não pede nada)")
    return erros


if __name__ == "__main__":
    erros = confere_loja(sys.argv[1])
    for e in erros:
        print("ERRO", e)
    print(f"{len(erros)} problema(s)")
    sys.exit(1 if erros else 0)
