"""Testes do conversor (só a biblioteca padrão + PyYAML): python3 -m unittest discover -s tests"""
import json
import os
import shutil
import sys
import tempfile
import textwrap
import unittest

import yaml

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "garimpo"))
import converter as c  # noqa: E402
import confere  # noqa: E402

ORIGEM = {"slug": "teste", "nome": "Teste", "selo": "via Teste", "fonte": "https://example.com/loja",
          "licenca": "Apache-2.0", "sobre": "Loja de teste."}
OFICIAIS = {"ids": {"jellyfin"}, "nomes": {"nextcloud"}}


def receita(txt):
    return yaml.safe_load(textwrap.dedent(txt))


SIMPLES = """
name: meuapp
services:
  meuapp:
    image: exemplo/meuapp:1.2.3
    restart: unless-stopped
    container_name: meuapp
    network_mode: bridge
    environment:
      PUID: $PUID
      TZ: $TZ
      CHAVE: ${CHAVE_API}
      ESCAPADO: $$NAO_MEXE
    ports:
      - target: 8080
        published: "8123"
        protocol: tcp
      - "9000:9000/udp"
    volumes:
      - type: bind
        source: /DATA/AppData/$AppID/config
        target: /config
      - /DATA/Media/Movies:/filmes:ro
      - /DATA/Downloads:/downloads
      - /etc/localtime:/etc/localtime
      - dados:/dados
x-casaos:
  main: meuapp
  port_map: "8123"
  index: /admin
  architectures: [amd64, arm64, arm]
  category: Media
  title: {en_US: My App, pt_BR: Meu App}
  tagline: {en_US: An app}
  description: {en_US: A long description.}
  developer: Fulano
  repo: https://github.com/fulano/meuapp
"""


