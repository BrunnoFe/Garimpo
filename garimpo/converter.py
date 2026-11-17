#!/usr/bin/env python3
"""Garimpo: converte uma loja de apps do CasaOS/ZimaOS para o formato de loja do Runtipi.

Uso:
    python3 garimpo/converter.py --origem casaos --fonte <pasta da loja> --oficial <pasta da loja oficial do Runtipi>
                                 --saida <pasta da loja convertida> [--origens origens.json]

A <saida> é o ramo da loja convertida (ex.: ramo "casaos"). O que já estiver lá é lido para manter o
tipi_version e as datas de cada app (o Runtipi só avisa de atualização quando o tipi_version sobe), e
depois a pasta apps/ é reescrita do zero.

Segurança: as lojas de origem são de terceiros. Receitas que dão poder sobre o servidor (privileged,
socket do Docker, rede do host, pastas do sistema, poderes de administrador do Linux, aparelhos além da
placa de vídeo) são recusadas, e a lista de recusados vai para o README da loja com o motivo.
"""

import argparse
import copy
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

import yaml

# ── regras de segurança ──────────────────────────────────────────────────────────────────────────

# poderes do Linux que dão controle do servidor (ou da rede dele)
CAPS_PROIBIDAS = {
    "ALL", "SYS_ADMIN", "NET_ADMIN", "SYS_MODULE", "SYS_RAWIO", "SYS_PTRACE", "SYS_BOOT", "SYS_TIME",
    "DAC_READ_SEARCH", "LINUX_IMMUTABLE", "MAC_ADMIN", "MAC_OVERRIDE", "SYSLOG", "BPF", "PERFMON",
}
# pastas do servidor que um app nunca pode montar
PASTAS_SISTEMA = (
    "/", "/bin", "/boot", "/dev", "/etc", "/home", "/lib", "/lib32", "/lib64", "/media", "/mnt", "/opt",
    "/proc", "/root", "/run", "/sbin", "/srv", "/sys", "/usr", "/var",
)
# arquivos do sistema que podem ser montados, sempre só para leitura (hora certa)
ARQUIVOS_LIVRES = {"/etc/localtime", "/etc/timezone"}
# chaves do serviço que o conversor entende; o resto passa como está (compose padrão)
CHAVES_TIRADAS = {"restart", "container_name", "x-casaos", "network_mode", "networks"}

# ── mapeamentos ──────────────────────────────────────────────────────────────────────────────────

CATEGORIAS = {
    "media": "media", "productivity": "utilities", "ai": "ai", "networking": "network", "network": "network",
    "developer": "development", "development": "development", "home": "automation", "finance": "finance",
    "social": "social", "others": "utilities", "utilities": "utilities", "photography": "photography",
    "music": "music", "books": "books", "gaming": "gaming", "games": "gaming", "security": "security",
    "backup": "data", "data": "data", "download": "media", "downloader": "media", "automation": "automation",
}
ARQUITETURAS = {"amd64": "amd64", "x86_64": "amd64", "arm64": "arm64", "aarch64": "arm64"}
# pastas de mídia do CasaOS → pasta de mídia compartilhada do Runtipi
MIDIA = [
    ("/DATA/Media", "${ROOT_FOLDER_HOST}/media/data"),
    ("/DATA/Downloads", "${ROOT_FOLDER_HOST}/media/downloads"),
    ("/DATA/Gallery", "${ROOT_FOLDER_HOST}/media/data/images"),
    ("/DATA/Documents", "${ROOT_FOLDER_HOST}/media/data/documents"),
]
SUBPASTAS_MIDIA = {"movies": "movies", "tv shows": "tv", "tvshows": "tv", "tv": "tv", "music": "music", "books": "books",
                   "photos": "images", "pictures": "images", "images": "images", "podcasts": "podcasts"}
VERSAO_MINIMA_RUNTIPI = "4.7.0"  # a primeira versão que os apps oficiais em docker-compose.yml pedem
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
VAR_RE = re.compile(r"(?<!\$)\$(?:\{([A-Za-z_][A-Za-z0-9_]*)(?:[:?-][^}]*)?\}|([A-Za-z_][A-Za-z0-9_]*))")
MAX_LOGO = 2 << 20
# variáveis que o Runtipi já preenche (ou que são do shell dentro do container): não viram perguntas
VARS_CONHECIDAS = {
    "APP_DATA_DIR", "ROOT_FOLDER_HOST", "APP_PORT", "APP_DOMAIN", "APP_PROTOCOL", "APP_ID", "APP_HOST",
    "APP_EXPOSED", "APP_URN", "APP_STORE_ID", "LOCAL_DOMAIN", "INTERNAL_IP", "RUNTIPI_MEDIA_DIR", "TZ",
    "UID", "GID", "HOME", "PATH", "HOSTNAME", "PWD", "USER",
}


