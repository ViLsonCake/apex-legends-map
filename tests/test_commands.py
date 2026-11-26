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
    assert "E-District" in reply.text
    assert "00:29:51" in reply.text
    assert "03:00 UTC, Nov 26" in reply.text
    assert "Broken Moon" in reply.text and "4h 30m" in reply.text
    assert reply.photo_url == "https://apexlegendsstatus.com/assets/maps/E-District.png"


def test_pubs(api):
    reply = commands.build_reply("pubs")
    assert "Broken Moon" in reply.text and "Storm Point" in reply.text
    assert "00:29:51" in reply.text and "1h 30m" in reply.text


def test_mixtape(api):
    reply = commands.build_reply("mixtape")
    assert "Control" in reply.text and "Barometer" in reply.text
    assert "Gun Run" in reply.text and "Wattson&#x27;s Pylon" in reply.text
    assert "00:14:51" in reply.text


def test_wildcard_event(api):
    reply = commands.build_reply("wildcard")
    assert reply.text == templates.render("wildcard_event", **commands._rotation_context(api["wildcard"]))
    assert "Godzilla Attacks" in reply.text
    assert "Storm Point" in reply.text
    assert "135:29:51" in reply.text
    assert "Olympus" in reply.text


def test_wildcard_regular(api):
    api["wildcard"]["current"]["eventName"] = "Wildcard"
    reply = commands.build_reply("wildcard")
    assert "Godzilla" not in reply.text
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
