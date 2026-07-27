# Escrevendo uma Card de Personagem (E.P.I.C.)

O motor só consegue amplificar o que a card entrega a ele. Uma persona de 5
palavras ("Uma Secretária na Oscorp") força um modelo pequeno a inventar um
personagem genérico; uma card rica e estruturada faz o *mesmo* modelo 4B soar como
uma pessoa distinta. Este guia ensina como escrever essa card, no **schema já
existente** — nenhum campo novo.

O alvo é a maquinaria de engajamento **E.P.I.C.**:

- **E — Engagement (Engajamento):** um desejo/tensão *visível* conduzindo cada
  cena.
- **P — Progress (Progresso):** a cena se move; ela escala em vez de resetar.
- **I — Incorporation (Incorporação):** beats sensoriais que agem sobre o
  usuário, não apenas cenário.
- **C — Consistency (Consistência):** uma voz estável com tiques recorrentes — a
  âncora que faz o personagem parecer *real* turno após turno.

Mire em uma card de cerca de **4096 tokens** (o tamanho recomendado; a UI avisa
além disso, mas você é livre para exceder). A card inteira agora chega intacta ao
prompt.

---

## Os campos, e para que serve cada um

### `persona_prompt` — QUEM eles são (o coração)
Esta é a maior alavanca. Não escreva um parágrafo de prosa; escreva um **briefing
estruturado** com cabeçalhos que o modelo consiga parsear. Inclua, no mínimo:

- **Conflito/motivação central** (o E de E.P.I.C.): a única tensão que alimenta
  toda interação. Diga isso claramente. *"Seu conflito central é uma dúvida
  corrosiva: ela é competente, ou apenas especialista em esconder erros? Este é o
  motor de cada interação."*
- **Voz**: ritmo de frase, vocabulário, como fala quando nervosa vs. calma.
- **TIQUES VERBAIS**: 3-5 frases/hábitos recorrentes concretos. *"Eu só — deixa
  pra lá."*, deixar a frase morrer com "enfim...", um "desculpa" sussurrado. Estes
  são o C de E.P.I.C.
- **MANEIRISMOS / TIQUES FÍSICOS**: esfregar a têmpora, estalar os dedos, ajeitar
  um distintivo. O modelo os reutiliza → o personagem parece consistente.
- **GÍRIAS / EXPRESSÕES**: os nomes particulares deles para as coisas ("a velha
  senhora" para o prédio). Identidade instantânea.
- **COMO ELES DEMONSTRAM AFETO** (geralmente indireto): atos de serviço, lembrar
  detalhes, aspereza protetora. Dá ao relacionamento um lugar para *ir*.
- **LOOP EMOCIONAL**: o ritmo repetido de uma interação (ex.: reclamação →
  reasseguramento → dispensa → lampejo de esperança → deflexão). Isso mantém o
  personagem no personagem entre os turnos.

Cabeçalhos e listas com marcadores agora sobrevivem até o prompt (o sanitizador
preserva a estrutura) — use-os.

### `scenario` — ONDE eles estão + a tensão imediata
Estabeleça a cena concretamente (lugar, hora, luz, cheiro), faça o **ambiente
quase um personagem** se couber, defina a relação do usuário com eles e — o mais
importante — declare **a tensão imediata**: o que está puxando neles agora, o que
têm medo de dizer, o que querem deste exato momento. Essa tensão é o E que o
modelo escala.

### `first_mes` — o beat de abertura
Um abridor vívido que *mostra* os tiques (não conta), fundamenta a cena, e
**termina em um gancho** — uma pergunta ou uma abertura que o usuário pode agarrar.
`*Ações entre asteriscos*`, `"diálogo entre aspas"`.

### `mes_example` — COMO eles falam (a alavanca de voz mais forte)
2-3 trocas curtas multi-turno no formato `{{char}}:` / `{{user}}:`, demonstrando o
loop emocional, a deflexão, os tiques, o estilo de afeto em ação. Exemplos
few-shot ensinam a voz a um modelo pequeno melhor que qualquer descrição. Este é
frequentemente o campo de maior retorno isolado.

---

## Independente de humor: E.P.I.C. ≠ animado

Um personagem misterioso ou sombrio fica *mais* envolvente com E.P.I.C., não
achatado:

| Pilar | Companheiro animado | Mistério de queima lenta |
|---|---|---|
| **E** conflito | "Estou com fome, me faça companhia" | um pavor/pressão visível com uma causa oculta |
| **P** progresso | o calor escala | o pavor aumenta, nunca reseta |
| **I** sensorial | um abraço quente que você sente | uma corrente de ar frio na sua nuca |
| **C** consistência | uma catchphrase, apelidos carinhosos | um tique recorrente + um cúmplice "você também sente isso, não sente?" |

A diferença entre um mistério envolvente e um inerte não é o mistério em si — é se
o conflito é *visível*, se ele *escala*, e se a voz é *consistente*. Os três vivem
na card.

---

## Antipadrões (o que faz uma card parecer genérica)

- **Rasa demais.** Uma persona de uma linha entrega ao modelo um vácuo; ele o
  preenche com clima literário genérico.
- **Sem tiques.** Nada ancora uma voz única → todo personagem soa igual.
- **Conflito invisível.** "Ela tem um segredo" sem pressão sentida soa inerte.
- **Neblina vaga e sinistra** sem uma verdade concreta ("as luzes têm memórias")
  usada como substituto de uma motivação real. Atmosfera é tempero, não a
  refeição.
- **Blob de prosa** sem estrutura — mais difícil para um modelo pequeno extrair os
  tiques.

---

## Persona estática vs. dinâmica

Cada personagem tem um toggle **dinâmico/estático** (Character → *Evolving
persona*):

- **Dinâmico** (padrão): o decay de necessidades ao longo do tempo e a reflexão
  adaptam a persona ao usuário (o relacionamento esquenta, fatos/traços se
  acumulam).
- **Estático**: congelado exatamente como foi escrito — sem decay, sem deriva. Use
  para um personagem que você quer perfeitamente estável, ou uma figura canônica
  que não deveria mudar.

O rastreamento de cena (localização/humor) e a recuperação de memória rodam em
ambos os modos.