# variável que guarda segredo (o valor fixo vira um "random" do Runtipi, gerado em cada instalação)
NOME_SEGREDO = re.compile(r"(SECRET|PASSWORD|PASSWD|TOKEN|API_?KEY|PRIVATE_?KEY|_KEY$|^KEY$|SALT)", re.I)
# coisas com cara de chave de verdade: nunca publicar (o GitHub também barra)
SEGREDO_RE = re.compile(
    r"(sk-[A-Za-z0-9_-]{20,}|sk-proj-[A-Za-z0-9_-]{10,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"
    r"|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")


class Recusa(Exception):
    """App que não entra na loja convertida (o motivo vai para o README)."""


# ── utilidades ───────────────────────────────────────────────────────────────────────────────────

def le(caminho):
    with open(caminho, encoding="utf-8") as f:
        return f.read()


def le_bytes(caminho):
    with open(caminho, "rb") as f:
        return f.read()


def grava(caminho, conteudo):
    with open(caminho, "wb" if isinstance(conteudo, bytes) else "w", **({} if isinstance(conteudo, bytes) else {"encoding": "utf-8"})) as f:
        f.write(conteudo)

def texto(campo, idioma_preferido=("pt_BR", "pt_PT", "en_US")):
    """Escolhe o texto em português quando existe, senão em inglês (os campos do CasaOS são por idioma)."""
    if isinstance(campo, str):
        return campo.strip()
    if not isinstance(campo, dict):
        return ""
    for k in idioma_preferido:
        v = campo.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    for v in campo.values():
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def limpa_id(s):
    s = re.sub(r"[^a-z0-9-]+", "-", str(s or "").lower()).strip("-")
    s = re.sub(r"-{2,}", "-", s)[:63].strip("-")
    return s


def normaliza(s):
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def url_ok(u):
    return isinstance(u, str) and u.startswith(("https://", "http://")) and len(u) <= 300 and " " not in u


def troca_vars(valor, app_id, desconhecidas):
    """Troca as variáveis do CasaOS pelas do Runtipi; anota as que não conhece (viram perguntas da instalação)."""
    if isinstance(valor, str):
        def f(m):
            nome = m.group(1) or m.group(2)
            if nome == "AppID":
                return app_id
            if nome in ("PUID", "PGID"):
                return "1000"
            if nome == "TZ":
                return "${TZ}"
            if nome == "WEBUI_PORT":
                return "${APP_PORT}"
            if nome.isupper() and nome not in VARS_CONHECIDAS:
                desconhecidas.add(nome)
            return m.group(0)
        return VAR_RE.sub(f, valor)
    if isinstance(valor, list):
        return [troca_vars(v, app_id, desconhecidas) for v in valor]
    if isinstance(valor, dict):
        return {k: troca_vars(v, app_id, desconhecidas) for k, v in valor.items()}
    return valor


def segredos_fixos(servicos):
    """Valores fixos de variáveis de segredo (16+ letras, sem variável dentro), na ordem em que aparecem."""
    achados = []
    for s in servicos.values():
        env = s.get("environment") if isinstance(s, dict) else None
        pares = env.items() if isinstance(env, dict) else (str(e).split("=", 1) for e in env or [] if "=" in str(e))
        for k, v in pares:
            v = "" if v is None else str(v)
            if NOME_SEGREDO.search(str(k)) and len(v) >= 16 and "$" not in v and " " not in v and v not in achados:
                achados.append(v)
    return achados


def troca_texto(valor, trocas):
    if isinstance(valor, str):
        for velho, novo in trocas.items():
            valor = valor.replace(velho, novo)
        return valor
    if isinstance(valor, list):
        return [troca_texto(v, trocas) for v in valor]
    if isinstance(valor, dict):
        return {k: troca_texto(v, trocas) for k, v in valor.items()}
    return valor


def dentro_de(caminho, pasta):
    return caminho == pasta or caminho.startswith(pasta.rstrip("/") + "/")


def pasta_midia(resto):
    partes = [p for p in resto.split("/") if p]
    if partes:
        partes[0] = SUBPASTAS_MIDIA.get(partes[0].lower(), re.sub(r"[^a-z0-9._-]+", "-", partes[0].lower()))
    return "/".join(partes)


