# Nametag

Nametag helps you remember the people you care about. Keep notes, birthdays and important dates, see how everyone is connected in an interactive network graph, organize people into groups, keep a journal, and get reminders to stay in touch. Two-way CardDAV sync keeps it in step with Google Contacts, iCloud, Outlook or Nextcloud.

## Antes de instalar

Before installing, set NEXTAUTH_URL to the address you will open Nametag at, for example http://192.168.1.10:10300 (use your ZimaOS IP or domain). The default, http://localhost:10300, only works from the ZimaOS device itself, and sign-in and email links will point to the wrong place.

After installing, open Nametag and create your account. Anyone who can reach this port can also register, so once your account exists you can add DISABLE_REGISTRATION=true to close sign-ups.

Email is optional. To send reminder and password-reset emails, add the SMTP_* variables described at https://docs.nametag.one/self-hosting/email/

A receita original trazia uma chave secreta fixa (igual para todo mundo); aqui o Runtipi gera uma nova em cada instalação.

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
