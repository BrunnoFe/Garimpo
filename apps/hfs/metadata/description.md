# HFS

HFS is an HTTP file server with uploads, downloads, user accounts, permissions,
a virtual file system and plugins. Manage it through the Admin panel and share
files with users through the web interface.
This installation starts with a dedicated empty shared folder. To share an
existing folder, change the host path of the /shares volume in app settings.

## Antes de instalar

**First login**

| Username | Password |
|----------|----------|
| `admin` | `please-change` |

After logging in, open **Accounts**, select **admin**, and change the password.

To choose your own password before installation, use Custom Installation
instead of Install. Under Environment Variables, replace the value of
HFS_INITIAL_ADMIN_PASSWORD with your password (not username:password).
This variable is only used when no configuration file exists.
After installation, change passwords in HFS Admin, not in app settings.

A receita original vinha com uma senha fixa (igual para todo mundo); aqui você escolhe a sua na instalação.

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
