import typing

import jinja2


def render_jinja2_template(
    template_str: str, configuration: typing.Mapping
) -> str:
    """
    Renders a jinja2 template
    """

    template = jinja2.Template(template_str)
    return template.render(**configuration)
