# Smoke test manual em dispositivo móvel real via LAN

Uma passada manual curta para rodar em um celular de verdade sempre que houver
mudanças na UI voltada para mobile. Isso **não** é um substituto para a suíte
automatizada — existe especificamente para pegar o que a automação estruturalmente
não consegue (veja a última seção). Leva cerca de 5 minutos.

## 1. Colocar para rodar na LAN

1. A partir da raiz do repositório, rode `run.bat` (sem o argumento `local` — isso
   vincula somente a localhost e os celulares não conseguem alcançar).
2. Ele builda o frontend e depois imprime o próprio IP da LAN, por exemplo:
   ```
   LAN mode ON. On your phone (same Wi-Fi) open:
       http://192.168.1.23:8000
   ```
   Não precisa rodar `ipconfig` — a saída do console já é a URL a usar. Se em
   algum momento ele falhar em detectar um IP, caia para `ipconfig` (procure o
   endereço IPv4 no seu adaptador Wi-Fi/Ethernet) e monte a URL você mesmo.
3. Na primeira conexão você pode receber um prompt do Firewall do Windows no PC —
   permita o Python em **redes privadas**.
4. Abra essa URL `http://<ip-da-lan>:8000` no navegador do celular (Safari no iOS,
   Chrome no Android — verifique os dois se você estiver mexendo em layout/código
   de viewport).

## 2. Checklist

- [ ] **Hambúrguer do sidebar** — toque para abrir, o backdrop aparece, toque no
  backdrop (ou no hambúrguer de novo) para fechar. Sem salto de layout.
- [ ] **Barra de tabs inferior** (`MobileTabBar`) — visível na parte de baixo em
  larguras mobile, alterna entre views (Chat/Characters/Library/etc.), a tab ativa
  é visualmente distinta.
- [ ] **Enviar uma mensagem** — o composer cresce automaticamente conforme você
  digita um prompt multi-linha (não fica travado em uma linha); depois de enviar,
  toque nos botões de ação de uma mensagem (Regenerate / Edit / Delete / Copy ID)
  diretamente — eles precisam ser tocáveis no primeiro toque, **sem etapa de
  hover** necessária.
- [ ] **HUD de stats** — o toggle de colapsar/expandir funciona no chip de resumo
  mobile; a grade expandida é legível e os controles de +/- de stat são tocáveis
  com o polegar.
- [ ] **Sem scroll/overflow horizontal** — deslize/role na horizontal em cada tela
  principal (Characters, Chat, Lorebook, Tags) e confirme que a página nunca faz
  pan horizontal, não importa em qual tela ou modal você esteja.
- [ ] **Teclado vs. composer** (⚠️ área conhecidamente mais fraca — observe esta
  com atenção). Toque no input do chat para abrir o teclado on-screen e verifique
  se o composer e o botão Send continuam visíveis acima dele, não escondidos atrás
  do teclado ou de uma home-bar/área de gesto. Só o padding de safe-area foi
  entregue até agora; ainda não há tratamento de resize via `visualViewport`,
  então este é o ponto mais provável de ainda estar quebrado, especialmente no
  Chrome Android ou com um teclado flutuante/dividido. Reporte exatamente o que
  você vê (input totalmente escondido, parcialmente coberto, ok) em vez de um
  passou/falhou — espera-se que isso precise de trabalho de acompanhamento.
- [ ] **Adicionar à tela inicial / instalação PWA** — no Safari iOS use
  Compartilhar → "Adicionar à Tela de Início"; no Chrome Android use o prompt de
  instalação (menu → "Instalar app", ou o banner automático). Confirme que um
  ícone real aparece (não uma imagem em branco/quebrada) e que o app instalado
  abre em modo standalone (sem chrome do navegador).

## 3. Por que isso não pode ser substituído pelo Playwright

O CI agora roda os projetos de emulação de dispositivo `mobile-chrome` (Pixel 5) e
`mobile-safari` (iPhone 13) do Playwright. Essa cobertura é real e deve continuar
verde, mas a emulação de dispositivo não consegue reproduzir:

- O comportamento real do `100dvh` do Safari iOS conforme a barra de endereço
  aparece/some.
- Os valores reais de `env(safe-area-inset-*)` em um dispositivo com notch/home
  indicator.
- Rolagem por momentum nativa e oclusão de teclado on-screen.
- A instalação real de "Adicionar à Tela de Início" e a renderização em modo
  standalone.

A emulação verifica a lógica de DOM/CSS; este checklist verifica o que um motor de
navegador real faz com ela. Rode os dois: os testes automatizados a cada mudança,
esta passada manual antes de lançar qualquer coisa que toque no layout mobile, no
composer, no HUD, na safe-area, ou no manifest/service worker.
