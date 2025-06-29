from pathlib import Path

def define_env(env):
    """
    This is the hook for the variables, macros and filters.
    """

    @env.macro
    def app_html():
        parts = Path(str(getattr(env, 'page'))).parts # apps/Templates/PlotlyPenguins/app/
        app_index = str(Path(getattr(env, 'project_dir'), 'docs', 'site', *parts[1:-1], 'index.html'))
        # print(app_index)
        return app_index

    @env.macro
    def doc_env():
        "Document the environment"
        return {name: getattr(env, name) for name in dir(env) if not name.startswith('_')}
