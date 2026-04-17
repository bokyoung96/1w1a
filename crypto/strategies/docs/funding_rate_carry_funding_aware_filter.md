# Funding Rate Carry Funding Aware Filter

## What it is

This family harvests funding-driven carry or uses funding as a positioning filter so the strategy can favor crowded or uncrowded perp setups more intelligently.

## How it works

- monitor funding-rate extremes and their persistence through time
- combine funding with price trend, basis proxies, or crowding context
- enter when the carry opportunity or funding filter aligns with risk controls
- avoid naive carry trades when funding is extreme for good structural reasons

## Economic rationale

Perpetual funding transfers expose where leveraged demand is concentrated. Persistent positive or negative funding can create carry, but it also reveals crowding risk. Strategies that explicitly model that information can capture compensation when positioning is one-sided without blindly stepping in front of strong directional flows.
