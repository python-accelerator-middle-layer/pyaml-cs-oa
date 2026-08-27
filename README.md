# pyaml-cs-oa

**PyAML control system plugin for ophyd-async**

[![Documentation Status](https://readthedocs.org/projects/pyaml-cs-oa/badge/?version=latest)](https://pyaml-cs-oa.readthedocs.io/en/latest/?badge=latest)
[![Current release](https://img.shields.io/github/v/tag/python-accelerator-middle-layer/pyaml-cs-oa)](https://github.com/python-accelerator-middle-layer/pyaml-cs-oa/tags)

## Overview

`pyaml-cs-oa` provides `pyAML` control-system bindings based on
`ophyd-async`. It currently supports EPICS and Tango control systems.

## Installation

Install the package from PyPI:

```bash
pip install pyaml-cs-oa
```

**EPICS CA/PVA Support**

```bash
pip install pyaml-cs-oa[epics]
```

This adds the EPICS channel and PV access dependencies.

**TANGO Support**

```bash
pip install pyaml-cs-oa[tango]
```

This adds the TANGO dependencies.

## Development

Install the development dependencies with:

```bash
pip install pyaml-cs-oa[dev]
```

Run the test suite with:

```bash
pytest
```

Install the pre-commit hooks with:

```bash
pre-commit install
```

## Documentation

The documentation is available at:

<https://pyaml-cs-oa.readthedocs.io/en/latest/>

## Contributing

Please use the issue tracker or submit a pull request.
