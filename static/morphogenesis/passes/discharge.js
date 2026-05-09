// Discharge — charge propagates ALONG branch_memory ridges, not isotropically.
//
// In v0.1 charge merely diffused, so high-charge regions looked like soft
// glows.  In v0.2 we want the relational picture: where wood (branch_memory)
// has accumulated paths, fire (charge) follows them.  The implementation:
//
//   chargeNext[i] = charge[i] * (1 - alpha · branch[i])
//                 +  alpha · branch[i] · branchWeightedAvgOfNeighbors(charge)
//
// Effect: cells with high branch_memory pull charge from neighbors that
// also have high branch_memory, while low-branch cells leak charge away
// faster.  The result is a tendency for charge to concentrate along the
// branched filaments.  Where charge AND branch are both high we also leak
// energy into `life` — that's the moment a discharge lights tissue, the
// "rootToLightning" relation made visible at the field level.

export function dischargePass(stack, grid, params) {
  const {
    branch_thresh = 0.04,
    propagate = 0.45,
    leak_to_life = 0.018,
    decay = 0.985,
  } = params;

  const W = stack.W, H = stack.H, N = stack.N;
  const branch = stack.get("branch_memory");
  const charge = stack.get("charge");
  const life = stack.get("life");
  const chargeNext = stack.scratchOf("charge");

  // First pass: branch-weighted neighbor average of charge.
  for (let y = 0; y < H; y++) {
    const yp = (y - 1 + H) % H, yn = (y + 1) % H;
    for (let x = 0; x < W; x++) {
      const xp = (x - 1 + W) % W, xn = (x + 1) % W;
      const i = y * W + x;
      const b = branch[i];

      if (b < branch_thresh) {
        // Low-branch cells: pure decay
        chargeNext[i] = charge[i] * decay;
        continue;
      }

      // Branch-weighted neighbor sum
      const nb = [
        branch[y * W + xp], branch[y * W + xn],
        branch[yp * W + x], branch[yn * W + x],
      ];
      const nc = [
        charge[y * W + xp], charge[y * W + xn],
        charge[yp * W + x], charge[yn * W + x],
      ];
      let wsum = 0, csum = 0;
      for (let k = 0; k < 4; k++) {
        const w = nb[k] + 1e-6;
        wsum += w;
        csum += nc[k] * w;
      }
      const target = wsum > 0 ? csum / wsum : charge[i];
      const alpha = propagate * b;
      chargeNext[i] = (charge[i] * (1 - alpha) + target * alpha) * decay;

      // Discharge leaks into life — the "lighting tissue" moment
      const intensity = Math.abs(charge[i]) * b;
      const next = life[i] + leak_to_life * intensity;
      life[i] = next > 1 ? 1 : next;
    }
  }
  stack.swap("charge");
}
