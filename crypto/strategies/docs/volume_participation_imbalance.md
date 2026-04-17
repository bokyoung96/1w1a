# Volume Participation Imbalance

## What it is

This family looks for directional edges when turnover, participation, or aggressor flow becomes unusually unbalanced relative to the recent baseline.

## How it works

- track abnormal volume, taker activity, or participation concentration
- compare current participation to the recent distribution for the same market
- align entries with the side that is attracting authentic incremental participation
- exit when the imbalance normalizes or fails to produce expected price follow-through

## Economic rationale

Price moves backed by real participation are usually more durable than moves caused by drift alone. In perpetual futures, sudden changes in volume and aggressor dominance can reveal informed flow, forced repositioning, or broad market attention before those effects are fully reflected in trend statistics.
