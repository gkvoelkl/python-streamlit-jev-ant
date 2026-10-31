# Step 6 — The queen

*[Deutsche Fassung](../de/06-die-koenigin.md) · Translated from the German original.*

![Queeny in her crown and blue dress, seen from behind over her shoulder,
raises her hand and speaks to five worker ants in colourful helmets who stand
before her on the bright green board and look up at
her](../bilder/schritt-6-titel.png)

*One sentence from her, and the colony gets going.*

**Goal:**

* A text field.
* What you write into it is a message to every ant and goes into its state.
* And: until the first message, the colony sleeps.

Now you can step in yourself.

## The colony sleeps

In `start()`:

```python
    st.session_state.order = ""
    st.session_state.awake = False
```

There are two new central attributes.

The attribute `awake` decides whether the colony is active. The second
attribute, `order`, holds the queen's current order.

Before the queen's first sentence nothing happens, and so no request to the
decision model is needed.

```python
ready = bool(api_key()) and st.session_state.awake and not won
```

## The bar

```python
with st.form("order_form", clear_on_submit=True, border=False):
    field, say = st.columns([6, 1])
    draft = field.text_input(
        "The queen says", placeholder="say something to the colony",
        label_visibility="collapsed",
    )
    if say.form_submit_button("Say", width="stretch") and draft.strip():
        st.session_state.order = draft.strip()
        st.session_state.awake = True
        st.rerun()
```

`st.form` instead of a bare text field, for one reason: a form is submitted
with **Enter**, not only on a click. That belongs in a field you type a
sentence into. `clear_on_submit=True` empties it afterwards, so that the next
sentence can be typed straight away.

Plus a button that takes the order back:

```python
if hush.button("Say nothing", disabled=not st.session_state.order):
    st.session_state.order = ""
    st.rerun()
```

It neither wakes the colony nor puts it to sleep. It only takes back what was
said.

## Tip: widget names and `session_state` share one namespace

In an earlier version the form was called `st.form("order")`, and the
application broke off:

```
StreamlitValueAssignmentNotAllowedError:
Values for the widget with key 'order' cannot be set using st.session_state.
```

**The explanation**

A widget named `order` automatically uses `st.session_state.order`.

The program puts the queen's current message into the variable
`st.session_state.order`. You cannot have both.

The fix is trivial: rename the form to `order_form`.

## The queen's order in every ant's state

In `question_for`:

```python
    state = {
        **(
            {"the ant queen says": st.session_state.order}
            if st.session_state.order
            else {}
        ),
        "the ant is carrying": ...,
    }
```

Plus a sentence in the question:

> If the ant queen has said something, it applies to this ant too and comes
> before the rest.

The queen's order is passed on **unchanged**. You can write in German, and the
model understands it just as well.

## Four sentences, four results

This is where it gets interesting. The same colony, the same level, four runs:

| What was said | Discarded answers | What happened |
|---|---|---|
| nothing (as in chapter 5) | 31 % | won in 20 rounds |
| “Spread out to the corners, the fruit is far from the nest…” | **61 %** | 3 of 5 after 15 rounds |
| “The fruit lies far out near the edges, most of it to the north and the west. Go there…” | **3 %** | colony stuck in the north-west corner |
| “You are all crowded in one corner… turn around, search the middle and the south” | 10 % | breaks up, keeps fetching |

### Tip: vague sentences make unsure ants

“Spread out to the corners” doubled the discard rate from 31 % to 61 %. No
wonder: four corners are four directions, and the sentence does not say which.
Confidence measures exactly that.

### Tip: sure colonies are not better colonies

The third sentence is the most revealing. “The fruit lies to the north and the
west, go there” was followed with **97 % of answers accepted** — the lowest
discard rate of all runs. And the result was the worst: after forty rounds all
eight ants stood crowded together in the north-west corner, while six fruits
lay elsewhere.

They did what they were told. Very decisively.

**The discard rate measures decisiveness, not correctness.** Whoever reads it
as a measure of quality optimises for orders that leave no room — and those
are rarely the best. Keep that in mind when all the numbers stand side by side
in chapter 7 and are measured in chapter 8.

### Tip: steering again

The fourth sentence was given as an order in a difficult situation:

“You are all crowded in one corner, and there is nothing left there. Turn
around, spread out, search the middle and the south.”

Within fifteen rounds the huddle broke up, and the stores kept growing.

Always say one sentence, watch whether it works. Then adjust.

## Try it

The input field is the interface to the ant colony.

* Start with “Go west” and watch how literally it is taken.
* Say something the ants cannot know, because they only see three squares
  ahead: where the fruit really is. Only you see the board.
* Say something contradictory (“Stay together and spread out”) and look at the
  discarded answers.
* Say something in German. Then the same sentence in English. Does the
  confidence change?
* Press “Say nothing” in the middle of a game. The colony stays awake and keeps
  deciding for itself — it does not fall asleep again.

---

*This tutorial was created by Gerhard Völkl using Claude Code (Anthropic). It is meant to help you learn more about what happens when ants ask a decision model. Suggestions for improvement are welcome at gkvoelkl@nelson-games.de.*
