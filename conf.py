extensions = [ "myst_nb",
              "sphinx_thebe",
              ]

source_suffix = {
	'.rst': 'restructuredtext',
	'.ipynb': 'myst-nb',
}

entry_points={
	"myst_nb.mime_render": [
	"default = myst_nb.render_outputs:CellOutputRenderer",
	"inline = myst_nb.render_outputs:CellOutputRendererInline",
	],
}
# use the default colors
nb_render_plugin="default"

thebe_config = {
    "repository_url": "https://github.com/amehri-upvd/testMaiaBinder",
    "repository_branch": "main",

    # convertt alls cells into interactives cell with thebe
     "selector": "div.highlight"

    # load thebe if user click run
    "always_load": False                  # défaut = True
}
