import drf_turbo

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_issues",
]

primary_domain = "py"
default_role = "py:obj"

github_user = "Mng-dev-ai"
github_repo = "drf-turbo"

issues_github_path = f"{github_user}/{github_repo}"

# The master toctree document.
master_doc = "index"
language = "en"
html_domain_indices = False
source_suffix = ".rst"
project = "drf-turbo"
copyright = "2021, Michael Gendy"
version = release = drf_turbo.__version__
templates_path = ["_templates"]
exclude_patterns = ["_build"]
author = "Michael Gendy"
autoclass_content = "both"

# Theme
html_theme = "furo"


html_sidebars = {
    "*": [
        "sidebar/scroll-start.html",
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
    ]
}
