"""Unit tests for server_utils module."""

from __future__ import annotations

import textwrap
from typing import Final

import pytest
import trio

from character_sim.llm_request import fake_stream
from character_sim.server import format_stream

RESPONSE: Final = """

My heart hammered against my ribs, a frantic drumbeat drowning out the murmurs of the other students. The air in the summoning hall was thick with the scent of ozone and excitement. One by one, my classmates called forth their magnificent companions. A phoenix of living flame, a griffin with wings like storm clouds, a tiny, iridescent dragon that curled around its summoner's shoulder. Each success was a fresh wound, a silent accusation of my inadequacy.

Then it was my turn. I stepped into the circle, the chalk lines cold beneath my feet. I focused, pouring every ounce of my will into the spell, the words tasting like ash in my mouth. The sigils flared… and then sputtered, dying into a dull, black smudge. A wave of heatless failure washed over me, and I felt the familiar, crushing weight of Kailen's sneer from the back of the room. *Weak witch.*

Humiliation burned my cheeks. I squeezed my eyes shut, wishing the stone floor would swallow me whole. But then, a sensation cut through the shame. The darkness from my failed circle didn't just fade; it *pooled*, thick and velvety. It wasn't the absence of light, but a presence of its own.

A low hum began, vibrating up through the soles of my boots. From the center of the blackened circle, a light emerged. But it was unlike any light I'd ever seen. It wasn't the bright gold of a griffin or the fiery orange of a fox. It was a pure, white luminescence, soft and cool, like moonlight on fresh snow. It didn't blind; it illuminated, casting long, gentle shadows.

The students in the hall fell silent, their earlier bravado replaced by a collective, breathless awe. Even Professor Elara, who had been watching with a stern, evaluating gaze, leaned forward, her eyes wide.

The white glow coalesced, rising like a gentle mist. And from it, it emerged.

It was a creature of impossible grace. It had the general form of a large feline, but its body seemed woven from starlight and shadow. Its fur was the deep black of the night sky, pricked with tiny, shimmering points of light that moved and swirled like constellations. It moved with a silent, fluid elegance, each paw making no sound on the polished floor. Its eyes, when they opened, were not animalistic, but pools of that same serene white light, ancient and intelligent.

It wasn't any creature from the academy's bestiary. It was something… else. Something new.

The creature turned its luminous gaze from me to the watching crowd, and a low, melodic sound resonated in the air—not a growl, not a purr, but a soft, chiming vibration that seemed to speak directly to the soul. It was a sound that held both a profound welcome and a quiet, undeniable power.

I stood frozen, my own magical failure forgotten. The whispers of the other students, the weight of Kailen's contempt, it all faded into insignificance. Before me stood a mystery, a silent promise that perhaps, just perhaps, my path at the Academy of Astral Magic was not written in the textbooks after all. My familiar had not failed to appear. It had simply chosen to arrive in a way that defied all expectations. And as it looked back at me, I felt, for the first time since the breakup, a flicker of something other than fear. I felt wonder."""


def wordwrap_lines(string: str, width: int) -> str:
    """Return paragraphs from word wrapping string.

    Mostly copied from how the internals of jinja2's `wordwrap` filter
    works found here:
    https://github.com/pallets/jinja/blob/5ef70112a1ff19c05324ff889dd30405b1002044/src/jinja2/filters.py#L956

    which is licenced under the BSD-3-Clause License.
    """
    return "\n".join(
        "\n".join(
            textwrap.wrap(
                line,
                width=width,
                expand_tabs=False,
                replace_whitespace=False,
                break_long_words=True,
                break_on_hyphens=True,
            ),
        )
        for line in string.splitlines()
    )


@pytest.mark.trio
async def test_format_stream() -> None:
    text = ""
    stream_ctx = format_stream(fake_stream(RESPONSE))
    async with stream_ctx as stream:
        async for fragment in stream:
            text += fragment
    real = wordwrap_lines(RESPONSE[2:], 79)
    ##for line, real_line in zip(text.splitlines(), real.splitlines()):
    ##    if line != real_line:
    ##        print("difference:")
    ##        print(repr(line))
    ##        print(repr(real_line))
    ##        print()
    assert text == real


@pytest.mark.trio
async def test_format_stream_no_wordwrap() -> None:
    text = ""
    stream_ctx = format_stream(fake_stream(RESPONSE), None)
    async with stream_ctx as stream:
        async for fragment in stream:
            text += fragment
    assert text == RESPONSE.lstrip()


if __name__ == "__main__":
    trio.run(test_format_stream)
