# Funding-Rate Carry / Funding-Aware Filter

## What it is
A strategy family that harvests carry or filters directional trades using funding-rate conditions.

## How it works
It blends 15-minute price action with 1-hour structure and 8-hour funding information. Signals are strongest when directional setup and carry regime agree, and weakest when funding implies crowded positioning against the trade.

## Economic rationale
Funding transfers are a direct expression of leverage imbalance in perpetual futures. Using funding as a carry source or risk filter can improve trade selection when positioning gets one-sided.
