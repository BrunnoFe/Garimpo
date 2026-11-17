# Firefly

Firefly is a simple and easy to install WireGuard server software, which can be widely used in scenarios such as remote networking, remote work, and expose a local server behind a NAT or firewall to the internet.  🎯 Features 🟢 Provide a simple and easy-to-use web management UI  🟣 Supports access to all WireGuard clients  🟡 No need for system installation of WireGuard components  🟠 Single file, no additional library dependencies  🔴 Automatically apply for free SSL certificate

## Antes de instalar

Default password for admin background `firefly`, you can modify it in environment variables.

A receita original vinha com uma senha fixa (igual para todo mundo); aqui você escolhe a sua na instalação.

## Requer privilégios

A receita deste app pede poderes sobre o servidor que os apps comuns não têm. Instale só se confia nele:

- Usa a rede do servidor direto, sem isolamento (network_mode: host)
- Poderes de administrador do Linux (NET_ADMIN, SYS_MODULE)
- Acesso ao aparelho /dev/net/tun do servidor
- Mexe na pasta /lib/modules do servidor

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
