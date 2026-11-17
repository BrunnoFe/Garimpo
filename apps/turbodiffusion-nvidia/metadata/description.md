# TurboDiffusion(Nvidia GPU)

TurboDiffusion é um framework acelerado para geração texto-para-vídeo baseado no Latent Consistency Model (LCM). Ele utiliza vários modelos TurboWan2 para gerar rapidamente vídeos de alta qualidade a partir de descrições de texto. O framework suporta geração de imagens e vídeos e fornece checkpoints otimizados para diferentes configurações de GPU.

**Principais funcionalidades:**
- Geração ultra-rápida de vídeos e imagens
- Gradio WebUI intuitivo
- Otimizado para diferentes configurações de GPU
- Checkpoints quantizados e não quantizados
- Configuração de modelo flexível

**Requisitos de hardware:**
- Recomendado: RTX 3090 ou superior
- VRAM da GPU: > 30 GB
- RAM do sistema: > 40 GB
- Drivers NVIDIA compatíveis com CUDA

**Saiba mais:**
- [TurboDiffusion GitHub](https://github.com/thu-ml/TurboDiffusion)

## Antes de instalar

Modelo integrado: TurboWan2.1-T2V-1.3B-480P

1. Lista de modelos oficialmente suportados (organização oficial HF TurboDiffusion)
Text-to-Video (T2V)
- [TurboDiffusion/TurboWan2.1-T2V-1.3B-480P](https://huggingface.co/TurboDiffusion/TurboWan2.1-T2V-1.3B-480P)
- [TurboDiffusion/TurboWan2.1-T2V-14B-480P](https://huggingface.co/TurboDiffusion/TurboWan2.1-T2V-14B-480P)
- [TurboDiffusion/TurboWan2.1-T2V-14B-720P](https://huggingface.co/TurboDiffusion/TurboWan2.1-T2V-14B-720P)
Image-to-Video (I2V)
- [TurboDiffusion/TurboWan2.2-I2V-A14B-720P](https://huggingface.co/TurboDiffusion/TurboWan2.2-I2V-A14B-720P)

2. Instalar hf download (Hugging Face CLI) (Executar no terminal)

- Método A (Recomendado): Script de instalação oficial com um clique
`curl -LsSf https://hf.co/cli/install.sh | bash`

- Método B: pip install (adequado para ambientes Python existentes)
`pip install -U huggingface_hub`

- Verificar após a instalação:
`hf --help`

3. Transferir pesos de modelo específicos para um diretório fixo (Modelo de comando recomendado)
Modelo:
`hf download <repo_id> <filename> --local-dir /DATA/AppData/turbodiffusion_nvidia/models`
Exemplo: Transferir pesos quant 14B 720P (ajustar com base no nome real do ficheiro no repo)
`hf download TurboDiffusion/TurboWan2.1-T2V-14B-720P TurboWan2.1-T2V-14B-720P-quant.pth --local-dir /DATA/AppData/turbodiffusion_nvidia/models`

4. Como aplicar após a transferência estar concluída
- Confirmar que o ficheiro de pesos está em: `/DATA/AppData/turbodiffusion_nvidia/models`
- Atualizar a lista de modelos na WebUI, clicar em discover model / refresh model list

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
