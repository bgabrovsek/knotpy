# Documentation

The knotpy project uses [Sphinx](https://github.com/sphinx-doc/sphinx) to generate documentation.

## Installation

After cloning the *knotpy* project, install the requirements by running the following command from the project's root directory.

```bash
pip install -r docs/requirements.txt
```

## Building documentation

To build the entire documentation in the HTML format, run the following command inside the `docs/` directory.

```bash
make html
```

This will generate the `_build/html` subdirectory containing the built documentation.