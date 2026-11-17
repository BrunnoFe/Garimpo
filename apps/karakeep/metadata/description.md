# Karakeep

O Karakeep é um gestor de marcadores open-source e auto-hospedado para ligações, notas, imagens, PDFs e destaques, criado para reunir num só lugar tudo o que quer guardar.
Obtém automaticamente títulos, descrições e pré-visualizações e depois ajuda a organizar a biblioteca com etiquetagem por IA, pesquisa em texto completo, listas e automação baseada em regras.
Com extensões de navegador, aplicações móveis, ingestão RSS e arquivamento de páginas, o Karakeep funciona bem tanto como ferramenta de leitura posterior como arquivo pessoal duradouro de conteúdos.

**Principais Funcionalidades:**
- Guarda ligações, notas, imagens, PDFs e destaques de texto numa única biblioteca
- Obtém automaticamente títulos, descrições, imagens e páginas arquivadas para leitura posterior
- Usa etiquetagem por IA, resumos, OCR e pesquisa em texto completo para reencontrar conteúdos rapidamente
- Organiza conteúdos com etiquetas, listas colaborativas, feeds RSS e fluxos de trabalho baseados em regras
- Dá acesso à coleção através da aplicação web, aplicações móveis, extensões de navegador, API REST e CLI

**Saiba Mais:**
- [Site Oficial Karakeep](https://karakeep.app/)
- [Karakeep GitHub](https://github.com/karakeep-app/karakeep)
- [Documentação do Karakeep](https://docs.karakeep.app/)

## Antes de instalar

Defina `NEXTAUTH_URL` para o endereço que vai usar para aceder ao Karakeep.
Use cadeias aleatórias longas para `NEXTAUTH_SECRET` e `MEILI_MASTER_KEY`, e mantenha o mesmo `MEILI_MASTER_KEY` em `karakeep` e `meilisearch`.
O primeiro utilizador a registar-se na sua instância torna-se administrador.

A receita original trazia uma chave secreta fixa (igual para todo mundo); aqui o Runtipi gera uma nova em cada instalação.

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
