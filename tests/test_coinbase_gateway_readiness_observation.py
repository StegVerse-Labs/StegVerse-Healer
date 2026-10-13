"""Post-deploy readiness is non-gating evidence; local TLS is pinned to the adopted certificate."""
from __future__ import annotations

import http.server
import json
import shutil
import ssl
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

from app import coinbase_stegdeploy_gateway as mod


def free_port() -> int:
    import socket
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class ReadinessObservationTests(unittest.TestCase):
    def test_unreachable_readiness_is_not_observed_not_blocking(self) -> None:
        unobserved: dict[str, str] = {}
        url = f"http://127.0.0.1:{free_port()}/api/coinbase/skap/readiness"
        value = mod._observe_readiness(url, None, "LOCAL_COINBASE_READINESS_UNAVAILABLE", unobserved, "coinbase")
        self.assertIsNone(value)
        entry = unobserved["coinbase"]
        self.assertEqual(entry["consequence_observation"], "NOT_AUTHENTICALLY_OBSERVED")
        self.assertTrue(entry["reason"].startswith("LOCAL_COINBASE_READINESS_UNAVAILABLE:"))
        self.assertEqual(entry["reconciliation_entrypoint"], "GET " + url)
        self.assertIs(entry["gates_transition"], False)

    def test_execute_records_readiness_as_non_gating_evidence(self) -> None:
        source = Path(mod.__file__).read_text(encoding="utf-8")
        self.assertNotIn("_create_unverified_context", source)
        self.assertIn('"readiness_gates_transition": False', source)
        self.assertIn('"destination_liveness_is_transition_predicate": False', source)

    def test_adopted_certificate_is_required_for_tls_context(self) -> None:
        with self.assertRaisesRegex(mod.GatewayActivationError, "TLS_ADOPTED_CERTIFICATE_LOCATOR_REQUIRED"):
            mod.adopted_certificate_context(None)


@unittest.skipUnless(shutil.which("openssl"), "openssl CLI required to mint test certificates")
class AdoptedCertificatePinTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        for name in ("adopted", "other"):
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1",
                "-subj", "/CN=stegverse.org", "-keyout", str(root / f"{name}.key"),
                "-out", str(root / f"{name}.crt"),
            ], check=True, capture_output=True)
        self.root = root

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def serve(self, name: str) -> str:
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                raw = json.dumps({"state": "READY"}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def log_message(self, *_args):
                return

        server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(self.root / f"{name}.crt"), str(self.root / f"{name}.key"))
        server.socket = context.wrap_socket(server.socket, server_side=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return f"https://127.0.0.1:{server.server_address[1]}/api/coinbase/skap/readiness"

    def test_endpoint_presenting_adopted_certificate_is_observed(self) -> None:
        context = mod.adopted_certificate_context({"cert_file": self.root / "adopted.crt"})
        unobserved: dict[str, str] = {}
        value = mod._observe_readiness(self.serve("adopted"), context, "LOCAL_COINBASE_READINESS_UNAVAILABLE", unobserved, "coinbase")
        self.assertEqual(value, {"state": "READY"})
        self.assertEqual(unobserved, {})

    def test_endpoint_presenting_other_certificate_fails_closed(self) -> None:
        context = mod.adopted_certificate_context({"cert_file": self.root / "adopted.crt"})
        with self.assertRaisesRegex(mod.GatewayActivationError, "LOCAL_GATEWAY_TLS_CERTIFICATE_NOT_ADOPTED_CERTIFICATE"):
            mod._observe_readiness(self.serve("other"), context, "LOCAL_COINBASE_READINESS_UNAVAILABLE", {}, "coinbase")


if __name__ == "__main__":
    unittest.main()
