# Project NOMAD

O Project NOMAD é um servidor de conhecimento e educação offline com um centro de controle acessível pelo navegador. Instale e gerencie a Wikipédia e livros digitais com Kiwix, cursos com Kolibri, IA local com Ollama e Qdrant, mapas offline, CyberChef e notas em uma única interface.

Este pacote inclui o centro de controle, MySQL, Redis, Dozzle para os logs dos serviços e monitoramento dos discos do host. As ferramentas opcionais, os modelos de IA e os conteúdos offline são instalados separadamente pela interface NOMAD.

## Antes de instalar

Requer um dispositivo amd64 com pelo menos 4 GB de RAM e 10 GB livres para instalação. Os modelos de IA e os conteúdos offline exigem recursos adicionais. Antes da primeira inicialização, defina URL com o endereço do dispositivo, escolha um APP_KEY exclusivo com pelo menos 32 caracteres e altere DB_PASSWORD junto com MYSQL_PASSWORD, além de MYSQL_ROOT_PASSWORD. O NOMAD não tem autenticação e pode gerenciar contêineres Docker: use apenas em uma rede local confiável. Mantenha o nome do contêiner nomad_admin e o nome da rede project-nomad_default. Atualize o centro de controle pelo ZimaOS; o atualizador automático do projeto não está incluído. Remova as ferramentas opcionais no NOMAD antes de desinstalar este pacote, pois elas usam contêineres separados.

A receita original trazia uma chave secreta fixa (igual para todo mundo); aqui o Runtipi gera uma nova em cada instalação.

## Requer privilégios

A receita deste app pede poderes sobre o servidor que os apps comuns não têm. Instale só se confia nele:

- Controla o Docker do servidor (socket do Docker): equivale a controle total
- Mexe na pasta / do servidor

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
