# clr-stubs

Python stub generation system for .NET assemblies, using pythonnet
These stubs are intended to be used by the autocomplete engine of editors like Atom, Sublime, and VS Code, as well
as for python documentation generation (for example, with Sphinx)

## Why clr-stubs?

If your are writing python code using .NET modules via pythonnet's `clr.AddReference`, your IDE's
autocomplete (which usually runs python) will not be able to follow any .NET namespaces or libraries.

The workaround in clr-stubs is to create 'stubs' or 'fakes' with the same namespaces, types, and metadata
that would typically be available in a pure python library. The 'stubs' can then be used by your IDE's
autocomplete.


-----------------------

# Documentation

1. Install Mechanical 2023 R2 onto your computer.

    Ensure the environment variable, AWP_ROOT232, is set to the location of
    Mechanical 2023 R2 (C:\Program Files\Ansys Inc\v232).

2. Run main.py to generate the stubs from Mechanical 232.

    ```python main.py```

    Note: There may be an Unhandled Exception when the stubs are done running.
    If the message, "Done creating all Mechanical stubs" appears, proceed
    to the next step.

3. Next, create a virtual environment and activate it:

    ```python -m venv .venv```

    Windows:
        ```.venv\Scripts\activate.bat```

    Linux:
        ```source .venv/bin/activate```

4. Navigate to the package directory and install mechanical-stubs

    ```cd package && pip install -e .```

5. Navigate to the doc directory and make the Sphinx documentation

    ```cd doc && make html```

    Note: Warning messages can be ignored for now.


# Quickstart

TODO


### Credits

This project is inspired by [ironpython-stubs](https://github.com/gtalarico/ironpython-stubs) but is developed
from scratch
