"""Frontend tests for the Churros page (Render DB admin controls)."""
import pytest
from streamlit.testing.v1 import AppTest


class TestChurros:
    def _run(self):
        at = AppTest.from_file("pages/99_Churros.py", default_timeout=15)
        at.run()
        return at

    def test_loads_without_error(self):
        at = self._run()
        # The page may show errors due to secrets structure mismatch,
        # but it should not raise an unhandled exception.
        assert not at.exception, f"Page crashed: {at.exception}"

    def test_shows_title(self):
        at = self._run()
        assert any("Admin" in t.value for t in at.title)

    def test_has_password_form(self):
        """The auth gate should show a password text_input."""
        at = self._run()
        # The page shows a text_input inside a form for the admin password.
        # AppTest text_input elements may not expose a 'type' property,
        # so just check that a text_input exists (the only one on the
        # unauthenticated page is the password field).
        assert len(at.text_input) >= 1, (
            "Expected a password text_input in the auth form"
        )

    def test_has_form_submit(self):
        """The auth form should have a submit button."""
        at = self._run()
        # The page uses st.form with a form_submit_button
        buttons = [b.label for b in at.button]
        assert any("Unlock" in label for label in buttons), (
            "Expected an 'Unlock' submit button in the auth form"
        )


# ── render_admin unit tests ──────────────────────────────────────────
# These cover the Render DB recreate flow's failure modes directly,
# without going through AppTest.

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from render_admin import (  # noqa: E402
    RenderClient,
    RenderConfig,
    RenderError,
    normalize_postgres_id,
)


class _FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text
        self.ok = 200 <= status_code < 300

    def json(self):
        return json.loads(self.text) if self.text else {}


def _client(**overrides) -> RenderClient:
    cfg = RenderConfig(
        api_key="rnd_test",
        owner_id="tea_test",
        postgres_id=overrides.get("postgres_id", "dpg-abc123def456"),
        service_id="srv-test",
        db_name="test-db",
    )
    return RenderClient(cfg)


def _stub(client: RenderClient, response: _FakeResponse, calls: list):
    def fake_request(method, url, **kw):
        calls.append((method, url))
        return response

    client.s.request = fake_request


class TestNormalizePostgresId:
    """The API resource id is `dpg-xxxx`; `-a` and the region host belong
    to the *hostname*. Pasting a connection-string host into the
    postgres_id secret 404s every API call."""

    def test_strips_internal_hostname_suffix(self):
        assert normalize_postgres_id("dpg-da993r142hec73f5961g-a") == (
            "dpg-da993r142hec73f5961g"
        )

    def test_strips_full_external_hostname(self):
        raw = "dpg-da993r142hec73f5961g-a.frankfurt-postgres.render.com"
        assert normalize_postgres_id(raw) == "dpg-da993r142hec73f5961g"

    def test_leaves_a_bare_resource_id_untouched(self):
        assert normalize_postgres_id("dpg-da993r142hec73f5961g") == (
            "dpg-da993r142hec73f5961g"
        )

    def test_tolerates_surrounding_whitespace(self):
        assert normalize_postgres_id("  dpg-abc123-a  ") == "dpg-abc123"

    def test_passes_through_unrecognised_values(self):
        """Don't silently mangle something we don't understand — let the
        API return a real error instead."""
        assert normalize_postgres_id("not-an-id") == "not-an-id"


class TestRenderConfigNormalisation:
    def test_config_normalises_postgres_id_on_construction(self):
        cfg = RenderConfig(
            api_key="k",
            owner_id="o",
            postgres_id="dpg-da993r142hec73f5961g-a",
            service_id="s",
            db_name="d",
        )
        assert cfg.postgres_id == "dpg-da993r142hec73f5961g"


class TestDeletePostgresIdempotency:
    """Step 1 of the recreate flow. An expired free database is reaped by
    Render automatically, so 'already absent' is the desired end state of
    a delete — not a failure that should abort the recreate."""

    def test_404_is_treated_as_already_deleted(self):
        client = _client()
        calls: list = []
        _stub(client, _FakeResponse(404, '{"message":"not found: dpg-x"}'), calls)

        assert client.delete_postgres("dpg-abc123def456") is False
        assert calls == [("DELETE", "https://api.render.com/v1/postgres/dpg-abc123def456")]

    def test_successful_delete_reports_true(self):
        client = _client()
        calls: list = []
        _stub(client, _FakeResponse(204), calls)

        assert client.delete_postgres("dpg-abc123def456") is True

    def test_server_error_still_raises(self):
        """The 404 tolerance must not swallow genuine failures."""
        client = _client()
        calls: list = []
        _stub(client, _FakeResponse(500, "internal error"), calls)

        with pytest.raises(RenderError):
            client.delete_postgres("dpg-abc123def456")

    def test_auth_failure_still_raises(self):
        client = _client()
        calls: list = []
        _stub(client, _FakeResponse(401, "unauthorized"), calls)

        with pytest.raises(RenderError):
            client.delete_postgres("dpg-abc123def456")


class TestRenderErrorStatusCode:
    def test_error_carries_the_http_status(self):
        client = _client()
        calls: list = []
        _stub(client, _FakeResponse(503, "unavailable"), calls)

        with pytest.raises(RenderError) as excinfo:
            client.get_postgres("dpg-abc123def456")
        assert excinfo.value.status_code == 503
