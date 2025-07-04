from pathlib import Path


def get_app_link(current_path, subdir: str):
    parts = current_path.parts
    html_filename = str(parts[-1]).split('.')[0]
    if subdir is not None:
        html_filename += '_' + subdir
    return str(Path('apps', html_filename, 'index.html'))

def define_env(env):
    """
    This is the hook for the variables, macros and filters.
    """

    @env.macro
    def embed_app(width='100%', height='600px', subdir: str = None):
        current_path = Path(str(getattr(env, 'page'))) # " /blog/plotly-penguins-app.html"
        return f"<div>\n<iframe src={get_app_link(current_path, subdir)} width={width} height={height}></iframe>\n</div>"

    @env.macro
    def doc_env():
        "Document the environment"
        return {name: getattr(env, name) for name in dir(env) if not name.startswith('_')}
