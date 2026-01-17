from pathlib import Path
import platform

def get_app_link(current_path, subdir: str, target: str):
    parts = current_path.parts
    html_filename = str(parts[-1]).split('.')[0]
    if subdir is not None:
        html_filename += '_' + subdir

    if platform.system() == "Windows":
        app_link =  str(Path('apps_' + html_filename, target))
    elif platform.system() == "Linux":
        app_link =  str(Path('apps', html_filename, target))
    else:
        raise ValueError("Unsupported operating system. This script only supports Windows and Linux.")
    return app_link

def define_env(env):
    """
    This is the hook for the variables, macros and filters.
    """

    @env.macro
    def embed_app(width='100%', height='600px', subdir: str = None):
        current_path = Path(str(getattr(env, 'page'))) # " /blog/plotly-penguins-app.html"
        return f"<div>\n<iframe src={get_app_link(current_path, subdir, 'index.html')} width={width} height={height}></iframe>\n</div>"

    @env.macro
    def embed_code(subdir: str = None, language: str = 'python'):
        current_path = Path(str(getattr(env, 'page'))) # " /blog/plotly-penguins-app.html"
        if language == 'python':
            with open(Path("site", get_app_link(current_path, subdir, "app.py"))) as f:
                code_text =  f.read()
            embed_text = "\n``` py title='app.py' linenums='1'\n" + code_text + "\n```\n"
        else:
            raise KeyError("Unsupported language")
        return embed_text

    @env.macro
    def doc_env():
        "Document the environment"
        return {name: getattr(env, name) for name in dir(env) if not name.startswith('_')}
