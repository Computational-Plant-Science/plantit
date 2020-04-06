# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS      =
SPHINXBUILD     = docker-compose -f docker-compose.yml -f docker-compose.dev.yml run plantit sphinx-build
SPHINXAPIDOC    = docker-compose -f docker-compose.yml -f docker-compose.dev.yml run plantit sphinx-apidoc
SPHINXPROJ      = DIRT2Web
SOURCEDIR       = ../docs/source
BUILDDIR        = ../docs/build
CODEDIR         = .
# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

apidoc:
	@$(SPHINXAPIDOC) -o "$(SOURCEDIR)" "$(CODEDIR)"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
