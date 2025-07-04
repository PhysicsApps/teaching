from pathlib import Path

target_url = 'https://ptuemmler.github.io/msft_web_example/' #use this for QR-code generation via e.g. https://pypi.org/project/qrcode/


def get_app_link(current_path):
    parts = current_path.parts
    html_filename = str(parts[-1]).split('.')[0]
    return str(Path('apps', html_filename, 'index.html'))

def define_env(env):
    """
    This is the hook for the variables, macros and filters.
    """

    @env.macro
    def embed_app(width='100%', height='600px'):
        current_path = Path(str(getattr(env, 'page'))) # " /blog/plotly-penguins-app.html"
        return f"<div>\n<iframe src={get_app_link(current_path)} width={width} height={height}></iframe>\n</div>"

    @env.macro
    def doc_env():
        "Document the environment"
        return {name: getattr(env, name) for name in dir(env) if not name.startswith('_')}
