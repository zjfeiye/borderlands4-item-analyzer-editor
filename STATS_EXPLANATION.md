# Understanding Statistical Analysis: Outlier vs Noise

## Quick Guide

When your script runs, look at the **Interpretation** section. It tells you:

- ✓ **STRONG SIGNAL** (z ≥ 2.58): Trust this result! Almost certainly NOT noise.
- ✓ **MODERATE SIGNAL** (z ≥ 1.96): Probably correct, but more data helps.
- ⚠ **WEAK SIGNAL** (z ≥ 1.0): Could be noise. Get more test samples.
- ✗ **NO SIGNAL** (z < 1.0): This is likely random noise.

## Key Metrics Explained

### Z-Score (σ - "sigma")
- **What it is**: How many "standard deviations" away from average your winner is
- **Why it matters**: Larger = more unusual = more likely to be real
- **Rule of thumb**: 
  - z < 1: probably noise
  - z ≥ 2: probably real
  - z ≥ 3: almost definitely real

### Confidence Level
Standard statistical thresholds:
- **99.9%**: Extremely confident (z ≥ 3.29)
- **99%**: Very confident (z ≥ 2.58)
- **95%**: Confident (z ≥ 1.96) ← Industry standard
- **90%**: Somewhat confident (z ≥ 1.65)
- **< 90%**: Not confident (likely noise)

### Standard Deviation
- **What it is**: How "spread out" your results are
- **Why it matters**: If all results are similar (low std dev), even a small winner might be significant
- If results vary a lot (high std dev), you need a bigger gap to be sure

## Example Scenarios

### Scenario 1: Clear Winner
```
Best:  85.2%
Mean:  72.1%
StdDev: 3.5%
Z-Score: 3.74

→ Winner is 13.1% above mean and 3.74 standard deviations away
→ This is a STRONG SIGNAL - trust it!
```

### Scenario 2: Noise
```
Best:  74.3%
Mean:  73.8%
StdDev: 2.1%
Z-Score: 0.24

→ Winner is only 0.5% above mean and 0.24 standard deviations away
→ This is NO SIGNAL - probably just luck
```

### Scenario 3: Need More Data
```
Best:  76.5%
Mean:  73.2%
StdDev: 2.0%
Z-Score: 1.65

→ Winner is 3.3% above mean and 1.65 standard deviations away
→ WEAK SIGNAL - could be real, but add more test samples to be sure
```

## Tips for Better Results

1. **More test samples = more confidence**: Add more buyback pairs to your array
2. **Look at the gap to 2nd place**: If it's large (> 1 σ), the winner is more trustworthy
3. **Check the Top 5**: If only #1 has a high z-score but #2-5 are all similar, that's good
4. **If you get weak signal**: Try testing with the `similar_items_combinations` dataset instead

