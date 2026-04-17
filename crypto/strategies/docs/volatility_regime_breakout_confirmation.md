# Volatility Regime Breakout Confirmation

## What it is

This family trades directional breakouts only when the volatility regime supports expansion, helping separate real range escapes from low-energy noise.

## How it works

- estimate whether realized or implied volatility is compressing or expanding
- pair directional triggers with volatility-regime filters
- allow breakout entries when volatility transitions from compression to expansion
- stand down when volatility is too dead or too chaotic for clean trend capture

## Economic rationale

Breakouts are more likely to persist when volatility shifts from quiet accumulation into active repricing. In crypto, volatility regime changes often accompany narrative catalysts, liquidation cascades, and renewed participation, so combining direction with volatility context can improve selectivity.