def converte_origem_volume(origem, servico):
    """Pasta do servidor no CasaOS → pasta no Runtipi. Recusa o que é do sistema."""
    o = re.sub(r"/{2,}", "/", origem.strip())
    if ".." in o.split("/"):
        raise Recusa(f"o serviço {servico} monta uma pasta com '..'")
    if "docker.sock" in o or o.endswith("/docker") and dentro_de(o, "/var/run"):
        raise Recusa(f"o serviço {servico} usa o socket do Docker (controle total do servidor)")
    if o.startswith("./"):
        return "${APP_DATA_DIR}/data/" + o[2:].strip("/")
    if not o.startswith("/"):
        if o.startswith("$"):
            raise Recusa(f"o serviço {servico} monta a pasta {o}, que depende de uma variável desconhecida")
        # volume com nome: vira uma pasta do app (entra no backup do Runtipi)
        return "${APP_DATA_DIR}/data/volumes/" + re.sub(r"[^A-Za-z0-9._-]+", "-", o)
    o = o.rstrip("/") or "/"
    if dentro_de(o, "/DATA/AppData"):
        partes = o.split("/")[4:]  # tira /DATA/AppData/<app>
        return "${APP_DATA_DIR}/data" + ("/" + "/".join(partes) if partes else "")
    for casa, runtipi in MIDIA:
        if dentro_de(o, casa):
            resto = pasta_midia(o[len(casa):])
            return runtipi + ("/" + resto if resto else "")
    if o == "/DATA":
        return "${ROOT_FOLDER_HOST}/media/data"
    if dentro_de(o, "/DATA"):
        return "${ROOT_FOLDER_HOST}/media/data/" + pasta_midia(o[len("/DATA"):])
    if o in ARQUIVOS_LIVRES:
        return o
    if o.startswith("/dev/dri"):
        return o
    for p in PASTAS_SISTEMA:
        if dentro_de(o, p):
            raise Recusa(f"o serviço {servico} monta a pasta {o} do servidor")
    raise Recusa(f"o serviço {servico} monta a pasta {o}, fora das pastas do CasaOS")


def converte_volumes(volumes, servico):
    out = []
    for v in volumes or []:
        if isinstance(v, str):
            partes = v.split(":")
            if len(partes) == 1:  # volume anônimo dentro do container
                out.append(v)
                continue
            origem, destino = partes[0], partes[1]
            modo = partes[2] if len(partes) > 2 else ""
        elif isinstance(v, dict):
            tipo = v.get("type", "bind")
            if tipo == "tmpfs":
                out.append(v)
                continue
            origem, destino = str(v.get("source") or ""), str(v.get("target") or "")
            modo = "ro" if v.get("read_only") else ""
            if not origem:
                out.append(destino)
                continue
        else:
            raise Recusa(f"o serviço {servico} tem um volume que não entendi")
        if not destino.startswith("/"):
            raise Recusa(f"o serviço {servico} tem um volume sem destino")
        nova = converte_origem_volume(origem, servico)
        if nova in ARQUIVOS_LIVRES or nova.startswith("/dev/dri"):
            modo = "ro" if nova in ARQUIVOS_LIVRES else modo
        modo = "ro" if "ro" in modo.split(",") else ""
        out.append(f"{nova}:{destino}" + (":ro" if modo else ""))
    return out


def confere_servico(nome, s):
    """Recusa o que dá poder sobre o servidor."""
    if s.get("privileged") in (True, "true", "True"):
        raise Recusa(f"o serviço {nome} pede privileged (controle total do servidor)")
    rede = str(s.get("network_mode") or "")
    if rede == "host":
        raise Recusa(f"o serviço {nome} usa a rede do servidor (network_mode: host)")
    if rede.startswith("container:"):
        raise Recusa(f"o serviço {nome} usa a rede de outro container de fora do app")
    for k in ("pid", "ipc", "userns_mode", "uts", "cgroup"):
        if str(s.get(k) or "") == "host":
            raise Recusa(f"o serviço {nome} compartilha {k} com o servidor")
    if s.get("cgroup_parent") or s.get("volumes_from"):
        raise Recusa(f"o serviço {nome} usa cgroup_parent ou volumes_from")
    caps = {str(c).upper().removeprefix("CAP_") for c in (s.get("cap_add") or [])}
    ruins = sorted(caps & CAPS_PROIBIDAS)
    if ruins:
        raise Recusa(f"o serviço {nome} pede poderes de administrador do Linux ({', '.join(ruins)})")
    for d in s.get("devices") or []:
        origem = (d.get("source") if isinstance(d, dict) else str(d).split(":")[0]) or ""
        if not str(origem).startswith("/dev/dri"):
            raise Recusa(f"o serviço {nome} usa o aparelho {origem} do servidor (só a placa de vídeo é permitida)")
    for o in s.get("security_opt") or []:
        if "unconfined" in str(o) or "disable" in str(o):
            raise Recusa(f"o serviço {nome} desliga uma proteção do Docker ({o})")
    if s.get("runtime") not in (None, "nvidia"):
        raise Recusa(f"o serviço {nome} usa o runtime {s.get('runtime')}")


