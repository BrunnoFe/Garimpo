# llama.cpp

O llama.cpp é um motor de inferência em C/C++ puro para grandes modelos de linguagem GGUF, com o servidor oficial compatível com OpenAI e uma interface web integrada.

**Principais recursos:**
- Execute modelos GGUF (Llama, Qwen, DeepSeek, Gemma, Mistral e mais) na CPU ou GPU
- O backend Vulkan funciona imediatamente em GPUs AMD / Intel / NVIDIA
- Ótimo para máquinas com memória unificada (ex.: AMD Ryzen AI Max 395)
- API compatível com OpenAI para Open WebUI, ChatGPT-Next-Web e mais
- Interface web de chat integrada com carregamento de modelos em tempo de execução

**Primeiros passos:**
1. Coloque os arquivos de modelo GGUF no volume de modelos (`/models`)
2. Abra a interface web em `http://<zima-ip>:18080` e carregue um modelo
3. Mantenha `/dev/dri` para aceleração Vulkan; remova para o modo somente CPU

---

Convertido automaticamente da loja CasaOS (https://github.com/IceWhaleTech/CasaOS-AppStore, licença Apache-2.0) pelo Garimpo do BrunOS. Pastas: os dados do app ficam na pasta do app no Runtipi; filmes, músicas, fotos e downloads, na pasta de mídia do Runtipi. Problemas com o app em si: fale com o autor dele.
