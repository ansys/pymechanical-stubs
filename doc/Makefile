# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    = -j auto --color --keep-going
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Install dependencies for sphinx-autoapi
# .install-deps:
# 	@pip freeze | grep -q "sphinx-autoapi @ git+https://github.com/ansys/sphinx-autoapi" && is_custom_sphinx_autoapi_installed="yes" || is_custom_sphinx_autoapi_installed="no"
# 	@if [ "$$is_custom_sphinx_autoapi_installed" != "yes" ]; then \
# 		pip uninstall --yes sphinx-autoapi; \
# 		pip install "sphinx-autoapi @ git+https://github.com/ansys/sphinx-autoapi@feat/single-page-stable"; \
# 	fi

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
# %: .install-deps Makefile
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# pdf: .install-deps
pdf:
	mkdir -p doc/_build/latex
	touch doc/_build/latex/doc.pdf


# Customized clean due to examples gallery
# clean: .install-deps
clean:
	rm -rf $(BUILDDIR)/*
	rm -rf $(SOURCEDIR)/examples
	find . -type d -name "_autosummary" -exec rm -rf {} +
