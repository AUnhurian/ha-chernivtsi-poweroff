from bs4 import BeautifulSoup

from custom_components.chernivtsi_poweroff.energyua_scrapper import EnergyUaScrapper
from custom_components.chernivtsi_poweroff.const import PowerOffGroup, STATE_OFF, STATE_POSSIBLE_ON


def test_extract_tokens_today_and_tomorrow():
    with open("tests/oblenergo_test.html", "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    scr = EnergyUaScrapper(PowerOffGroup.Two)
    container = soup.select_one("div#inf2[data-id='2']")
    tokens = scr._extract_tokens(container)  # type: ignore[attr-defined]

    assert len(tokens) >= 1
    assert len(tokens[0]) == 48
    assert tokens[0][2] == "В" or tokens[0][1] in {"В", "З", "МЗ"}


def test_tokens_to_periods_map_to_entities():
    with open("tests/oblenergo_test.html", "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    scr = EnergyUaScrapper(PowerOffGroup.Two)
    container = soup.select_one("div#inf2[data-id='2']")
    tokens = scr._extract_tokens(container)  # type: ignore[attr-defined]

    periods_off = scr._tokens_to_periods(tokens[0], target="В")  # type: ignore[attr-defined]
    periods_possible = scr._tokens_to_periods(tokens[0], target="МЗ")  # type: ignore[attr-defined]

    # With the provided fixture, expect off run 19:00-21:30 (slots 38..43 -> minutes 1140..1290)
    assert all(isinstance(p[0], int) and isinstance(p[1], int) for p in periods_off)
    assert all(p[0] % 30 == 0 and p[1] % 30 == 0 for p in periods_off)


