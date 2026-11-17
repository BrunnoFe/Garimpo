# SnapOtter

SnapOtter is an open-source, self-hosted file manipulation suite with 200+ tools across images, video, audio, PDFs, and files. It includes batch processing, reusable pipelines, local AI tools, a browser image editor, and a REST API so files stay on your own server.

This package uses SnapOtter's single-container embedded mode for an easy CasaOS install. PostgreSQL 17 and Redis 8 run inside the container when DATABASE_URL and REDIS_URL are left unset, with persistent data stored under /data.

Default login is admin / admin. SnapOtter asks you to change the default password after first login.

## Antes de instalar

Default login is admin / admin. You will be asked to change the password after first login.

This package uses SnapOtter embedded mode, so leave DATABASE_URL and REDIS_URL unset unless you are moving to the upstream multi-container PostgreSQL and Redis stack.

A receita original vinha com uma senha fixa (igual para todo mundo); aqui você escolhe a sua na instalação.

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
