from renderers.email_renderer import EmailRenderOptions, render_newsletter_email_html, export_eml_bytes


def test_render_email_html_contains_subject_and_content():
    md = "# Title\n\n## Section\n- Item\n"
    options = EmailRenderOptions(subject="Test Subject")
    html = render_newsletter_email_html(newsletter_markdown=md, options=options)
    assert "Test Subject" in html
    assert "Title" in html
    assert "Section" in html


def test_export_eml_bytes_non_empty():
    md = "# Hello\n\nWorld\n"
    options = EmailRenderOptions(subject="Hello")
    data = export_eml_bytes(newsletter_markdown=md, options=options)
    assert isinstance(data, (bytes, bytearray))
    assert len(data) > 100
