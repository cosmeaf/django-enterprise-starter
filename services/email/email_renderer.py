from django.template.loader import render_to_string
from django.utils.html import strip_tags

class EmailRenderer:
    @staticmethod
    def render(template_path, context):
        html = render_to_string(f"emails/{template_path}.html", context)
        try:
            text = render_to_string(f"emails/{template_path}.txt", context)
        except Exception:
            text = strip_tags(html)
        return text, html