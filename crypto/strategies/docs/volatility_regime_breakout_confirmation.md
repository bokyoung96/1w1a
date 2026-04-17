# Volatility Regime / Breakout Confirmation

## What it is
A breakout filter that activates only when volatility conditions support expansion rather than chop.

## How it works
It tracks 15-minute and 1-hour volatility state, then allows breakout entries when range compression transitions into expanding realized movement. Low-quality breakouts in dull regimes are filtered out.

## Economic rationale
Breakout systems work better when volatility is transitioning from compression to expansion. In crypto, regime shifts often coincide with news, liquidations, or sudden participation surges.
