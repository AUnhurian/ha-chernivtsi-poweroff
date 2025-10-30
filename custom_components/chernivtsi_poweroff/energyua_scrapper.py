"""Scraper for Chernivtsi oblenergo shutdowns page.

The page `https://oblenergo.cv.ua/shutdowns/` contains per-group schedules in
containers like `<div id="inf{group}" data-id="{group}">`. Inside each
container there are 24 hour cells for today and (optionally) for tomorrow that
show legend letters:
  - "В" (off), "З" (on), "МЗ" (possible on).

We collect contiguous periods for OFF ("В") to build calendar events and also
collect POSSIBLE ON ("МЗ") periods to expose a third sensor state.
"""

import re

import aiohttp
from bs4 import BeautifulSoup

from .const import PowerOffGroup, STATE_OFF, STATE_POSSIBLE_ON
from .entities import PowerOffPeriod

URL = "https://oblenergo.cv.ua/shutdowns/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

class EnergyUaScrapper:
    """Scrape OFF and POSSIBLE ON periods for a selected group."""

    def __init__(self, group: PowerOffGroup) -> None:
        """Initialize the EnergyUaScrapper object."""
        self.group = group

    async def validate(self) -> bool:
        async with (
            aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session,
            session.get(URL) as response,
        ):
            if response.status != 200:
                return False
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")
            container = soup.select_one(f"div#inf{self.group}[data-id='{self.group}']")
            return container is not None

    @staticmethod
    def merge_periods(periods: list[PowerOffPeriod]) -> list[PowerOffPeriod]:
        if not periods:
            return []

        periods.sort(key=lambda x: x.start)

        merged_periods = [periods[0]]
        for current in periods[1:]:
            last = merged_periods[-1]
            if current.start <= last.end:  # Overlapping or contiguous periods
                last.end = max(last.end, current.end)
                continue
            merged_periods.append(current)

        return merged_periods

    async def get_power_off_periods(self) -> list[PowerOffPeriod]:
        async with (
            aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session,
            session.get(URL) as response,
        ):
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")

        container = soup.select_one(f"div#inf{self.group}[data-id='{self.group}']")
        if container is None:
            return []

        # Extract sequence of 24 symbols per day (today first, then tomorrow if present)
        tokens = self._extract_tokens(container)
        results: list[PowerOffPeriod] = []
        for day_idx, day_tokens in enumerate(tokens):
            periods_off = self._tokens_to_periods(day_tokens, target="В")
            results += [PowerOffPeriod(s, e, today=(day_idx == 0), state=STATE_OFF) for s, e in periods_off]
            periods_possible = self._tokens_to_periods(day_tokens, target="МЗ")
            results += [PowerOffPeriod(s, e, today=(day_idx == 0), state=STATE_POSSIBLE_ON) for s, e in periods_possible]

        return results

    def _extract_tokens(self, container: BeautifulSoup) -> list[list[str]]:
        """Extract per-hour tokens from the group's container.

        Heuristic: scan all descendants and collect text nodes that are exactly one
        of {"В", "З", "МЗ"}. The first 24 belong to today, the next 24 (if any)
        belong to tomorrow.
        """
        raw = []
        for el in container.find_all(True):
            text = (el.get_text(strip=True) or "").upper()
            if text not in {"В", "З", "МЗ"}:
                # On the site letters can be implicit via tag name: <u>=З, <s>=МЗ, <o>=В
                tag = el.name.lower() if hasattr(el, "name") and el.name else ""
                if tag == "u":
                    text = "З"
                elif tag == "s":
                    text = "МЗ"
                elif tag == "o":
                    text = "В"
            if text in {"В", "З", "МЗ"}:
                raw.append(text)

        # chunk into days by 48 half-hour slots
        days: list[list[str]] = []
        while raw:
            days.append(raw[:48])
            raw = raw[48:]
            if len(days[-1]) < 48:
                # pad if fewer cells found to avoid index errors
                days[-1] += ["З"] * (48 - len(days[-1]))
            if len(days) == 2:
                break
        if not days:
            days = [["З"] * 48]
        return days

    def _tokens_to_periods(self, tokens: list[str], target: str) -> list[tuple[int, int]]:
        """Convert sequence of 48 half-hour tokens to minute-based periods for a token."""
        periods: list[tuple[int, int]] = []
        start_slot: int | None = None
        for slot in range(48):
            if tokens[slot] == target and start_slot is None:
                start_slot = slot
            end_of_run = start_slot is not None and (slot == 47 or tokens[slot + 1] != target)
            if end_of_run and start_slot is not None:
                start_min = start_slot * 30
                end_min = (slot + 1) * 30
                periods.append((start_min, end_min))
                start_slot = None
        return periods
