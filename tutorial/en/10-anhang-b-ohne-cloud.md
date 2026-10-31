# Appendix B — The same game without the cloud

*[Deutsche Fassung](../de/10-anhang-b-ohne-cloud.md) · Translated from the German original.*

![Queeny, seen from behind over her shoulder, sits at a desk at night in front
of a laptop; the game board with worker ants and apples glows on the screen, a
cable leads to the wall socket, next to it a desk lamp, outside the window
clouds drift by](../bilder/anhang-b-titel.png)

*The same game, but this time on your own machine.*

Since version 0.35, **Ollama** runs decision models on your own machine and
answers decision questions in the same format as TypeSafe: the same path
`/v1/systemone`, the same question types `choice`, `noul` and `score`, the same
`criteria`, and `probabilities`, `confidence` and `usage` in the answer. The
announcement says so openly — the interface is “based on TypeSafe's Jev API”.

For this game that means: it runs **without a key, without cost and without a
network**. And without changing one line of code.

## Setting up

```sh
ollama pull nimble
```

At the launch there were three models: `nimble` (9B), `tev1` (4B) and
`tev1:0.8b`. All three are still there. By now the choice is larger: at the
end of October 2026,
[ollama.com/search?c=decision](https://ollama.com/search?c=decision) lists
twelve decision models, among them:

| Model | Size on disk | Note |
|---|---|---|
| `nimble` | 9.3 GB (9B) | measured here, Apache 2.0 |
| `kev` | 6.7 GB (9B) | measured here, Apache 2.0, Ollama 0.40.4 or later |
| `strands-decider` | 2.0 GB (2B) | measured here, Apache 2.0, Apple Silicon only |
| `nimble-v3` | 9.3 GB (9B) | successor to nimble, **non-commercial** only (CC BY-NC 4.0) |
| `tev1` | 4.5 GB (4B), 0.8 GB (0.8B) | answers with a context of only about 2,000 tokens |
| `d3` | 3 to 30 GB (2B to 27B) | Ollama 0.40.9 or later, understands images too |

Then in `.env`:

```
TYPESAFE_API_KEY=ollama
TYPESAFE_BASE_URL=http://localhost:11434
TYPESAFE_DEFAULT_MODEL=nimble
```

That is all. The `typesafe-sdk` reads both addresses from the environment
(`TYPESAFE_BASE_URL` and `TYPESAFE_DEFAULT_MODEL`), and Ollama needs no key —
the field just must not be empty. Another model is another
`TYPESAFE_DEFAULT_MODEL` line.

This is where something that was only a sentence in chapter 2 pays off: that
the base URL can be configured.

> **Pitfall.** The base must **not** contain `/v1`. The SDK appends
> `/v1/systemone` itself, and `…:11434/v1` turns into `…/v1/v1/systemone`. The
> error message is then `404 page not found` and looks as if the model were
> missing. Correct is `http://localhost:11434`.

I measured on an Apple M4 with 32 GB and Ollama 0.40.13. There Ollama runs the
three models through MLX on the GPU.

## Does it answer usefully?

An ant that sees a fruit two squares to the north-east:

| | nimble | kev | strands-decider |
|---|---|---|---|
| Chosen | `north-east` | `north-east` | `north-east` |
| Confidence | **0.99** | 0.78 | 0.75 |
| Input tokens | 328 | 128 | 196 |
| first call (model is loaded) | 3.8–8.8 s | 4.7 s | 1.9 s |
| after that, median | **1.4–2.8 s** | 1.2 s | **0.4 s** |

All three choose correctly. nimble is the most decisive, but also the slowest.

In the cloud I measured about 600 ms for a request. So locally only the
smallest model is faster.

## The number that fooled me at first

An earlier version of this appendix gave **163 ms** for nimble. Today I measure
the same thing again, five times the same request in a row:

```
same request:       6918, 5, 4, 4, 4, 5 ms
different requests: 4242, 2582, 2440, 2888, 2644, 2377 ms
```

After the first call the same request comes back in 4 ms. That is not
computing time, that is a **cache**: Ollama remembers the answer to a prompt it
has seen before. So five times the same request measures nothing.

The same trap is there with eight ants at once:

```
8 identical requests:      2.7 s
8 different requests:     22.7 s
8 different, once more:   22.4 s
```

Eight different ones take about eight times as long as one. Eight different
prompts need eight computations of their own, and a machine with one GPU works
through them practically one after the other. A service on the network has
many.

From this follows something that could not have been said like this in
chapter 3:

> `asyncio.gather` pays off against a **remote** service and brings **almost
> nothing locally**. The same line of code, opposite benefit — depending on
> whether the waiting is network or computation.

So when measuring locally, always use requests that differ. In the game that
happens by itself, because every ant stands somewhere else.

## A whole level

The same board and the same order as in chapter 8, “Fan out and search, and
carry what you find straight home.”, three runs each, at most 60 rounds:

| | Jev (cloud, chapter 8) | nimble | kev | strands-decider |
|---|---|---|---|---|
| Rounds to five fruits | 23 · 26 · 59 | **19 · 22 · 23** | not made | not made |
| discarded answers | 36–47 % | 28–41 % | 100 % | 100 % |
| one round with eight ants, median | 0.6 s | **11–18 s** | — | — |
| a whole game | under a minute | **5–6 minutes** | — | — |
| cost of the game | ~$0.005 | **0** | 0 | 0 |
| key needed | yes | no | no | no |

**nimble plays as well as Jev.** Three runs are too few to say it is better.
But it is not worse. The price is time: locally a round takes twenty to thirty
times as long.

**kev and strands-decider do not get out of the nest.** In the nest an ant only
sees the other ants. Both models answer that indecisively: kev with a
confidence of at most 0.18, strands-decider with 0.02 to 0.07. Both are below
the threshold of 0.22 from chapter 5, so every answer is thrown away, and no
ant moves.

And because nothing in the nest changes then, the question does not change
either: the models run at temperature 0, every round brings the same answer,
and the colony is stuck for good.

### Tip: the threshold belongs to the model

The 0.22 was measured with Jev. Confidence is calibrated differently in every
model, and a threshold that suits one model can paralyse another completely.
Whoever changes the model has to measure the threshold again.

## What this cannot do

**The version on Streamlit's cloud.** No Ollama runs there, and `localhost`
points to Streamlit's server. Whoever offers the game on the web still needs a
key — the local way is the one for your own machine.

**A small machine.** nimble wants 9.3 GB loaded and held in memory. The small
models would be fast enough, but they do not play with the threshold from
chapter 5.

## Try it

* Start small: change `.env` and press “Next round” once. That it works at all,
  without you touching one line of code, is the real point of this appendix.
* Compare the confidences. Put one ant next to a fruit and one into empty
  space — where do cloud and local differ, and where not?
* Set `"ants"` in `level1.json` to 3 and play locally. A round gets three times
  faster, the game slower going. Which trade do you prefer?
* Take `kev` and lower `MIN_CONFIDENCE` to 0.1. Does the colony get out of the
  nest now? And what is an answer with 0.1 confidence still worth?
