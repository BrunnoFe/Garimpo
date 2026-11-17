# BentoPDF

**Your PDFs never leave your device.** BentoPDF is a privacy-first PDF toolkit that runs entirely in your browser. Every merge, split, conversion, and edit happens locally on your machine — no file is ever uploaded to a server. More than 50 tools are bundled into one clean, fast, ad-free interface.

**One app for every PDF job.** Organize and edit your documents (merge, split, reorder, rotate, crop, watermark, page numbers, redaction, annotations and forms), convert to and from PDF (images, Word, Excel, PowerPoint, EPUB, Markdown and more), run OCR, and secure your files with compression, encryption, digital signatures, and metadata cleanup.

**Made for your private cloud.** Self-hosting BentoPDF on a private cloud device like Zima gives your whole household or team a single, ad-free PDF workshop on hardware you control — fast over the local network, with your documents staying private by design.

## Antes de instalar

## Getting Started

Open the Web UI at `http://<your-zima-ip>:3000`. BentoPDF is ready to use immediately — there is no account or setup, and files are processed entirely in your browser, never uploaded to a server.

## HTTPS for Office conversions

Converting Office files (Word, Excel, PowerPoint) relies on the browser feature `SharedArrayBuffer`, which is only available in a secure context. When you access BentoPDF over a LAN IP or hostname (anything other than `localhost`), serve it behind HTTPS — for example through CasaOS's reverse proxy — to enable these conversions.

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
