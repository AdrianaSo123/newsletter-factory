"""Generate a newsletter and export an email-friendly HTML + .eml draft.

Usage:
  cd ".../newsletter factory" && ./.venv/bin/python scripts/export_email_draft.py

Outputs:
- ai_newsletter_real_data.md
- ai_newsletter_real_data.html
- ai_newsletter_real_data.eml
"""

from __future__ import annotations

from datetime import datetime
import os
import sys

# Ensure the project root is on sys.path when executed as a file.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from example_real_data import create_newsletter_with_real_data
from renderers.email_renderer import EmailRenderOptions, render_newsletter_email_html, export_eml_bytes


def main() -> int:
    newsletter_md = create_newsletter_with_real_data()

    stamp = datetime.now().strftime("%Y-%m-%d")
    subject = f"AI Investment Weekly — {stamp}"

    options = EmailRenderOptions(
        subject=subject,
        brand_name="AI Investment Weekly",
        preheader="Who invested in whom + upcoming AI events (with sources).",
    )

    md_path = "ai_newsletter_real_data.md"
    html_path = "ai_newsletter_real_data.html"
    eml_path = "ai_newsletter_real_data.eml"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(newsletter_md)

    html = render_newsletter_email_html(newsletter_markdown=newsletter_md, options=options)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    eml_bytes = export_eml_bytes(newsletter_markdown=newsletter_md, options=options)
    with open(eml_path, "wb") as f:
        f.write(eml_bytes)

    print(f"Wrote {md_path}")
    print(f"Wrote {html_path}")
    print(f"Wrote {eml_path}")
    print("Tip: open the .eml in Apple Mail or Gmail (import) to preview.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
