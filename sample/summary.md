```py
# COUNT: 5
[
    {
        'color': str,
          # 'black'{1}, ...[5 singletons]
        'category': str,
          # 'hue'{5}
        'type': str,
          # 'primary'{4}, 'secondary'{1} [2 uniq, 5 total]
        'code': {
            'rgba': [
              # COUNT: 4
                int,
                  # 255{8}, 0{7}, 1{5}
            ],
            'hex': str,
              # '#FF0'{2}, '#000'{1}, '#00F'{1}, '#0F0'{1} [4 uniq, 5 total]
        },
    },
]
```
