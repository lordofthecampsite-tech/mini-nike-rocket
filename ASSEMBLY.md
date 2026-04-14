# Assembly Instructions

These instructions assume you have sliced and printed all parts per the
handoff spec (0.4 mm nozzle, 3 perimeters, 15 % gyroid, 0.2 mm layer).

![Assembled rocket](images/assembly.png)

## Parts checklist

| Qty | Part | File |
|---:|---|---|
| 1 | Nose cone (with internal shock-cord bridge) | `stl/nose_cone.stl` |
| 1 | Body tube (keyhole fin slots + 2 rail guides) | `stl/body_tube.stl` |
| 1 | Fin can (motor mount + centering rings + fin slots) | `stl/fin_can.stl` |
| 4 | Fins (keyway tab with wings at aft end) | `stl/fin.stl` |

Recovery gear (not printed):

- 12" parachute + shroud lines
- ~18" elastic shock cord
- Recovery wadding
- Estes C6-5 motor (18 mm × 70 mm)

---

## 1. Install the fin can in the body tube

Orient the body tube with the **aft end down** (the aft end has the 4 fin
slots — each slot has a slightly wider pocket at the very bottom).

Slide the fin can up into the aft end of the body tube, collar-first. The
upper collar (25.1 mm OD) friction-fits into the body tube ID (25.4 mm).
Rotate the fin can so its 4 fin slots line up with the body tube's 4 fin
slots. Push it up until the outer flush collar seats against the aft edge
of the body tube.

> **Known simplification:** retention here is friction only. A proper
> bayonet/twist-lock is a known spec gap — see `README.md`. Don't worry
> about it unbonding in flight under a C6-5; the motor thrust pushes
> the fin can *up* into the body tube, not out of it.

## 2. Insert the fins (keyway lock)

Each fin has a **through-wall tab** with two "wings" at the aft end. The
body tube fin slot has a matching pattern: a wider **keyhole pocket** at
the aft end (bottom) and a narrower channel above.

**For each of the 4 fins:**

1. Hold the fin with its aft edge at the bottom, span pointing outward.
2. Position the fin so the winged aft end of its tab aligns with the
   keyhole pocket at the bottom of a body tube slot.
3. Press the tab radially inward through the slot. The wings will pass
   through the wider keyhole pocket; the rest of the tab rides in the
   narrow channel above. The fin face should now sit flush against the
   body tube outer surface.
4. **Slide the fin forward (toward the nose) by ~8 mm.** The wings move
   from under the wider pocket to under the narrow channel. At this
   point the fin is mechanically captured — the wings are wider than
   the narrow slot, so the fin cannot be pulled radially outward.

When all 4 fins are installed and slid forward, you should not be able to
pull any fin outward without sliding it back toward the aft edge.

> **Tip:** if the fin drags on install, check the slot for layer-line
> stringing. A quick pass with a file on the fin tab or inside the slot
> usually fixes it.

## 3. Attach the shock cord to the nose cone

The nose cone has an **internal bridge** with a 2.5 mm hole about 3 mm
above the base of the interior cavity.

1. Feed one end of the shock cord up through the shoulder opening.
2. Pass it through the bridge hole.
3. Tie a robust knot (double overhand or figure-8) with ≥10 mm of tail.
4. Tug the knot up against the underside of the bridge to verify it
   won't pull through.

## 4. Prep and pack the recovery system

1. Tie the free end of the shock cord to the parachute (or to a small
   loop on the body tube — a typical hack is to route the cord around
   the aft centering ring on first pack).
2. Fold the parachute per your usual method and dust it lightly with
   talc if you're flying in cool weather.
3. Slide the recovery wadding into the body tube from the forward
   (nose) end first — 2–3 squares of fire-resistant wadding is enough
   for a C6-5.
4. Load the folded parachute on top of the wadding.
5. Leave the shock cord trailing out of the forward end.

## 5. Fit the nose cone

Press the nose cone shoulder (25.1 mm OD) into the forward end of the
body tube (25.4 mm ID). Friction fit only — it should require firm
thumb pressure to seat and should come off under the ejection charge
pressure of the C6-5.

> **Test first:** with the rocket un-flown, pop the nose cone off by
> hand a few times. You want it snug enough to survive boost but loose
> enough to come off on ejection. Too loose? Add a single wrap of
> masking tape to the shoulder. Too tight? Lightly sand the shoulder OD.

## 6. Load the motor

1. From the aft end, slide an Estes C6-5 up into the fin can's motor
   mount tube (18.5 mm ID). The motor should bottom out against the
   integrated retainer lip.
2. Install the igniter and plug per Estes' instructions.
3. Verify the motor's thrust ring is seated against the retainer lip —
   it should not rattle or slide freely.

## 7. On the pad

The rail guides sit at 45° between fins (never on a fin slot). They are
sized for a standard **80/20 1010 T-slot rail** (6.40 mm surface opening,
8.26 mm interior cavity):

- Aft guide: 85 mm from aft end
- Forward guide: 175 mm from aft end

Slide the rocket onto the rail head-first until the aft guide clears the
rail tip. The rocket should slide freely with minimal slop.

---

## Disassembly (post-recovery)

1. Pop the nose cone off.
2. Pull out the spent motor from the aft end (push down on the thrust
   ring through the mount tube if stuck).
3. Re-pack parachute/wadding for next flight.

To fully disassemble for storage: slide each fin aftward by ~8 mm to
re-align wings with keyholes, then pull fins radially outward. Pull
fin can out of body tube's aft end.
