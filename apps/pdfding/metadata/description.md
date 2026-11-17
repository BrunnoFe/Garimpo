# PdfDing

PdfDing é um gestor, visualizador e editor PDF auto-hospedado que oferece uma experiência de utilizador perfeita em múltiplos dispositivos. Foi concebido para ser mínimo, rápido e fácil de configurar usando Docker.

Com funcionalidades como visualização PDF baseada em navegador que lembra a sua posição atual, etiquetagem multi-nível, funcionalidades de favoritos e arquivo, edição PDF com comentários, realces e desenhos, interface de utilizador limpa e intuitiva com modo escuro, suporte SSO via OIDC, partilha de PDF com audiência externa, notas markdown e barras de progresso que mostram o progresso de leitura, PdfDing garante uma excelente experiência de gestão PDF.

Implementar PdfDing em dispositivos cloud privados como Zima traz conveniência incomparável com acesso multi-dispositivo, garantindo que a sua coleção PDF está sempre ao alcance e segura, não importa onde esteja.

## Antes de instalar

Após a instalação, pode aceder ao PdfDing em http://your-server-ip:8000. Crie a sua primeira conta de administrador durante a configuração inicial.

Nota: Se encontrar problemas de acesso, poderá precisar de editar manualmente o ficheiro docker-compose.yml e substituir a variável de ambiente HOST_NAME pelo seu endereço IP real do servidor.

A receita original trazia uma chave secreta fixa (igual para todo mundo); aqui o Runtipi gera uma nova em cada instalação.

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
