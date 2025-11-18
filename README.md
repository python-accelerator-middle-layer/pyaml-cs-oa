# `pyaml-cs-oa`

**PyAML control system plugin for ophyd-async**

`pyaml-cs-oa` is a plugin for `PyAML` based on `ophyd-async`, which
currently supports EPICS and Tango control systems.

---

## 🔧 Installation

### **Requirements**

- Python **3.11+**

- Depending on your runtime environment, you may want to install support for EPICS or Tango.

### **EPICS CA/PVA Support**

```
pip install pyaml-cs-oa[epics]
```

This installs:

- `ophyd-async[ca,pva]`

### **Tango Support**

```
pip install pyaml-cs-oa[tango]
```

This installs:

- `ophyd-async[tango]`

---

## 🧪 Developer Installation

If you are contributing, debugging, or running the test suite (no test
currently provided):

```
pip install pyaml-cs-oa[dev]
```

This installs:

- `ophyd-async[ca,pva]`
- `ophyd-async[tango]`
- `pre-commit`
- `ruff`
- `mypy`
- `pytest`

### Setup pre-commit hooks

```
pre-commit install
```