class TesteConversao(unittest.TestCase):
    def converte(self, txt, usados=None):
        return c.converte_app("/x/MeuApp", receita(txt), ORIGEM, OFICIAIS, usados or set())

    def test_app_simples(self):
        app_id, cfg, comp, md, info = self.converte(SIMPLES)
        self.assertEqual(app_id, "meuapp")
        self.assertEqual(cfg["name"], "Meu App")  # português quando existe
        self.assertEqual(cfg["short_desc"], "An app")  # senão inglês
        self.assertEqual(cfg["port"], 8123)
        self.assertEqual(cfg["version"], "1.2.3")
        self.assertEqual(cfg["supported_architectures"], ["amd64", "arm64"])
        self.assertEqual(cfg["categories"], ["media"])
        self.assertEqual(cfg["url_suffix"], "/admin")
        self.assertEqual([f["env_variable"] for f in cfg["form_fields"]], ["CHAVE_API"])
        s = comp["services"]["meuapp"]
        self.assertEqual(s["x-runtipi"], {"is_main": True, "internal_port": 8080})
        for k in ("restart", "container_name", "network_mode"):
            self.assertNotIn(k, s)
        self.assertEqual(s["ports"], ["9000:9000/udp"])  # a porta da página web sai (o Runtipi cuida)
        self.assertEqual(s["environment"], {"PUID": "1000", "TZ": "${TZ}", "CHAVE": "${CHAVE_API}", "ESCAPADO": "$$NAO_MEXE"})
        self.assertEqual(s["volumes"], [
            "${APP_DATA_DIR}/data/config:/config",
            "${ROOT_FOLDER_HOST}/media/data/movies:/filmes:ro",
            "${ROOT_FOLDER_HOST}/media/downloads:/downloads",
            "/etc/localtime:/etc/localtime:ro",
            "${APP_DATA_DIR}/data/volumes/dados:/dados",
        ])
        self.assertEqual(comp["x-runtipi"], {"schema_version": 2})
        self.assertIn("Convertido automaticamente da loja Teste", md)

    def test_privilegios_entram_com_a_lista(self):
        # decisão 62 do BrunOS: o app entra na loja, com o que pede listado (e a receita intacta)
        casos = {
            "privileged: true": "privileged",
            "network_mode: host": "network_mode: host",
            "pid: host": "pid: host",
            "cap_add: [NET_ADMIN, CHOWN]": "(NET_ADMIN)",
            "devices: [/dev/kvm:/dev/kvm]": "/dev/kvm",
            "security_opt: [apparmor:unconfined]": "proteção",
            "volumes: [/var/run/docker.sock:/var/run/docker.sock]": "socket do Docker",
            "volumes: [/etc:/host-etc]": "pasta /etc",
            "volumes: [/:/raiz]": "pasta / ",
        }
        for extra, motivo in casos.items():
            txt = f"""
name: forte
services:
  forte:
    image: x/forte:1
    ports: ["8080:80"]
    {extra}
x-casaos: {{main: forte, port_map: "8080"}}
"""
            with self.subTest(extra=extra):
                _, _, comp, md, info = self.converte(txt)
                self.assertTrue(any(motivo.strip() in p + " " for p in info["privilegios"]), info["privilegios"])
                self.assertIn("## Requer privilégios", md)
        _, _, comp, _, info = self.converte(SIMPLES.replace("network_mode: bridge", "network_mode: host"))
        self.assertEqual(comp["services"]["meuapp"]["network_mode"], "host")
        # pasta pessoal e hora certa não são privilégio
        _, _, _, md, info = self.converte(SIMPLES.replace("/DATA/Downloads:/downloads", "/home/fulano:/x"))
        self.assertEqual(info["privilegios"], [])
        self.assertNotIn("Requer privilégios", md)

    def test_recusa_o_que_nao_funciona(self):
        casos = {
            "network_mode: container:outro": "rede de outro container",
            "volumes_from: [outro]": "volumes_from",
            "runtime: kata": "runtime",
            "volumes: [$PASTA_X:/x]": "variável desconhecida",
            "volumes: [/DATA/../etc:/x]": "'..'",
        }
        for extra, motivo in casos.items():
            txt = f"""
name: ruim
services:
  ruim:
    image: x/ruim:1
    ports: ["8080:80"]
    {extra}
x-casaos: {{main: ruim, port_map: "8080"}}
"""
            with self.subTest(extra=extra):
                with self.assertRaises(c.Recusa) as e:
                    self.converte(txt)
                self.assertIn(motivo, e.exception.args[0])

    def test_perguntas_da_instalacao(self):
        txt = """
name: painel
services:
  painel:
    image: x/painel:1
    ports: ["8080:80"]
    environment:
      ADMIN_USER: admin
      ADMIN_PASSWORD: casaos
      DB_PASSWORD: interna
      SITE_NAME: Meu Painel
      TZ: $TZ
  worker:
    image: x/painel:1
    environment: ["ADMIN_PASSWORD=casaos", "DB_PASSWORD=interna"]
x-casaos:
  main: painel
  port_map: "8080"
  envs:
    - container: SITE_NAME
      description: {en_US: Name shown on the page}
    - container: TZ
      description: {en_US: Time zone}
"""
        _, cfg, comp, md, _ = self.converte(txt)
        campos = {f["env_variable"]: f for f in cfg["form_fields"]}
        self.assertEqual(campos["ADMIN_PASSWORD"]["type"], "password")
        self.assertTrue(campos["ADMIN_PASSWORD"]["required"])
        self.assertNotIn("default", campos["ADMIN_PASSWORD"])  # a senha fixa nunca vai como sugestão
        self.assertEqual((campos["ADMIN_USER"]["type"], campos["ADMIN_USER"]["default"]), ("text", "admin"))
        self.assertEqual((campos["SITE_NAME"]["default"], campos["SITE_NAME"]["hint"]), ("Meu Painel", "Name shown on the page"))
        self.assertNotIn("DB_PASSWORD", campos)  # senha de banco: só os serviços do app usam
        self.assertNotIn("TZ", campos)
        env = comp["services"]["painel"]["environment"]
        self.assertEqual((env["ADMIN_PASSWORD"], env["ADMIN_USER"], env["SITE_NAME"], env["DB_PASSWORD"]),
                         ("${ADMIN_PASSWORD}", "${ADMIN_USER}", "${SITE_NAME}", "interna"))
        self.assertEqual(comp["services"]["worker"]["environment"], ["ADMIN_PASSWORD=${ADMIN_PASSWORD}", "DB_PASSWORD=interna"])
        self.assertIn("senha fixa", md)
        # exceções app a app: tirar uma pergunta e forçar outra
        exc = {"painel": {"nao_perguntar": ["SITE_NAME", "ADMIN_PASSWORD"], "perguntar": ["DB_PASSWORD"]}}
        _, cfg, comp, _, _ = c.converte_app("/x/Painel", receita(txt), ORIGEM, OFICIAIS, set(), exc)
        nomes = [f["env_variable"] for f in cfg["form_fields"]]
        self.assertIn("DB_PASSWORD", nomes)
        self.assertNotIn("SITE_NAME", nomes)
        self.assertNotIn("ADMIN_PASSWORD", nomes)
        self.assertEqual(comp["services"]["painel"]["environment"]["ADMIN_PASSWORD"], "casaos")

    def test_segredo_fixo_vira_aleatorio(self):
        chave = "sk-" + "A1b2C3d4" * 6  # valor falso no formato de chave da OpenAI
        txt = f"""
name: pilha
services:
  pilha:
    image: x/pilha:1
    ports: ["8080:80"]
    environment:
      SECRET_KEY: {chave}
      DB_PASSWORD: curta
  worker:
    image: x/pilha:1
    environment: ["SECRET_KEY={chave}", "URL=http://x?k={chave}"]
x-casaos: {{main: pilha, port_map: "8080"}}
"""
        _, cfg, comp, md, _ = self.converte(txt)
        self.assertEqual(comp["services"]["pilha"]["environment"]["SECRET_KEY"], "${GARIMPO_SEGREDO_1}")
        self.assertEqual(comp["services"]["pilha"]["environment"]["DB_PASSWORD"], "curta")  # curta: senha interna, fica
        self.assertEqual(comp["services"]["worker"]["environment"], ["SECRET_KEY=${GARIMPO_SEGREDO_1}", "URL=http://x?k=${GARIMPO_SEGREDO_1}"])
        self.assertEqual([(f["type"], f["env_variable"]) for f in cfg["form_fields"]], [("random", "GARIMPO_SEGREDO_1")])
        self.assertNotIn("required", cfg["form_fields"][0])  # random nunca obrigatório (teste da loja oficial)
        self.assertIn("chave secreta fixa", md)

    def test_chave_escrita_fora_de_variavel_de_segredo_recusa(self):
        txt = SIMPLES.replace("CHAVE: ${CHAVE_API}", "CONFIG: sk-" + "Z9y8X7w6" * 6)
        with self.assertRaises(c.Recusa) as e:
            self.converte(txt)
        self.assertIn("chave secreta", e.exception.args[0])

    def test_placa_de_video_pode(self):
        txt = SIMPLES.replace("    restart: unless-stopped", "    devices: [/dev/dri:/dev/dri]")
        _, _, comp, _, _ = self.converte(txt)
        self.assertEqual(comp["services"]["meuapp"]["devices"], ["/dev/dri:/dev/dri"])

    def test_repetido_da_loja_oficial(self):
        with self.assertRaises(c.Recusa) as e:
            self.converte(SIMPLES.replace("name: meuapp", "name: jellyfin"))
        self.assertEqual(e.exception.args[1], "duplicado")
        with self.assertRaises(c.Recusa):
            self.converte(SIMPLES.replace("pt_BR: Meu App", "pt_BR: Nextcloud (LinuxServer.io)"))

    def test_varios_servicos_com_nginx_na_frente(self):
        txt = """
name: pilha
services:
  web:
    image: x/web:2.0
    depends_on: [db]
  db:
    image: postgres:16
    volumes: [/DATA/AppData/pilha/db:/var/lib/postgresql/data]
  nginx:
    image: nginx:1
    ports: ["3701:80"]
    depends_on: [web]
x-casaos: {main: web, port_map: "3701", title: {en_US: Pilha}}
"""
        app_id, cfg, comp, _, _ = self.converte(txt)
        self.assertEqual(app_id, "web")  # serviço principal não é renomeado (os outros dependem do nome)
        self.assertEqual(list(comp["services"])[0], "web")
        self.assertEqual(cfg["version"], "2.0")
        self.assertEqual(comp["services"]["nginx"]["x-runtipi"], {"is_main": True, "internal_port": 80})
        self.assertNotIn("x-runtipi", comp["services"]["web"])
        self.assertEqual(comp["services"]["db"]["volumes"], ["${APP_DATA_DIR}/data/db:/var/lib/postgresql/data"])

    def test_navegador_ganha_memoria_compartilhada(self):
        txt = SIMPLES.replace("image: exemplo/meuapp:1.2.3", "image: lscr.io/linuxserver/brave:1.99")
        _, _, comp, _, _ = self.converte(txt)
        self.assertEqual(comp["services"]["meuapp"]["shm_size"], "1gb")
        _, _, comp, _, _ = self.converte(SIMPLES)
        self.assertNotIn("shm_size", comp["services"]["meuapp"])

    def test_imagem_sem_tag(self):
        self.assertEqual(c.imagem_e_versao("nginx"), ("nginx:latest", "latest"))
        self.assertEqual(c.imagem_e_versao("ghcr.io:443/a/b@sha256:abc"), ("ghcr.io:443/a/b:latest", "latest"))
        self.assertEqual(c.imagem_e_versao("ghcr.io/a/b:1.0@sha256:abc"), ("ghcr.io/a/b:1.0", "1.0"))


