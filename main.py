from pathlib import Path

def define_env(env):
    """
    This is the hook for the variables, macros and filters.
    """

    @env.macro
    def app_html():
        parts = Path(str(getattr(env, 'page'))).parts # "apps/Templates/PlotlyPenguins/app/"
        app_index = '/' + str(Path('site', *parts[1:-1], 'index.html')) # "site/Templates/PlotlyPenguins/index.html"
        # generate relative path wtih a lot of ../../..

        relative_path = '../' * (len(parts) - 2 + 1)  # Adjust the number of '../' based on the depth
        app_index = relative_path + app_index

        return app_index

    @env.macro
    def doc_env():
        "Document the environment"
        return {name: getattr(env, name) for name in dir(env) if not name.startswith('_')}
