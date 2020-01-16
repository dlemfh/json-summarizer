```py
# COUNT: 3
[
    {
        'id': str,
          # '0001'{1}, ...(3 singletons)
        'type': str,
          # 'donut'{3}
        'name': str,
          # 'Cake'{1}, ...(3 singletons)
        'ppu': float,
          # 0.55
        'batters': {
            'batter': [
              # COUNT: 1, 2, 4
                {
                    'id': str,
                      # '1001'{3}, '1002'{2}, '1003'{1}, '1004'{1}
                    'type': str,
                      # 'Regular'{3}, 'Chocolate'{2}, 'Blueberry'{1}, "Devil's Food"{1}
                },
            ],
        },
        'topping': [
          # COUNT: 4, 5, 7
            {
                'id': str,
                  # '5001'{3}, '5002'{3}, '5003'{3}, '5004'{3}, '5005'{2}, '5007'{1}, '5006'{1}
                'type': str,
                  # 'None'{3}, 'Glazed'{3}, 'Chocolate'{3}, 'Maple'{3}, 'Sugar'{2}, ...(7 uniq, 16 total)
            },
        ],
    },
]
```
