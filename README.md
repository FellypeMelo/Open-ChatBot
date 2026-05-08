# Open-ChatBot
Desenvolvimento de sistemas conversacionais locais com foco em IA contextual, persistência de memória, modelagem comportamental e personalização avançada de agentes inteligentes, visando interações mais naturais, adaptativas e semanticamente coerentes.

## Living Entity Framework v5
Este projeto utiliza uma arquitetura de 5 camadas para gerar personas imersivas e persistentes.

### Como Iniciar (Tudo em um)

Para facilitar o início, criamos scripts de automação que iniciam os dois servidores de IA (Inferência e Embedding) e o backend Python simultaneamente.

**No Linux (Bash/Fish):**
```bash
chmod +x run.sh
./run.sh
```

**No Windows:**
```cmd
run.bat
```

*Nota: Certifique-se de que o Intel oneAPI está instalado nos locais padrão ou ajuste os caminhos nos scripts.*

### Servidores Individuais
O sistema agora requer três componentes rodando em paralelo:
1. **Llama Inference Server** (Porta 8080)
2. **Llama Embedding Server** (Porta 8081)
3. **Python Backend** (Porta 8000)
