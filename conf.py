extensions = [ "myst_nb",
              "sphinx_thebe",
              ]
# convertt alls cells into interactives cell with thebe
thebe_config = {
   "selector": "div.highlight"
}

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

