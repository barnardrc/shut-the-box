# Shut the Box strategy simulator

A small Monte Carlo experiment for comparing deterministic move-selection
heuristics in the dice game **Shut the Box**.

The simulator plays the common nine-tile variant. It rolls two dice while the
sum of the open tiles is greater than six and one die thereafter. Each strategy
chooses from every legal combination that matches the roll. A game’s score is
the sum of the tiles left open, so lower scores are better and zero means the
box was shut.

## Strategies

The experiment includes simple baselines and composite heuristics:

- prefer the largest available tile;
- prefer the narrowest numeric range;
- remove the fewest tiles;
- combine tile value, move size, and range;
- preserve future ways to make seven.

The strategy names and exact tie-breaking rules are defined in
[`select_move`](shut_the_box_strategy_comparison.py).

## Run the experiment

Python 3.10 or newer is recommended. The project has no third-party runtime
dependencies.

```bash
python shut_the_box_strategy_comparison.py --sessions 1000 --games-per-session 10 --seed 43
```

The optional seed makes comparisons reproducible. Results are printed in
best-to-worst order by average remaining score.

```text
STRATEGY                     |  AVG SESSION |   AVG GAME
-----------------------------------------------------------
...
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## Methodology and limitations

Each strategy receives an independent pseudorandom stream. This avoids making
the result for one strategy depend on how many random numbers an earlier
strategy consumed. More sessions reduce sampling noise but do not prove that a
heuristic is optimal.

The simulator intentionally evaluates explainable heuristics rather than an
exhaustive dynamic-programming policy. Rule variants—such as always rolling two
dice or using twelve tiles—would require separate experiments.

## Repository layout

```text
.
├── shut_the_box_strategy_comparison.py  # game rules, strategies, and CLI
└── tests/                                # deterministic unit tests
```

## License

No license has been selected yet. Until one is added, normal copyright rules
apply.
