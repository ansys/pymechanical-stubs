# clr-stubs

Python stub generation system for .NET assemblies, using pythonnet
These stubs are intended to be used by the autocomplete engine of editors like Atom, Sublime, and VSCode, as well
as for python documentation generation (e.g. with Sphinx)

## Why clr-stubs?

If your are writing python code using .NET modules via pythonnet's `clr.AddReference`, your IDE's
autocomplete (which usually runs python) will not be able to follow any .NET namespaces or libraries.

The workaround in clr-stubs is to create 'stubs' or 'fakes' with the same namespaces, types, and metadata
that would typically be available in a pure python library. The 'stubs' can then be used by your IDE's
autocomplete.


-----------------------

# Documentation

TODO

# Quickstart

TODO


### Credits

This project is inspired by [ironpython-stubs](https://github.com/gtalarico/ironpython-stubs) but is developed
from scratch