def portas(s):
    """Lista (publicada, interna, protocolo, entrada original) das portas do serviço."""
    out = []
    for p in s.get("ports") or []:
        if isinstance(p, dict):
            pub, alvo, proto = p.get("published"), p.get("target"), p.get("protocol") or "tcp"
        else:
            txt = str(p)
            proto = "tcp"
            if "/" in txt:
                txt, proto = txt.rsplit("/", 1)
            pedacos = txt.split(":")
            if len(pedacos) == 1:
                pub, alvo = None, pedacos[0]
            else:
                pub, alvo = pedacos[-2], pedacos[-1]
        try:
            alvo = int(str(alvo).split("-")[0])
        except ValueError:
            continue
        try:
            pub = int(str(pub)) if pub not in (None, "") else None
        except ValueError:
            pub = None
        out.append((pub, alvo, proto, p))
    return out


def imagem_e_versao(imagem):
    img = str(imagem or "").strip()
    if not img or " " in img:
        raise Recusa("o serviço principal não tem imagem")
    if "@" in img:
        img = img.split("@", 1)[0]
    ultimo = img.rsplit("/", 1)[-1]
    if ":" not in ultimo:
        img += ":latest"
    tag = img.rsplit(":", 1)[1]
    if "$" in tag:
        raise Recusa("a versão da imagem depende de uma variável")
    return img, tag


# ── conversão de um app ──────────────────────────────────────────────────────────────────────────

