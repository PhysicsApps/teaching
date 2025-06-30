from pathlib import Path

def define_env(env):
    """
    This is the hook for the variables, macros and filters.
    """

    @env.macro
    def app_html():
        parts = Path(str(getattr(env, 'page'))).parts # "apps/Templates/PlotlyPenguins/app/"
        app_index = str(Path('shinyliveapps', *parts[1:-1], 'index.html')) # "shinyliveapps/Templates/PlotlyPenguins/index.html"
        # generate relative path wtih a lot of ../../..

        relative_path = '../' * (len(parts) - 1)
        app_index = relative_path + app_index

        return app_index

    @env.macro
    def doc_env():
        "Document the environment"
        return {name: getattr(env, name) for name in dir(env) if not name.startswith('_')}
