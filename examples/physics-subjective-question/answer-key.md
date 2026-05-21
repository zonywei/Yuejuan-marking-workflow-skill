# Answer Key

## Given

- Power: `P = 120 kW = 1.2 x 10^5 W`
- Generator-side voltage: `U1 = 250 V`
- Transmission voltage after step-up: `U2 = 10 kV = 1.0 x 10^4 V`
- Line resistance: `R = 20 Ω`
- Ideal transformer, so power is treated as unchanged before line loss.

## 1. Currents

Generator-side current:

```text
I1 = P / U1 = 1.2 x 10^5 / 250 = 480 A
```

Transmission-line current after step-up:

```text
I2 = P / U2 = 1.2 x 10^5 / 1.0 x 10^4 = 12 A
```

## 2. Line loss and efficiency after step-up

Line loss:

```text
P_loss = I2^2 R = 12^2 x 20 = 2880 W = 2.88 kW
```

Power received by users:

```text
P_user = 120 kW - 2.88 kW = 117.12 kW
```

Efficiency:

```text
η = P_user / P = 117.12 / 120 = 0.976 = 97.6%
```

## 3. No step-up case

If transmitting directly at `250 V`:

```text
I = P / U = 120000 / 250 = 480 A
P_loss = I^2 R = 480^2 x 20 = 4.608 x 10^6 W
```

The calculated line loss is much larger than the source power, so this transmission plan is not physically practical. The result shows that direct low-voltage long-distance transmission would cause huge line loss.

Reason: for a fixed transmission power, increasing voltage reduces current. Since line loss is `I^2R`, reducing current greatly reduces loss.

