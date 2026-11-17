# CasaOS (convertida pelo Garimpo do BrunOS)

Apps da loja oficial do CasaOS e do ZimaOS (IceWhale), convertidos para o formato do Runtipi.

Esta loja do Runtipi é gerada automaticamente todo dia a partir de <https://github.com/IceWhaleTech/CasaOS-AppStore> (licença Apache-2.0, cópia em `LICENSE-ORIGEM`). Não é a loja oficial do CasaOS nem tem ligação com os autores dela. Os nomes e logos dos apps são dos seus autores.

Para usar no Runtipi: *Lojas de apps → Adicionar*, nome `casaos`, endereço `https://github.com/BrunnoFe/Garimpo/tree/casaos`. No BrunOS: janela Loja → Lojas.

## Apps (107)

- AdGuard Home (`adguard-home`)
- Adminer (`adminer`)
- Alby Hub ✨ (`albyhub`)
- Alist (`alist`)
- Alist-Sync (`alist-sync`)
- Anaconda3 (`anaconda3`)
- AnythingLLM (`anythingllm`)
- BeaverHabitTracker (`beaverhabittracker`)
- BentoPDF (`bentopdf`)
- Blinko (`blinko`)
- Chatbot UI (`chatbot-ui`)
- ChatGPT Next Web (`chatgpt-next-web`)
- CloudBeaver (`cloudbeaver`)
- Clumoove (`frontend`)
- ConvertX (`convertx`)
- CopyParty (`copyparty`)
- ddns-go (`ddns-go`)
- DeepSeek OCR(Nvidia GPU) (`deepseek-ocr-frontend`)
- DeepSeekHarness (`dsh-harness`)
- Dify (`web`)
- Dispatcharr (`dispatcharr`)
- Downtify (`downtify`)
- Embystat (`embystat`)
- Etherpad (`etherpad`)
- FileDrop (`filedrop`)
- FileFlows (`fileflows`)
- Firefly (`firefly`)
- Frigate (`frigate`)
- gateway-go (`gateway-go`)
- Gopeed (`gopeed`)
- handbrake (`handbrake`)
- Hermes (`hermes`)
- HFS (`hfs`)
- HoloPlay (`holoplay`)
- Hugo (`hugo`)
- Index-TTS (`index-tts`)
- Index-TTS(Nvidia GPU) (`index-tts-nvidia`)
- JDownloader2 (`jdownloader2`)
- Jellyseerr (`jellyseerr`)
- Jenkins CI/CD (`jenkins`)
- Karakeep (`karakeep`)
- Label Studio (`label-studio`)
- Langflow (`langflow`)
- Lazylibrarian (`lazylibrarian`)
- LibreChat (`librechat-api`)
- LibreDB Studio (`libredb-studio`)
- LLaMA Factory(Nvidia GPU) (`llama-factory-nvidia`)
- llama.cpp (`llamacpp`)
- Logseq (`logseq`)
- Lucky (`lucky`)
- LyrionMusicServer (`lyrionmusicserver`)
- MariaDB (`mariadb`)
- Maybe (`maybe-web`)
- Medusa (`medusa`)
- MineOS (`mineos-node`)
- MongoDB 4 (`mongodb4`)
- Motioneye (`motioneye`)
- MySpeed (`myspeed`)
- Nametag (`nametag`)
- Netronome (`netronome`)
- Nginx Proxy Manager (`nginxproxymanager`)
- nzbfast (`nzbfast`)
- Nzbget (`nzbget`)
- Obsidian (`obsidian`)
- Ollama (`ollama`)
- Ombi (`ombi`)
- OpenHAB (`openhab`)
- OpenHands (`openhands`)
- OpenList (`openlist`)
- OpenSpeedTest (`openspeedtest`)
- oPodSync (`opodsync`)
- Overseerr (`overseerr`)
- PdfDing (`pdfding`)
- PeaNUT (`peanut`)
- Petio (`petio`)
- PocketBase (`pocketbase`)
- PostgreSQL (`postgresql`)
- Project NOMAD (`admin`)
- PsiTransfer (`psitransfer`)
- PyLoad (`pyload`)
- Qui (`qui`)
- RagFlow (`ragflow`)
- Real-Debrid Torrent Client (`rdtclient`)
- RetroArch (`retroarch`)
- Sickchill (`sickchill`)
- SiYuan Note (`siyuan-note`)
- Smokeping (`smokeping`)
- snapdrop (`snapdrop`)
- SnapOtter (`snapotter`)
- Stable Diffusion (`icewhale-stable-diffusion-webui`)
- Stremio (`stremio`)
- Sure (`sure-web`)
- Swing Music (`swingmusic`)
- Teable (`teable`)
- Threadfin (`threadfin`)
- TurboDiffusion(Nvidia GPU) (`turbodiffusion-nvidia`)
- Unifi Network Application (`unifi-network-application`)
- Unifi-controller [legacy] (`unifi-controller`)
- Upload Assistant (`upload-assistant`)
- V2rayA (`v2raya`)
- Virtual Machine Manager (`virt-manager`)
- VoceChat (`vocechat`)
- Wallabag (`wallabag`)
- WebDAV (`webdav`)
- WeKnora (`weknora`)
- WireGuard Easy (`wg-easy`)
- ZTnet (`ztnet`)

