# Unifi Network Application

Only mandatory ports are enabled by default, to extend functionality consider exposing 1900:1900/udp, 8843:8843, 8880:8880, 6789:6789, 5514:5514/udp.
Other ports specifications [here](https://docs.linuxserver.io/images/docker-unifi-network-application/#ports-p).

Because the network application runs inside Docker by default it uses an IP address not accessible by other devices.
So, for it to adopt other devices, it is required to use port `8080` and change the inform IP address. To do so, go in settings and search for the `Inform Host` option, there select override and set the address to that of the host.
Often, it is also needed to ssh into the devices you want to adopt and manually set the inform IP address, the command needed for doing so is `set-inform http://HOST-ADDRESS:8080/inform`.

For more [information](https://docs.linuxserver.io/images/docker-unifi-network-application/)

## Antes de instalar

Only mandatory ports are enabled by default, to extend functionality consider exposing 1900:1900/udp, 8843:8843, 8880:8880, 6789:6789, 5514:5514/udp.
Other ports specifications [here](https://docs.linuxserver.io/images/docker-unifi-network-application/#ports-p).

Because the network application runs inside Docker by default it uses an IP address not accessible by other devices.
So, for it to adopt other devices, it is required to use port `8080` and change the inform IP address. To do so, go in settings and search for the `Inform Host` option, there select override and set the address to that of the host.
Often, it is also needed to ssh into the devices you want to adopt and manually set the inform IP address, the command needed for doing so is `set-inform http://HOST-ADDRESS:8080/inform`.

For more [information](https://docs.linuxserver.io/images/docker-unifi-network-application/)

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
