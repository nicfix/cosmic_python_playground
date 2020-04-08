# Cosmic Python Playground

A playground to exercise while reading the Cosmic Python book: https://www.cosmicpython.com/

### Prerequisites
Setup a running python3 environment (os or virtualenv).

### Setup
```bash
$ pip install -r requirements.txt
```

### Dev Setup
```bash
$ pip install -r requirements-dev.txt
```

### Run tests
```bash
$ pytest --cov-config=.coveragerc --cov=. batch_allocation/
```

### Format code
```bash
$ black ./batch_allocation
```

### Linter
```bash
$ flake8 ./batch_allocation
```
