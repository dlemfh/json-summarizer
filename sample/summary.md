```py
# COUNT: 5
[
    {
        'color': str,
          # 'black'{1}, ...[5 singletons]
        'category': str,
          # 'hue'{5}
        'type': str,
          # 'primary'{4}, 'secondary'{1}
        'code': {
            'rgba': List[int],
              # LEN: 4
              # [255, 255, 255, 1]{1}, ...[5 singletons]
            'hex': str,
              # '#FF0'{2}, '#000'{1}, '#00F'{1}, '#0F0'{1}
        },
    },
]
```
