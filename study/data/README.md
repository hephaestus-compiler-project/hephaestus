Queries
=======


### Kotlin

```python
{
    'lang': 'kotlin',
    '$or': [
        {'components': "frontend"},
        {'components': "frontend. control-flow analysis"},
        {'components': "frontend. data-flow analysis"},
        {'components': "frontend. declarations"},
        {'components': "frontend. ir"},
        {'components': "frontend. resolution and inference"}
    ]
}
```


### Groovy

```python
{
    'lang': 'groovy',
    'type': 'bug',
    'status': 'closed',
    'resolution': 'fixed',
    '$or': [
        {'components': 'static type checker'},
        {'compomenets': 'static compilation'},
        {'compomenets': 'compiler'},
    ]
}
```
