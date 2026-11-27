import string

import pytest

import apex_client
import commands
import templates


@pytest.fixture
def api(monkeypatch, rotation):
    monkeypatch.setattr(apex_client, "fetch_rotation", lambda: rotation)
    return rotation


def test_parse_command():
    assert commands.parse_command("/ranked") == "ranked"
    assert commands.parse_command("/Ranked@MyBot extra") == "ranked"
    assert commands.parse_command("hello") is None
    assert commands.parse_command(None) is None


def test_start():
    reply = commands.build_reply("start")
    assert reply.text == templates.render("start")
    assert reply.photo_url is None


def test_ranked(api):
    reply = commands.build_reply("ranked")
    assert reply.text == (
        "<b>Ranked</b>\n\nCurrent map: <b>E-District</b>\n\n"
        "Changes to <b>Broken Moon</b> in: <i>00:29:51</i>"
    )
    assert reply.photo_url == "https://apexlegendsstatus.com/assets/maps/E-District.png"


def test_pubs(api):
    reply = commands.build_reply("pubs")
    assert "Current map: <b>Broken Moon</b>" in reply.text
    assert "Changes to <b>Storm Point</b> in: <i>00:29:51</i>" in reply.text


def test_mixtape(api):
    reply = commands.build_reply("mixtape")
    assert "Mode: <b>Control</b>" in reply.text and "Map: <b>Barometer</b>" in reply.text
    assert "Changes to <b>Gun Run</b> on <b>Wattson&#x27;s Pylon</b> in: <i>00:14:51</i>" in reply.text


def test_wildcard_event(api):
    reply = commands.build_reply("wildcard")
    assert "Event: <b>Godzilla Attacks</b>" in reply.text
    assert "Map: <b>Storm Point</b>" in reply.text
    assert "<i>5 days 15 hours and 29 minutes</i>" in reply.text
    assert "135:29:51" not in reply.text
    assert "Olympus" not in reply.text


def test_wildcard_regular(api):
    api["wildcard"]["current"]["eventName"] = "Wildcard"
    reply = commands.build_reply("wildcard")
    assert "Godzilla" not in reply.text
    assert "Changes to <b>Olympus</b> in: <i>135:29:51</i>" in reply.text
    assert reply.text == templates.render("wildcard", **commands._rotation_context(api["wildcard"]))


def test_unknown_command():
    assert commands.build_reply("nope").text == templates.render("unknown_command")


def test_api_error(monkeypatch):
    def boom():
        raise apex_client.ApexApiError("down")

    monkeypatch.setattr(apex_client, "fetch_rotation", boom)
    assert commands.build_reply("ranked").text == templates.render("api_error")


def test_template_placeholders_are_provided(rotation):
    provided = set(commands._rotation_context(rotation["ranked"]))
    for key, text in templates.load()["messages"].items():
        used = {f for _, f, _, _ in string.Formatter().parse(text) if f}
        assert used <= provided, f"{key} uses unknown placeholders {used - provided}"


def test_every_command_has_description():
    assert set(templates.command_descriptions()) == set(commands.COMMANDS)