def converte_app(pasta, compose, origem, oficiais, usados_ids):
    """Devolve (id, config, compose_runtipi, descricao_md, info) ou levanta Recusa."""
    x = compose.get("x-casaos") or {}
    servicos = compose.get("services") or {}
    if not isinstance(servicos, dict) or not servicos:
        raise Recusa("não tem serviços")
    principal = x.get("main") if x.get("main") in servicos else next(iter(servicos))
    prefixo = origem.get("tira_prefixo") or ""
    nome_compose = str(compose.get("name") or os.path.basename(pasta))
    if prefixo and nome_compose.lower().startswith(prefixo):
        nome_compose = nome_compose[len(prefixo):]
    nome_app = texto(x.get("title")) or nome_compose
    if prefixo and nome_app.lower().startswith(prefixo):
        nome_app = nome_app[len(prefixo):]

    # id: o nome do compose; com vários serviços, o do serviço principal (renomear quebraria os outros)
    base_id = limpa_id(principal) if len(servicos) > 1 else limpa_id(nome_compose)
    app_id = base_id
    if not ID_RE.match(app_id or ""):
        raise Recusa("nome do app inválido")
    sem_parenteses = re.sub(r"\([^)]*\)", "", nome_app)  # "Sonarr (LinuxServer.io)" → "Sonarr"
    if normaliza(app_id) in oficiais["ids"] or normaliza(sem_parenteses) in oficiais["nomes"]:
        raise Recusa("já existe na loja oficial do Runtipi", "duplicado")
    if app_id in usados_ids:
        raise Recusa("outro app desta loja já usa o mesmo nome")

    for n, s in servicos.items():
        if not isinstance(s, dict):
            raise Recusa(f"o serviço {n} não foi entendido")
        confere_servico(n, s)
    if compose.get("volumes") and any(isinstance(v, dict) and v.get("driver_opts") for v in compose["volumes"].values() if v):
        raise Recusa("usa volumes com driver_opts (pastas montadas de outro jeito)")

    desconhecidas = set()
    novos = {}
    porta_ui = None
    porta_interna = None
    versao = None
    mapa_porta = str(x.get("port_map") or "").strip()
    # o serviço da página web: o que publica a porta do port_map (às vezes é um nginx na frente do principal)
    web = None
    if mapa_porta:
        web = next((n for n, s in servicos.items() if any(str(p[0]) == mapa_porta for p in portas(s))), None)
    if web is None and portas(servicos[principal]):
        web = principal
    if web is None:
        web = next((n for n, s in servicos.items() if portas(s)), None)
    if web is None:
        raise Recusa("não tem página web (porta) para abrir")
    # segredo fixo na receita (todo mundo teria a mesma chave): vira um valor aleatório por instalação
    trocas = {v: "${GARIMPO_SEGREDO_%d}" % (i + 1) for i, v in enumerate(segredos_fixos(servicos))}
    for n, s in servicos.items():
        s = copy.deepcopy(s)
        novo_nome = app_id if n == principal else n
        rede = str(s.get("network_mode") or "")
        for k in CHAVES_TIRADAS:
            s.pop(k, None)
        if rede.startswith("service:"):
            alvo = rede.split(":", 1)[1]
            s["network_mode"] = "service:" + (app_id if alvo == principal else alvo)
        if "labels" in s and isinstance(s["labels"], dict):
            s["labels"] = {k: v for k, v in s["labels"].items() if not str(k).startswith(("casaos", "icon"))} or None
            if s["labels"] is None:
                s.pop("labels")
        if "volumes" in s:
            s["volumes"] = converte_volumes(s["volumes"], n)
        if "depends_on" in s:
            d = s["depends_on"]
            if isinstance(d, list):
                s["depends_on"] = [app_id if i == principal else i for i in d]
            elif isinstance(d, dict):
                s["depends_on"] = {(app_id if k == principal else k): v for k, v in d.items()}
        s = troca_texto(troca_vars(s, app_id, desconhecidas), trocas)
        if n == principal:
            s["image"], versao = imagem_e_versao(s.get("image"))
        if n == web:
            lista = portas(s)
            escolhida = next((p for p in lista if mapa_porta and str(p[0]) == mapa_porta), None) or lista[0]
            porta_ui = escolhida[0] or escolhida[1]
            porta_interna = escolhida[1]
            resto = [p[3] for p in lista if p is not escolhida]
            if resto:
                s["ports"] = resto
            else:
                s.pop("ports", None)
            s["x-runtipi"] = {"is_main": True, "internal_port": porta_interna}
        novos[novo_nome] = s
    # deixa o serviço principal primeiro (mais fácil de ler)
    ordem = {app_id: novos.pop(app_id)}
    ordem.update(novos)
    saida = {"services": ordem, "x-runtipi": {"schema_version": 2}}
    for k in ("volumes", "configs", "secrets"):
        if k == "volumes":
            continue  # volumes com nome viraram pastas do app
        if compose.get(k):
            saida[k] = troca_texto(troca_vars(compose[k], app_id, desconhecidas), trocas)

    archs = sorted({ARQUITETURAS[a] for a in (x.get("architectures") or ["amd64"]) if a in ARQUITETURAS})
    if not archs:
        raise Recusa("não roda em amd64 nem arm64")
    cats = []
    for c in [x.get("category")] if isinstance(x.get("category"), str) else (x.get("category") or []):
        m = CATEGORIAS.get(str(c).strip().lower())
        if m and m not in cats:
            cats.append(m)
    if not cats:
        cats = ["utilities"]

    tagline = texto(x.get("tagline")) or nome_app
    descricao = texto(x.get("description")) or tagline
    fonte = next((u for u in (x.get("repo"), x.get("project_url"), x.get("website")) if url_ok(u)), origem["fonte"])
    site = next((u for u in (x.get("website"), x.get("project_url")) if url_ok(u)), None)
    campos = [{"type": "text", "label": f"{v} (pedido pela receita original)", "env_variable": v, "required": False}
              for v in sorted(desconhecidas)]
    campos += [{"type": "random", "label": f"Chave secreta {i + 1} (gerada na instalação)", "env_variable": f"GARIMPO_SEGREDO_{i + 1}",
                "min": 32} for i in range(len(trocas))]
    if SEGREDO_RE.search(json.dumps(saida)):
        raise Recusa("a receita traz uma chave secreta escrita nela")
    config = {
        "$schema": "https://schemas.runtipi.io/app-info.json",
        "name": nome_app[:60],
        "id": app_id,
        "available": True,
        "port": porta_ui,
        "exposable": True,
        "dynamic_config": True,
        "tipi_version": 1,
        "version": versao,
        "categories": cats,
        "description": tagline[:300],
        "short_desc": tagline[:150],
        "author": (texto(x.get("developer")) or texto(x.get("author")) or "Desconhecido")[:80],
        "source": fonte,
        "form_fields": campos,
        "supported_architectures": archs,
        "min_tipi_version": VERSAO_MINIMA_RUNTIPI,
    }
    if site:
        config["website"] = site
    indice = str(x.get("index") or "/").strip()
    if indice not in ("", "/") and re.match(r"^/[A-Za-z0-9._~/?=&%-]*$", indice):
        config["url_suffix"] = indice
    if str(x.get("scheme") or "").lower() == "https":
        config["https"] = True

    dicas = texto((x.get("tips") or {}).get("before_install")) if isinstance(x.get("tips"), dict) else ""
    md = [f"# {nome_app}", "", descricao, ""]
    if dicas:
        md += ["## Antes de instalar", "", dicas, ""]
    campos_texto = [c for c in campos if c["type"] == "text"]
    if campos_texto:
        md += ["## Perguntas da instalação", "",
               "A receita original usa estas variáveis; preencha na instalação se o app precisar: "
               + ", ".join(f"`{c['env_variable']}`" for c in campos_texto) + ".", ""]
    if trocas:
        md += ["A receita original trazia uma chave secreta fixa (igual para todo mundo); aqui o Runtipi gera uma "
               "nova em cada instalação.", ""]
    md += ["---", "", f"Convertido automaticamente da loja {origem['nome']} ({origem['fonte']}, licença {origem['licenca']}) "
           "pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e "
           "downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.", ""]
    md = "\n".join(md)
    if SEGREDO_RE.search(md):
        raise Recusa("a descrição traz uma chave secreta escrita nela")
    return app_id, config, saida, md, {"icone": x.get("icon"), "porta": porta_ui}


