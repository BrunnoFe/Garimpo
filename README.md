# Garimpo

Converte lojas de apps do **CasaOS/ZimaOS** para o formato de loja do **[Runtipi](https://runtipi.io)**,
para usar no Runtipi e na janela Loja do [BrunOS](https://github.com/BrunnoFe/DashboardBrunOS).

Cada loja de origem vira um **ramo** deste repositório, que é uma loja do Runtipi completa:

| Loja | Origem | Licença da origem | Endereço para o Runtipi |
|---|---|---|---|
| CasaOS | [IceWhaleTech/CasaOS-AppStore](https://github.com/IceWhaleTech/CasaOS-AppStore) (loja oficial do CasaOS e do ZimaOS) | Apache-2.0 | `https://github.com/BrunnoFe/Garimpo/tree/casaos` |
| LinuxServer | [WisdomSky/LinuxServer-AppStore](https://github.com/WisdomSky/LinuxServer-AppStore) | GPL-3.0 | `https://github.com/BrunnoFe/Garimpo/tree/linuxserver` |

Para adicionar no Runtipi: *Lojas de apps → Adicionar*, com o nome `casaos` (ou `linuxserver`) e o
endereço da tabela. No BrunOS: janela **Loja → Lojas**, botão da loja sugerida.

Estas lojas **não são oficiais** e não têm ligação com a IceWhale, com o LinuxServer.io nem com os autores dos
apps. Os nomes e logos dos apps são dos seus autores.

## Como funciona

Um GitHub Actions roda todo dia de madrugada (e quando o código muda):

1. baixa a loja de origem e a loja oficial do Runtipi;
2. converte cada app (`garimpo/converter.py`):
   - `docker-compose.yml` do CasaOS → `docker-compose.yml` do Runtipi com `x-runtipi` (serviço principal com o
     nome do app, porta da página web pelo Runtipi, versão igual à tag da imagem);
   - dados do app (`/DATA/AppData/<app>`) → pasta do app no Runtipi (entra no backup dele);
     `/DATA/Media`, `/DATA/Downloads`... → pasta de mídia compartilhada do Runtipi;
   - `$PUID`/`$PGID` → 1000, `$TZ` → fuso do Runtipi; outras variáveis viram perguntas da instalação;
   - **perguntas da instalação**: senha fixa na receita vira pergunta obrigatória (menos as de serviços
     internos do app: banco, busca, MinIO...); o usuário que anda com ela e as variáveis que o CasaOS descreve
     (`x-casaos.envs`) viram perguntas já preenchidas. O `perguntas.json` corrige app a app (`perguntar` /
     `nao_perguntar`);
   - textos em português quando a receita tem, senão em inglês; logo em JPEG 256×256;
   - apps que já existem na loja oficial do Runtipi ficam de fora (para não aparecer duas vezes);
   - `tipi_version` sobe sozinho quando a receita muda (é assim que o Runtipi avisa de atualização);
3. **lista o que dá poder sobre o servidor** (`privilegios.json` e README do ramo): `privileged`, socket do
   Docker, rede do servidor (`network_mode: host`), `pid`/`ipc` do servidor, poderes de administrador do Linux
   (`SYS_ADMIN`, `NET_ADMIN`...), pastas do sistema e aparelhos além da placa de vídeo. Desde 17/11/2026 esses
   apps entram na loja: o BrunOS mostra o selo **Requer privilégios** e só instala depois de "Entendo os riscos"
   + Senha de configuração (na tela do próprio Runtipi eles aparecem sem aviso). Ficam de fora só as receitas
   que não funcionariam (rede de outro container, `volumes_from`, variável desconhecida numa pasta...);
4. confere tudo de novo com um programa separado (`garimpo/confere.py`), inclusive se cada privilégio da
   receita está no `privilegios.json` (nada pode ficar escondido);
5. roda os **testes oficiais da loja do Runtipi** (`garimpo/testes-oficiais.sh`) sobre a loja convertida;
6. só então publica no ramo.

## Rodar aqui

```bash
pip install pyyaml pillow            # pillow e rsvg-convert são opcionais (logos)
python3 -m unittest discover -s tests
git clone --depth 1 https://github.com/IceWhaleTech/CasaOS-AppStore /tmp/fonte
git clone --depth 1 https://github.com/runtipi/runtipi-appstore /tmp/oficial
python3 garimpo/converter.py --origem casaos --fonte /tmp/fonte --oficial /tmp/oficial --saida /tmp/casaos
python3 garimpo/confere.py /tmp/casaos
bash garimpo/testes-oficiais.sh /tmp/oficial /tmp/casaos   # precisa do bun
```

Origens novas entram em `origens.json` (e na lista `matrix.origem` do workflow).

## Licença

O código do conversor é MIT (Bruno Barbosa). As lojas convertidas seguem a licença da loja de origem (cópia em
`LICENSE-ORIGEM` em cada ramo).
