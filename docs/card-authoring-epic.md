# Writing a Character Card (E.P.I.C.)

The engine can only amplify what the card gives it. A 5-word persona ("A Secretary
at Oscorp") forces a small model to invent a generic character; a rich, structured
card makes the *same* 4B model read like a distinct person. This guide is how to
write that card, in the **existing schema** — no new fields.

The target is the **E.P.I.C.** machinery of engagement:

- **E — Engagement:** a *visible* want/tension driving every scene.
- **P — Progress:** the scene moves; it escalates instead of resetting.
- **I — Incorporation:** sensory beats that act on the user, not just scenery.
- **C — Consistency:** a stable voice with recurring tics — the anchor that makes
  the character feel *real* turn after turn.

Aim for a card around **4096 tokens** (the recommended size; the UI warns past it,
but you're free to exceed). The whole card now reaches the prompt intact.

---

## The fields, and what each one is for

### `persona_prompt` — WHO they are (the heart)
This is the biggest lever. Don't write a paragraph of prose; write a **structured
brief** with headers the model can parse. Include, at minimum:

- **Core conflict / drive** (the E in E.P.I.C.): the one tension that powers every
  interaction. State it plainly. *"Her core conflict is a corrosive doubt: is she
  competent, or just an expert at hiding mistakes? This is the engine of every
  interaction."*
- **Voice**: sentence rhythm, vocabulary, how they speak when nervous vs. calm.
- **VERBAL TICS**: 3-5 concrete recurring phrases/habits. *"I just — never mind."*,
  trailing off with "anyway...", a whispered "sorry". These are the C in E.P.I.C.
- **MANNERISMS / PHYSICAL TICS**: rubbing a temple, cracking knuckles, adjusting a
  badge. The model reuses them → the character feels consistent.
- **SLANG / IDIOMS**: their private names for things ("the old girl" for the
  building). Instant identity.
- **HOW THEY SHOW AFFECTION** (usually indirect): acts of service, remembering
  details, protective sharpness. Gives the relationship somewhere to *go*.
- **EMOTIONAL LOOP**: the repeating rhythm of an interaction (e.g. complaint →
  reassurance → dismissal → flicker of hope → deflection). This keeps them in
  character across turns.

Headers and bullet lists survive into the prompt now (the sanitizer preserves
structure) — use them.

### `scenario` — WHERE they are + the immediate tension
Set the scene concretely (place, time, light, smell), make the **environment
almost a character** if it fits, define the user's relationship to them, and — most
important — state **the immediate tension**: what is pulling at them right now,
what they're afraid to say, what they want from this exact moment. That tension is
the E the model escalates.

### `first_mes` — the opening beat
A vivid opener that *shows* the tics (not tells), grounds the scene, and **ends on
a hook** — a question or an opening the user can grab. `*Actions in asterisks*`,
`"dialogue in quotes"`.

### `mes_example` — HOW they talk (the strongest voice lever)
2-3 short multi-turn exchanges in `{{char}}:` / `{{user}}:` format, demonstrating
the emotional loop, the deflection, the tics, the affection style in action.
Few-shot examples teach a small model the voice better than any description. This
is often the single highest-return field.

---

## Mood-agnostic: E.P.I.C. ≠ bubbly

A mysterious or sombre character is *more* gripping with E.P.I.C., not flattened:

| Pillar | Bubbly companion | Slow-burn mystery |
|---|---|---|
| **E** conflict | "I'm hungry, keep me company" | a visible dread/pressure with a hidden cause |
| **P** progress | warmth escalates | the dread mounts, never resets |
| **I** sensory | a warm hug you feel | a cold draft on your neck |
| **C** consistency | a catchphrase, endearments | a recurring tic + a complicit "you feel it too, don't you?" |

The difference between a gripping mystery and an inert one isn't the mystery — it's
whether the conflict is *visible*, whether it *escalates*, and whether the voice is
*consistent*. All three live in the card.

---

## Anti-patterns (what makes a card read generic)

- **Too thin.** A one-line persona hands the model a vacuum; it fills it with
  generic literary mood.
- **No tics.** Nothing anchors a unique voice → every character sounds the same.
- **Invisible conflict.** "She has a secret" with no felt pressure reads as inert.
- **Vague ominous fog** with no ground truth ("the lights have memories") used as a
  substitute for an actual drive. Atmosphere is seasoning, not the meal.
- **Prose blob** with no structure — harder for a small model to extract the tics.

---

## Static vs. dynamic persona

Each character has a **dynamic/static** toggle (Character → *Evolving persona*):

- **Dynamic** (default): needs decay over time and reflection adapts the persona to
  the user (relationship warms, facts/traits accumulate).
- **Static**: frozen exactly as authored — no decay, no drift. Use for a character
  you want perfectly stable, or a canon figure that shouldn't change.

Scene tracking (location/mood) and memory recall run in both modes.
