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


### Scala


```python
{
    'lang': 'scala',
    'status': 'closed',
    '$or': [
        {
            '$and': [
                {
                    '$or': [
                        {'labels': 'bug'},
                        {'labels': 'itype:bug'},
                        {'labels': 'itype:crash'},
                    ]
                },
                {
                    '$or': [
                        {'labels': 'area:implicits'},
                        {'labels': 'area:gadt'},
                        {'labels': 'area:match-types'},
                        {'labels': 'area:nullability'},
                        {'labels': 'area:overloading'},
                        {'labels': 'area:pattern-matching'},
                        {'labels': 'area:typer'},
                        {'labels': 'area:erasure'},
                        {'labels': 'area:erased-terms'},
                    ]
                }
            ]

        },
        {
            '$or': [
                {'labels': 'blocker'},
                {'labels': 'compiler crash'},
                {'labels': 'dependent types'},
                {'labels': 'erasure'},
                {'labels': 'errors and warnings'},
                {'labels': 'existential'},
                {'labels': 'structural types'},
                {'labels': 'gadt'},
                {'labels': 'implicit classes'},
                {'labels': 'implicit'},
                {'labels': 'infer'},
                {'labels': 'typer'},
                {'labels': 'overloading'},
                {'labels': 'patmat'},
                {'labels': 'should compile'},
                {'labels': 'should not compile'},
                {'labels': 'runtime crash'},
                {'labels': 'singleton-type'},
                {'labels': 'typelevel'},
            ]
        }
    ],
}
```
