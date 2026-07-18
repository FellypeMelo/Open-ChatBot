import { test } from '@playwright/test';

// Demo capture — drives the REAL frontend. Assistant replies are scripted
// (representative), so no LLM/GPU is needed and the recording is deterministic.
const SSE = (reply: string) =>
  reply
    .split(' ')
    .map((w) => `data: ${JSON.stringify({ token: w + ' ' })}\n\n`)
    .join('') + 'data: {"done": true}\n\n';

test('OpenChatBot — persistent memory demo', async ({ page }) => {
  // Art direction: hide the behavioral-state panel (energy/hunger/etc.) so the
  // capture focuses on the chat + memory recall. Injected before app scripts.
  await page.addInitScript(() => {
    const style = document.createElement('style');
    style.textContent =
      'div[class*="grid-cols-5"]{display:none!important}';
    document.documentElement.appendChild(style);
  });

  let step = 0;
  const replies = [
    'Memorizado. Projeto Aurora — stack PostgreSQL e Neo4j. Guardado na memoria de longo prazo.',
    'Rapido: REST usa HTTP e JSON, simples de cachear; gRPC usa HTTP/2 e protobuf, melhor para baixa latencia entre servicos.',
    'Seu projeto Aurora usa PostgreSQL (relacional) e Neo4j (grafo) — recuperado da memoria vetorial, sem voce repetir.',
  ];
  await page.route('**/chat/stream', async (route) => {
    const reply = replies[Math.min(step, replies.length - 1)];
    step++;
    await route.fulfill({
      status: 200,
      headers: { 'content-type': 'text/event-stream' },
      body: SSE(reply),
    });
  });

  await page.goto('/');
  await page.waitForTimeout(900);

  // Create a neutral technical agent
  await page.click('button:has-text("Characters")');
  await page.click('button:has-text("Initialize Persona")');
  await page.fill('#char_name', 'Atlas');
  await page.fill('#char_description', 'Assistente tecnico com memoria persistente (RAG).');
  await page.click('button[type="submit"]:has-text("Initialize")');
  await page.waitForTimeout(600);

  await page.click('button:has-text("Chat")');
  const box = page.locator('textarea');
  await box.waitFor();
  await page.waitForTimeout(500);

  const send = async (text: string, wait = 2400) => {
    await box.click();
    await box.type(text, { delay: 26 });
    await page.waitForTimeout(350);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(wait);
  };

  await send('Guarde: meu projeto se chama Aurora e usa PostgreSQL + Neo4j.');
  await send('Enquanto isso, REST vs gRPC em uma frase?');
  await send('Sem eu repetir: qual banco o meu projeto usa?', 3200);

  await page.waitForTimeout(1200);
});
