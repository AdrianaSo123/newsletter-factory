"""Email-friendly newsletter rendering.

This project generates newsletters as Markdown. For distribution, email is often
more user-friendly than raw Markdown.

This module:
- Converts Markdown -> HTML when `markdown` is available
- Falls back to a safe `<pre>` HTML view if `markdown` isn't installed
- Builds an `.eml` draft using the Python stdlib email package

No external network calls are made here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from email.utils import formatdate
from html import escape
from typing import Optional


@dataclass(frozen=True)
class EmailRenderOptions:
    subject: str
    from_addr: str = "newsletter@example.com"
    to_addr: str = "reader@example.com"
    preheader: str = "Weekly AI investments + events, grounded with sources."
    brand_name: str = "AI Investment Weekly"
    footer_text: str = "You’re receiving this because you subscribed to AI Investment Weekly."


def _markdown_to_html(markdown_text: str) -> str:
    """Convert Markdown to HTML.

    Uses `markdown` (Python-Markdown) if installed; otherwise falls back to `<pre>`.
    """
    markdown_text = markdown_text or ""

    try:
        import markdown as md  # type: ignore

        return md.markdown(
            markdown_text,
            extensions=[
                "extra",
                "sane_lists",
                "tables",
            ],
            output_format="html5",
        )
    except Exception:
        # Safe fallback: preserve content without trying to be clever.
        return "<pre style=\"white-space:pre-wrap;font-family:ui-monospace,Menlo,Consolas,monospace\">" + escape(markdown_text) + "</pre>"


def render_newsletter_email_html(
    *,
    newsletter_markdown: str,
    options: EmailRenderOptions,
    generated_at: Optional[datetime] = None,
) -> str:
    """Render full HTML email body from the newsletter Markdown."""

    generated_at = generated_at or datetime.now()
    body_html = _markdown_to_html(newsletter_markdown)

    # Basic, email-safe styling. Keep it simple (many clients strip modern CSS).
    css = """
    body{margin:0;padding:0;background:#f6f7fb;color:#111827;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;}
    .container{max-width:720px;margin:0 auto;padding:24px;}
    .card{background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;}
    .header{padding:18px 20px;border-bottom:1px solid #e5e7eb;background:#0b1220;color:#ffffff;}
    .header .brand{font-size:16px;font-weight:700;letter-spacing:.2px;}
    .header .meta{font-size:12px;opacity:.85;margin-top:4px;}
    .content{padding:20px;}
    .content h1{font-size:22px;margin:0 0 12px;}
    .content h2{font-size:18px;margin:22px 0 10px;}
    .content h3{font-size:15px;margin:18px 0 6px;}
    .content p,.content li{line-height:1.45;}
    .content a{color:#2563eb;}
    .content blockquote{margin:14px 0;padding:10px 12px;border-left:3px solid #e5e7eb;background:#f9fafb;}
    .content code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:0.95em;}
    .footer{padding:16px 20px;border-top:1px solid #e5e7eb;background:#fafafa;color:#6b7280;font-size:12px;}
    .preheader{display:none!important;visibility:hidden;opacity:0;color:transparent;height:0;width:0;overflow:hidden;mso-hide:all;}
    """.strip()

    html = f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{escape(options.subject)}</title>
    <style>{css}</style>
  </head>
  <body>
    <div class=\"preheader\">{escape(options.preheader)}</div>
    <div class=\"container\">
      <div class=\"card\">
        <div class=\"header\">
          <div class=\"brand\">{escape(options.brand_name)}</div>
          <div class=\"meta\">Generated {escape(generated_at.strftime('%B %d, %Y %H:%M'))}</div>
        </div>
        <div class=\"content\">
          {body_html}
        </div>
        <div class=\"footer\">
          <div>{escape(options.footer_text)}</div>
        </div>
      </div>
    </div>
  </body>
</html>"""

    return html


def build_eml_message(*, html_body: str, text_body: str, options: EmailRenderOptions) -> EmailMessage:
    """Create a MIME email message with text+HTML alternatives."""

    msg = EmailMessage()
    msg["Subject"] = options.subject
    msg["From"] = options.from_addr
    msg["To"] = options.to_addr
    msg["Date"] = formatdate(localtime=True)

    msg.set_content(text_body or "")
    msg.add_alternative(html_body or "", subtype="html")

    return msg


def export_eml_bytes(*, newsletter_markdown: str, options: EmailRenderOptions) -> bytes:
    """Convenience: render HTML + build `.eml` bytes."""

    html_body = render_newsletter_email_html(newsletter_markdown=newsletter_markdown, options=options)
    # Plain-text: keep the original Markdown (readable enough and preserves links).
    text_body = newsletter_markdown
    msg = build_eml_message(html_body=html_body, text_body=text_body, options=options)
    return msg.as_bytes()
