from pathlib import Path

target_url = 'https://ptuemmler.github.io/msft_web_example/' #use this for QR-code generation via e.g. https://pypi.org/project/qrcode/

def define_env(env):
    """
    This is the hook for the variables, macros and filters.
    """

    @env.macro
    def app_html():
        parts = Path(str(getattr(env, 'page'))).parts # " /blog/plotly-penguins-app.html"
        html_filename = str(parts[-1]).split('.')[0]
        app_index = '/' + str(Path('shinyliveapps', html_filename, 'index.html'))
        return app_index

    @env.macro
    def doc_env():
        "Document the environment"
        return {name: getattr(env, name) for name in dir(env) if not name.startswith('_')}
