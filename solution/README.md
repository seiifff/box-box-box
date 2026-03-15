# Solution — Box Box Box

## Approach

Reverse-engineered the race simulation formula from 30,000 historical races using constraint analysis and algebraic methods.

## Model

```
lap_time = base_lap_time + offset[compound] + rate[compound] × max(0, tire_age - cliff[compound]) × temp_factor
```

| Parameter | SOFT | MEDIUM | HARD |
|-----------|------|--------|------|
| Offset    | -1.0 | 0.0    | 0.8  |
| Rate      | 1.97 | 1.0    | 0.5  |
| Cliff     | 10   | 20     | 30   |

- **Offset**: Compound speed advantage per lap (SOFT fastest, HARD slowest)
- **Cliff**: Laps of consistent performance before degradation begins
- **Rate**: How quickly lap times increase after the cliff
- **Temp Factor**: Scales degradation based on track temperature and base lap time

## Key Discoveries

1. **Offset ratio** `off_SOFT / off_HARD = -5/4` — proven algebraically from driver ties in historical data
2. **Rates and cliffs** confirmed via marginal constraint analysis on 6,000+ driver pairs
3. **Temperature factor** depends on both `track_temp` and `base_lap_time`, not temperature alone

## Score

**100/100** on test cases.
