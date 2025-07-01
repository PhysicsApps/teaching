from pathlib import Path

target_url = 'https://ptuemmler.github.io/msft_web_example/' #use this for QR-code generation via e.g. https://pypi.org/project/qrcode/

def define_env(env):
    """
    This is the hook for the variables, macros and filters.
    """

    @env.macro
    def app_html():
        current_path = Path(str(getattr(env, 'page'))) # " /blog/plotly-penguins-app.html"
        parts = current_path.parts
        html_filename = str(parts[-1]).split('.')[0]
        app_index = str(Path('apps', html_filename, 'index.html'))
        return app_index

    @env.macro
    def doc_env():
        "Document the environment"
        return {name: getattr(env, name) for name in dir(env) if not name.startswith('_')}
