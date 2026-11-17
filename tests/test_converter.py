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

    def test_recusas(self):
        casos = {
            "privileged: true": "privileged",
            "network_mode: host": "rede do servidor",
            "pid: host": "pid",
            "cap_add: [NET_ADMIN]": "NET_ADMIN",
            "devices: [/dev/kvm:/dev/kvm]": "/dev/kvm",
            "security_opt: [apparmor:unconfined]": "proteção",
            "volumes: [/var/run/docker.sock:/var/run/docker.sock]": "socket do Docker",
            "volumes: [/etc:/host-etc]": "/etc",
            "volumes: [/:/raiz]": "pasta / ",
            "volumes: [/home/fulano:/x]": "/home/fulano",
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
                self.assertIn(motivo.strip(), e.exception.args[0] + " ")

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
        ok, recusados, dup, _ = c.converte_loja(ORIGEM, self.fonte, self.oficial, self.saida, self.padrao, agora_ms=1_800_000_000_000)
        self.assertEqual(sorted(i for i, _, _ in ok), ["meuapp", "outro"])
        self.assertEqual([d for d, _ in recusados], ["Ruim"])
        # portas únicas na loja (as duas receitas pedem 8123)
        self.assertEqual({self.cfg("meuapp")["port"], self.cfg("outro")["port"]}, {8123, 8124})
        self.assertTrue(os.path.isfile(os.path.join(self.saida, "apps", "meuapp", "metadata", "logo.jpg")))
        g = json.loads(c.le(os.path.join(self.saida, "garimpo.json")))
        self.assertEqual((g["nome"], g["selo"], g["apps"], g["recusados"]), ("Teste", "via Teste", 2, 1))
        self.assertIn("Ruim: o serviço ruim pede privileged", c.le(os.path.join(self.saida, "README.md")))
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
        self.assertTrue(any("privileged" in e for e in erros))
        self.assertTrue(any("/etc:/etc" in e for e in erros))


if __name__ == "__main__":
    unittest.main()
