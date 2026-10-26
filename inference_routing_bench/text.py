"""Deterministic filler text for prompts.

The benchmark measures routing, not language, so prompts only need two properties: the same seed always gives the
same words, and the words tokenize predictably. Every word below is a common lower-case English word that the
Qwen and Llama tokenizers encode as a single token after a space, so a prompt of n words is close to n tokens.
"""
from __future__ import annotations

import random

VOCABULARY = tuple("""
able about above across after again against ahead air all almost along also always among and another answer any
area around ask away back base be because been before begin being below best better between big both bring build
business but by call can care carry case cause change check city clear close come common could country course cover
cut data day deal decide deep different do down draw drive during each early east easy end enough even ever every
eye face fact fall family far fast few field find fine fire first follow food for force form free friend from front
full game general give go good great green ground group grow hand happen hard have head hear help here high hold home
hope hour house idea important in increase inside into issue job just keep kind know land large last late lead learn
leave left less let level life light like line list little live local long look low main make many mark matter may
mean measure meet member might mind model money month more most move much must name near need never new next night
note now number of off offer often old on once only open or order other our out over own page part pass past pay
people place plan play point policy power present price problem process produce program public put question quick
rather reach read ready real reason record report rest result return right rise road room rule run same say school
second see seem sell send serve service set short show side simple since small social some sound space speak special
stand start state step still stop story strong study such support sure system table take talk team tell term test
than that the then there these thing think this those through time today together top toward town trade travel true
try turn under unit until up upon use value very view wait walk want watch water way week well west what when where
which while white whole why wide will with within without word work world write year yes yet young
""".split())


def words(rng: random.Random, n: int) -> str:
    """n words drawn from VOCABULARY with rng; the same rng state always gives the same text."""
    if n < 0:
        raise ValueError("word count must be >= 0")
    return " ".join(rng.choice(VOCABULARY) for _ in range(n))


def count(text: str) -> int:
    """Words in text, the unit traces use for prompt sizes (about one token each with this vocabulary)."""
    return len(text.split())
