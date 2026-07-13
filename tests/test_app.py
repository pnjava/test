#!/usr/bin/env python3
"""
T5.1 + T4.2 acceptance test:
  End-to-end via Streamlit AppTest:
    - app boots without exceptions (sidebar shows knowledge gaps)
    - one known question through the chat input -> grounded answer rendered
    - citation expander(s) present, mapping the answer to visible sources

Run: .venv/bin/python tests/test_app.py    (live LLM call, ~1 min)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from streamlit.testing.v1 import AppTest


def main():
    failures = []

    at = AppTest.from_file(str(ROOT / "src" / "app.py"), default_timeout=180)
    at.run()
    if at.exception:
        print(f"✗ app failed to boot: {at.exception}")
        sys.exit(1)
    print("✓ app boots without exceptions")

    if at.sidebar and any("Knowledge gaps" in h.value for h in at.sidebar.header):
        print("✓ knowledge-gaps sidebar renders")
    else:
        failures.append("knowledge-gaps sidebar missing")

    # end-to-end: one known question
    at.chat_input[0].set_value("What technology is DG built on?").run()
    if at.exception:
        failures.append(f"exception during answer flow: {at.exception}")
    else:
        body = " ".join(md.value for md in at.markdown)
        if "universe" in body.lower():
            print("✓ grounded answer rendered (mentions UniVerse)")
        else:
            failures.append(f"expected answer not rendered; markdown={body[:300]}")

        if at.expander and any("::c" in (e.label or "") for e in at.expander):
            print(f"✓ citation expander(s) rendered: {[e.label for e in at.expander][:2]}")
        else:
            failures.append("no citation expanders rendered for grounded answer")

    if failures:
        print("\nACCEPTANCE FAILED:")
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)
    print("\nT5.1 + T4.2 ACCEPTANCE: PASSED")


if __name__ == "__main__":
    main()
