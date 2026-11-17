# Etherpad

Etherpad é um editor colaborativo de documentos em tempo real onde várias pessoas podem editar o mesmo pad em simultâneo, com cada alteração sincronizada de imediato e identificada por cores por autor.
Auto-hospedado, open source e totalmente sob o seu controlo, é ideal para notas de reunião, brainstorming, escrita partilhada e recolha leve de conhecimento.
Inclui um painel de administração integrado, um ecossistema com mais de 250 extensões, importação e exportação nativas de DOCX/PDF/Markdown e suporte de contentor multiarquitetura (amd64 + arm64).

**Principais Funcionalidades:**
- Edição colaborativa em tempo real com sincronização imediata
- Identificação por cores por autor para atribuição clara do texto
- Painel de administração integrado e ecossistema com mais de 250 extensões
- Importação e exportação nativas de DOCX, PDF e Markdown
- Implementação auto-hospedada open source com suporte para amd64 e arm64

**Saiba Mais:**
- [Site Oficial Etherpad](https://etherpad.org/)
- [Etherpad GitHub](https://github.com/ether/etherpad)
- [Documentação Etherpad](https://docs.etherpad.org/)

## Antes de instalar

A palavra-passe de administrador predefinida é "admin". Altere ADMIN_PASSWORD antes de expor o Etherpad à rede. Os pads são guardados em disco em /DATA/AppData/etherpad/var usando a base de dados dirty incorporada; esta configuração é ideal para uso pessoal e pequenas equipas. Para cargas de produção multiutilizador mais pesadas, altere DB_TYPE para postgres ou mysql e aponte DB_HOST, DB_NAME, DB_USER e DB_PASS para uma base de dados externa.

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