# ── logos ────────────────────────────────────────────────────────────────────────────────────────

def baixa(url):
    if not (isinstance(url, str) and url.startswith("https://")):
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "garimpo-conversor"})
        with urllib.request.urlopen(req, timeout=20) as r:
            dados = r.read(MAX_LOGO + 1)
        return dados if len(dados) <= MAX_LOGO else None
    except Exception:
        return None


def prepara_logo(pasta_app, url, destino, padrao):
    """Grava metadata/logo.jpg (JPEG 256×256 quando o Pillow existe; senão copia o arquivo como veio)."""
    dados = None
    for nome in ("icon.png", "icon.jpg", "icon.jpeg", "icon.webp", "icon.svg"):
        p = os.path.join(pasta_app, nome)
        if os.path.isfile(p) and not os.path.islink(p) and os.path.getsize(p) <= MAX_LOGO:
            dados = le_bytes(p)
            break
    if dados is None:
        dados = baixa(url)
    if dados and (dados.lstrip()[:5] == b"<?xml" or b"<svg" in dados[:400]):
        dados = svg_para_png(dados)
    if dados:
        jpg = para_jpeg(dados)
        if jpg:
            grava(destino, jpg)
            return True
        if dados[:3] == b"\xff\xd8\xff" or dados[:8] == b"\x89PNG\r\n\x1a\n":
            grava(destino, dados)
            return True
    shutil.copyfile(padrao, destino)
    return False


def svg_para_png(dados):
    if not shutil.which("rsvg-convert"):
        return None
    try:
        r = subprocess.run(["rsvg-convert", "-w", "256", "-h", "256", "-a", "-f", "png"], input=dados,
                           capture_output=True, timeout=30, check=True)
        return r.stdout
    except Exception:
        return None


