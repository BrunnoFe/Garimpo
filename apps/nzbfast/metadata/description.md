# nzbfast

nzbfast is a speed-focused Usenet (NZB) downloader written in Rust. It is one small binary with a low memory footprint, and it saturates a fast line with a handful of connections.

Articles are verified while they arrive, so most jobs finish with no separate verify pass. Repair and unpack run only when they are actually needed, and extraction starts before the last article lands.

The web dashboard on port 6790 also serves a SABnzbd-compatible API, so Sonarr, Radarr, Prowlarr and friends work with no extra glue. Add an .nzb from the dashboard, or drop one into the watch folder.

First run: open the dashboard, add your Usenet provider under Settings, and copy the API key it shows you into your *arr apps. If you would rather pin the key yourself so it survives a reinstall, set NZBFAST_APIKEY before the first start. Leave it empty and nzbfast generates one for you.

## Antes de instalar

Your settings, API key and queue live in the config folder. Keep that mapping pointed at the same host folder when you update or reinstall, or nzbfast comes back looking like a fresh install.

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
