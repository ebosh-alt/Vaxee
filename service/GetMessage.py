from jinja2 import Environment, PackageLoader, select_autoescape


def get_mes(path: str, **kwargs):
    env = Environment(
        loader=PackageLoader(package_name='main', package_path="messages", encoding="utf-8"),
        autoescape=select_autoescape(['html', 'xml'])
    )

    if ".md" not in path:
        path = path + '.md'
    tmpl = env.get_template(path)
    return tmpl.render(kwargs)

def get_text(text: str) -> str:
    text = text.replace("_", r"\_")
    text = text.replace("{", r"\{")
    text = text.replace("}", r"\}")
    # text = text.replace("[", r"\[")
    # text = text.replace("]", r"\]")
    text = text.replace("<", r"\<")
    text = text.replace(">", r"\>")
    # text = text.replace("(", r"\(")
    # text = text.replace(")", r"\)")
    text = text.replace("#", "")
    text = text.replace("+", r"\+")
    text = text.replace("-", r"\-")
    text = text.replace(".", r"\.")
    text = text.replace("!", r"\!")
    text = text.replace("=", r"\=")
    text = text.replace("|", r"\|")
    # text = text.replace("**", "*")
    return text