class TesteLoja(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.fonte = os.path.join(self.tmp, "fonte")
        self.oficial = os.path.join(self.tmp, "oficial")
        self.saida = os.path.join(self.tmp, "saida")
        os.makedirs(os.path.join(self.oficial, "apps"))
        for nome, txt in {"MeuApp": SIMPLES, "Outro": SIMPLES.replace("meuapp", "outro"),
                          "Ruim": SIMPLES.replace("meuapp", "ruim").replace("restart: unless-stopped", "privileged: true")}.items():
            os.makedirs(os.path.join(self.fonte, "Apps", nome))
            with open(os.path.join(self.fonte, "Apps", nome, "docker-compose.yml"), "w", encoding="utf-8") as f:
                f.write(textwrap.dedent(txt))
        with open(os.path.join(self.fonte, "LICENSE"), "w") as f:
            f.write("licença")
        self.padrao = os.path.join(RAIZ, "garimpo", "logo-padrao.jpg")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def cfg(self, app):
        return json.loads(c.le(os.path.join(self.saida, "apps", app, "config.json")))

    def test_loja_inteira_e_versoes(self):
        ok, recusados, dup, _ = c.converte_loja(ORIGEM, self.fonte, self.oficial, self.saida, self.padrao, agora_ms=1_800_000_000_000, excecoes={})
        self.assertEqual(sorted(i for i, _, _ in ok), ["meuapp", "outro", "ruim"])
        self.assertEqual(recusados, [])
        # portas únicas na loja (as três receitas pedem 8123)
        self.assertEqual({self.cfg("meuapp")["port"], self.cfg("outro")["port"], self.cfg("ruim")["port"]}, {8123, 8124, 8125})
        self.assertTrue(os.path.isfile(os.path.join(self.saida, "apps", "meuapp", "metadata", "logo.jpg")))
        g = json.loads(c.le(os.path.join(self.saida, "garimpo.json")))
        self.assertEqual((g["nome"], g["selo"], g["apps"], g["privilegios"], g["recusados"]), ("Teste", "via Teste", 3, 1, 0))
        self.assertEqual(json.loads(c.le(os.path.join(self.saida, "privilegios.json"))), {"ruim": ["Controle total do servidor (privileged)"]})
        readme = c.le(os.path.join(self.saida, "README.md"))
        self.assertIn("## Requerem privilégios (1)", readme)
        self.assertIn("- `ruim`: Controle total do servidor (privileged)", readme)
        self.assertEqual(confere.confere_loja(self.saida), [])
        # rodar de novo sem mudança: mesma versão e mesma data; com mudança: tipi_version sobe
        c.converte_loja(ORIGEM, self.fonte, self.oficial, self.saida, self.padrao, agora_ms=1_800_000_100_000)
        self.assertEqual((self.cfg("meuapp")["tipi_version"], self.cfg("meuapp")["updated_at"]), (1, 1_800_000_000_000))
        p = os.path.join(self.fonte, "Apps", "MeuApp", "docker-compose.yml")
        txt = c.le(p)
        with open(p, "w", encoding="utf-8") as f:
            f.write(txt.replace("1.2.3", "1.2.4"))
        c.converte_loja(ORIGEM, self.fonte, self.oficial, self.saida, self.padrao, agora_ms=1_800_000_200_000)
        m = self.cfg("meuapp")
        self.assertEqual((m["tipi_version"], m["version"], m["updated_at"], m["created_at"]), (2, "1.2.4", 1_800_000_200_000, 1_800_000_000_000))
        self.assertEqual(self.cfg("meuapp")["port"], 8123)  # a porta de quem já estava publicado não muda
        self.assertEqual(self.cfg("outro")["tipi_version"], 1)

    def test_confere_pega_o_que_escapou(self):
        c.converte_loja(ORIGEM, self.fonte, self.oficial, self.saida, self.padrao, agora_ms=1_800_000_000_000)
        p = os.path.join(self.saida, "apps", "meuapp", "docker-compose.yml")
        comp = yaml.safe_load(c.le(p))
        comp["services"]["meuapp"]["volumes"].append("/etc:/etc")
        comp["services"]["meuapp"]["privileged"] = True
        with open(p, "w", encoding="utf-8") as f:
            yaml.safe_dump(comp, f)
        erros = confere.confere_loja(self.saida)
        # privilégio que não está no privilegios.json: é exatamente o que a conferência existe para pegar
        self.assertTrue(any("meuapp: privilégios não batem" in e and "privileged" in e and "/etc" in e for e in erros), erros)
        # e o contrário: um app listado que não pede nada também é erro
        with open(os.path.join(self.saida, "privilegios.json"), "w", encoding="utf-8") as f:
            json.dump({"outro": ["Controle total do servidor (privileged)"]}, f)
        erros = confere.confere_loja(self.saida)
        self.assertTrue(any(e.startswith("outro: privilégios não batem") for e in erros), erros)


if __name__ == "__main__":
    unittest.main()
