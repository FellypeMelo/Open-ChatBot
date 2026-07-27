# Padrões de Design: Imersão Janitor AI / Character AI

## 1. Estética Visual
*   **HUD Cinemático**: A interface deve parecer um "Console Narrativo" em vez de um app de chat padrão.
*   **Estética**: Minimalista, com tema escuro por padrão, e tipografia de alto contraste para legibilidade.
*   **Fundos Imersivos**: Suporte para imagens de fundo específicas do personagem ou overlays cinemáticos desfocados.

## 2. UX de Mensagens
*   **Streaming em Tempo Real**: As palavras devem aparecer conforme são geradas, imitando uma sensação de "digitação".
*   **Blocos Narrativos**: Separação visual distinta entre:
    *   **Pensamentos**: Texto pequeno, em itálico, levemente transparente.
    *   **Ações**: Texto em negrito, com peso narrativo.
    *   **Fala**: Balões de diálogo grandes e claros, ou blocos de texto centralizados.
*   **Interação**: Efeitos de hover nas mensagens para mostrar "metadados" (ex.: impacto na afeição, custo de energia).

## 3. Modelo de Interação com o Personagem
*   **Perfil de Persona**: Uma sidebar dedicada ou view expansível mostrando:
    *   Tags dinâmicas (humor/comportamento atual).
    *   Barras de status (Energia, Fome, Relacionamento).
    *   Trechos de "Memória de Longo Prazo" atualmente em foco.

## 4. Fluxo Single-User
*   **Persistência Local**: Sem necessidade de login; o sistema carrega o perfil do usuário local automaticamente a partir de `chatbot.db`.
*   **Modo Offline**: Operação principal é offline via `llama.cpp`. Um indicador visual mostra o "Status do Motor" (modelo carregado, tokens/seg, uso de VRAM).