def para_jpeg(dados):
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        img = Image.open(io.BytesIO(dados))
        img.load()
        img = img.convert("RGBA")
        img.thumbnail((256, 256))
        fundo = Image.new("RGB", (256, 256), (255, 255, 255))
        fundo.paste(img, ((256 - img.width) // 2, (256 - img.height) // 2), img)
        out = io.BytesIO()
        fundo.save(out, "JPEG", quality=88)
        return out.getvalue()
    except Exception:
        return None


# ── loja inteira ─────────────────────────────────────────────────────────────────────────────────

def le_oficiais(pasta):
    ids, nomes = set(), set()
    apps = os.path.join(pasta, "apps")
    for d in sorted(os.listdir(apps)) if os.path.isdir(apps) else []:
        cfg = os.path.join(apps, d, "config.json")
        if not os.path.isfile(cfg):
            continue
        ids.add(normaliza(d))
        try:
            c = json.loads(le(cfg))
            ids.add(normaliza(c.get("id")))
            nomes.add(normaliza(c.get("name")))
        except Exception:
            pass
    ids.discard("")
    nomes.discard("")
    return {"ids": ids, "nomes": nomes}


def le_anteriores(saida):
    """config.json e um resumo de cada app já publicado (para manter tipi_version e datas)."""
    ant = {}
    apps = os.path.join(saida, "apps")
    for d in os.listdir(apps) if os.path.isdir(apps) else []:
        try:
            c = json.loads(le(os.path.join(apps, d, "config.json")))
            comp = le(os.path.join(apps, d, "docker-compose.yml"))
            ant[d] = (c, comp)
        except Exception:
            pass
    return ant


def resumo(config, compose_txt, md):
    c = {k: v for k, v in config.items() if k not in ("tipi_version", "created_at", "updated_at")}
    return hashlib.sha256((json.dumps(c, sort_keys=True) + compose_txt + md).encode()).hexdigest()


class Dumper(yaml.SafeDumper):
    pass


def _str(dumper, s):
    estilo = "|" if "\n" in s else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", s, style=estilo)


Dumper.add_representer(str, _str)


def porta_livre(p, usadas):
    p = p if isinstance(p, int) and 1024 <= p <= 65535 else 20000
    while p in usadas:
        p = p + 1 if p < 65535 else 20000
    usadas.add(p)
    return p


def converte_loja(origem, fonte, oficial, saida, padrao, agora_ms=None):
    agora_ms = agora_ms or int(time.time() * 1000) - 60_000  # um minuto antes: a loja recusa datas no futuro
    oficiais = le_oficiais(oficial)
    anteriores = le_anteriores(saida)
    pastas = sorted(d for d in os.listdir(os.path.join(fonte, "Apps")) if os.path.isdir(os.path.join(fonte, "Apps", d)))
    apps_dir = os.path.join(saida, "apps")
    if os.path.isdir(apps_dir):
        shutil.rmtree(apps_dir)
    os.makedirs(apps_dir)
    ok, recusados, duplicados = [], [], []
    usados_ids, usadas = set(), set()
    convertidos = []
    for d in pastas:
        pasta = os.path.join(fonte, "Apps", d)
        arq = os.path.join(pasta, "docker-compose.yml")
        if not os.path.isfile(arq) or os.path.islink(arq):
            continue
        try:
            compose = yaml.safe_load(le(arq))
            if not isinstance(compose, dict):
                raise Recusa("docker-compose.yml inválido")
            app_id, config, comp, md, info = converte_app(pasta, compose, origem, oficiais, usados_ids)
        except Recusa as e:
            (duplicados if len(e.args) > 1 and e.args[1] == "duplicado" else recusados).append((d, e.args[0]))
            continue
        except yaml.YAMLError:
            recusados.append((d, "docker-compose.yml com erro"))
            continue
        usados_ids.add(app_id)
        convertidos.append((d, pasta, app_id, config, comp, md, info))
    # portas: a de cada app tem que ser única na loja; quem já estava publicado guarda a sua
    for _, _, app_id, config, *_ in convertidos:
        p = anteriores.get(app_id, ({}, ""))[0].get("port")
        if isinstance(p, int) and p not in usadas:
            config["port"] = p
            usadas.add(p)
            config["_porta_ok"] = True
    for _, _, app_id, config, *_ in convertidos:
        if not config.pop("_porta_ok", False):
            config["port"] = porta_livre(config["port"], usadas)
    sem_logo = []
    for d, pasta, app_id, config, comp, md, info in convertidos:
        txt = yaml.dump(comp, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=200)
        ant = anteriores.get(app_id)
        if ant:
            c0 = ant[0]
            config["created_at"] = int(c0.get("created_at") or agora_ms)
            md_ant = ""
            try:
                md_ant = le(os.path.join(saida, ".resumos", app_id)).strip()
            except OSError:
                pass
            mudou = md_ant != resumo(config, txt, md)
            config["tipi_version"] = int(c0.get("tipi_version") or 0) + (1 if mudou else 0) or 1
            config["updated_at"] = agora_ms if mudou else int(c0.get("updated_at") or agora_ms)
        else:
            config["created_at"] = config["updated_at"] = agora_ms
        dest = os.path.join(apps_dir, app_id)
        os.makedirs(os.path.join(dest, "metadata"))
        with open(os.path.join(dest, "config.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            f.write("\n")
        with open(os.path.join(dest, "docker-compose.yml"), "w", encoding="utf-8") as f:
            f.write(f"# Convertido pelo Garimpo do BrunOS a partir de {origem['fonte']} (Apps/{d}).\n")
            f.write(txt)
        with open(os.path.join(dest, "metadata", "description.md"), "w", encoding="utf-8") as f:
            f.write(md)
        if not prepara_logo(pasta, info["icone"], os.path.join(dest, "metadata", "logo.jpg"), padrao):
            sem_logo.append(app_id)
        os.makedirs(os.path.join(saida, ".resumos"), exist_ok=True)
        with open(os.path.join(saida, ".resumos", app_id), "w", encoding="utf-8") as f:
            f.write(resumo(config, txt, md) + "\n")
        ok.append((app_id, config["name"], d))
    # resumos de apps que saíram
    rdir = os.path.join(saida, ".resumos")
    for r in os.listdir(rdir) if os.path.isdir(rdir) else []:
        if r not in usados_ids:
            os.remove(os.path.join(rdir, r))
    escreve_extras(origem, fonte, saida, ok, recusados, duplicados, agora_ms)
    return ok, recusados, duplicados, sem_logo


def escreve_extras(origem, fonte, saida, ok, recusados, duplicados, agora_ms):
    info = {
        "brunos": 1,
        "nome": origem["nome"],
        "selo": origem["selo"],
        "origem": origem["nome"],
        "fonte": origem["fonte"],
        "licenca": origem["licenca"],
        "sobre": origem["sobre"],
        "garimpo": "https://github.com/BrunnoFe/Garimpo",
        "apps": len(ok),
        "recusados": len(recusados),
        "repetidos": len(duplicados),
    }
    with open(os.path.join(saida, "garimpo.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
        f.write("\n")
    lic = os.path.join(fonte, "LICENSE")
    if os.path.isfile(lic) and not os.path.islink(lic):
        shutil.copyfile(lic, os.path.join(saida, "LICENSE-ORIGEM"))
    linhas = [
        f"# {origem['nome']} (convertida pelo Garimpo do BrunOS)", "",
        origem["sobre"], "",
        f"Esta loja do Runtipi é gerada automaticamente todo dia a partir de <{origem['fonte']}> "
        f"(licença {origem['licenca']}, cópia em `LICENSE-ORIGEM`). Não é a loja oficial do {origem['nome']} "
        "nem tem ligação com os autores dela. Os nomes e logos dos apps são dos seus autores.", "",
        "Para usar no Runtipi: *Lojas de apps → Adicionar*, nome `" + origem["slug"] + "`, endereço "
        f"`https://github.com/BrunnoFe/Garimpo/tree/{origem['slug']}`. No BrunOS: janela Loja → Lojas.", "",
        f"## Apps ({len(ok)})", "",
    ]
    linhas += [f"- {nome} (`{i}`)" for i, nome, _ in sorted(ok, key=lambda t: t[1].lower())]
    linhas += ["", f"## Recusados por segurança ou formato ({len(recusados)})", "",
               "Receitas que dariam poder demais sobre o servidor ou que não deu para converter:", ""]
    linhas += [f"- {d}: {m}" for d, m in recusados]
    linhas += ["", f"## Já existem na loja oficial do Runtipi ({len(duplicados)})", "",
               "Ficaram de fora para não aparecer duas vezes: " + ", ".join(d for d, _ in duplicados) + ".", ""]
    with open(os.path.join(saida, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Converte uma loja do CasaOS para o formato do Runtipi.")
    ap.add_argument("--origem", required=True)
    ap.add_argument("--fonte", required=True)
    ap.add_argument("--oficial", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--origens", default=os.path.join(os.path.dirname(__file__), "..", "origens.json"))
    a = ap.parse_args(argv)
    origens = {o["slug"]: o for o in json.loads(le(a.origens))}
    if a.origem not in origens:
        sys.exit(f"origem desconhecida: {a.origem}")
    os.makedirs(a.saida, exist_ok=True)
    padrao = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-padrao.jpg")
    ok, recusados, duplicados, sem_logo = converte_loja(origens[a.origem], a.fonte, a.oficial, a.saida, padrao)
    print(f"{origens[a.origem]['nome']}: {len(ok)} convertidos, {len(recusados)} recusados, "
          f"{len(duplicados)} já na loja oficial, {len(sem_logo)} com o logo padrão")
    for d, m in recusados:
        print(f"  recusado {d}: {m}")


if __name__ == "__main__":
    main()