## Requerem privilégios (21)

Estes apps pedem poderes sobre o servidor que os apps comuns não têm. No BrunOS eles aparecem com o selo **Requer privilégios** e só instalam depois de "Entendo os riscos" + Senha de configuração. Na tela do próprio Runtipi aparecem sem aviso: instale só se confia no app.

- `admin`: Controla o Docker do servidor (socket do Docker): equivale a controle total; Mexe na pasta / do servidor
- `anythingllm`: Poderes de administrador do Linux (SYS_ADMIN)
- `fileflows`: Controla o Docker do servidor (socket do Docker): equivale a controle total
- `firefly`: Usa a rede do servidor direto, sem isolamento (network_mode: host); Poderes de administrador do Linux (NET_ADMIN, SYS_MODULE); Acesso ao aparelho /dev/net/tun do servidor; Mexe na pasta /lib/modules do servidor
- `frigate`: Controle total do servidor (privileged); Acesso ao aparelho /dev/bus/usb do servidor; Acesso ao aparelho /dev/apex_0 do servidor; Acesso ao aparelho /dev/video11 do servidor
- `gateway-go`: Usa a rede do servidor direto, sem isolamento (network_mode: host)
- `handbrake`: Controle total do servidor (privileged)
- `holoplay`: Controle total do servidor (privileged)
- `icewhale-stable-diffusion-webui`: Compartilha a memória compartilhada com o servidor (ipc: host)
- `jenkins`: Mexe na pasta /var/lib/docker/volumes/b098c98b2c5dec792246dc33375853c05958ace7c144f4aa157326a6f6c0de4c/_data do servidor
- `logseq`: Controle total do servidor (privileged)
- `lucky`: Usa a rede do servidor direto, sem isolamento (network_mode: host)
- `mineos-node`: Mexe na pasta /var/games/mineos/minecraft do servidor
- `openhab`: Usa a rede do servidor direto, sem isolamento (network_mode: host)
- `openhands`: Controla o Docker do servidor (socket do Docker): equivale a controle total
- `ragflow`: Controle total do servidor (privileged); Controla o Docker do servidor (socket do Docker): equivale a controle total
- `v2raya`: Controle total do servidor (privileged); Usa a rede do servidor direto, sem isolamento (network_mode: host); Mexe na pasta /lib/modules do servidor; Mexe na pasta /etc/resolv.conf do servidor
- `virt-manager`: Acesso ao aparelho /dev/kvm do servidor; Mexe na pasta /var/run/libvirt/libvirt-sock do servidor; Mexe na pasta /var/lib/libvirt do servidor
- `webdav`: Mexe na pasta /media/ZimaOS-HD/Media do servidor
- `wg-easy`: Poderes de administrador do Linux (NET_ADMIN, SYS_MODULE)
- `ztnet`: Mexe na pasta /var/lib/zerotier-one do servidor

## Não convertidos (5)

Receitas que não funcionariam no Runtipi ou que não deu para converter:

- NetBird: não tem página web (porta) para abrir
- RoonServer: não tem página web (porta) para abrir
- TaskingAI: outro app desta loja já usa o mesmo nome
- Twingate: não tem página web (porta) para abrir
- playit-agent: não tem página web (porta) para abrir

## Já existem na loja oficial do Runtipi (71)

Ficaram de fora para não aparecer duas vezes: 2FAuth, ActualBudget, ArchiveBox, Audiobookshelf, Autobrr, Bazarr, Calibre-web, Cloudflared, Crafty, DDNS-Updater, Databag, Deluge, Docmost, DuckDNS, Duplicati, ESPHome, Emby, Emby_Nvidia, EmulatorJS, Excalidraw, FlareSolverr, FlowiseAi, FreshRSS, Gitea, Glances, Grafana, HomeAssistant, Homebridge, Immich, Jackett, Jellyfin, Jellyfin_Nvidia, Kavita, Komga, Lidarr, Linkwarden, Memos, Mongo, Monica, Mylar3, N8n, Navidrome, Netdata, Nextcloud, Node-RED, Ollama_Nvidia, OpenClaw, OpenWebUI, PhotoPrism, Pihole, Pinchflat, Pingvin-Share, Plex, Plex_Nvidia, PodFetch, Portainer, Prowlarr, Radarr, Readarr, Resilio-sync, RomM, Sabnzbd, Sonarr, Syncthing, Tailscale, Tautulli, Transmission, Trilium, UptimeKuma, Vaultwarden, qBittorrent.
