# Changelog

## Unreleased

## 0.2.1 - 2026-06-11

- Hardened the normal mowing finish step so the automation sends the mower home after the calculated runtime whenever the mower is still in any active state, not only when Home Assistant reports `mowing`.

## 0.2.0 - 2026-06-11

- Changed grass growth estimation to a cool-season turf Growth Potential (GP) temperature model.
- Reworked automatic planning so forecast-based mowing slots are scored across the next few days instead of sticking to only the primary or backup hour.
- Added wet-grass protections for recent rain, rain probability and high humidity in the automatic slot search.
- Improved mowing notifications so they explain when mowing is planned or skipped and why, using readable relative labels such as today, tomorrow and in 2 days.
- Added a missed-start checker so a planned start can still run shortly after the stored helper time.

- Added a simple automatic-irrigation growth correction for regularly watered lawns.
- Fixed the next planned mowing helper so daily recalculation can postpone a stored future time when the grass growth threshold or minimum mowing gap is not ready yet.
- When a primary or backup start fires before mowing is required, the automation now updates the next planned mowing helper and stops without leaving a stale missed start time.

## 0.1.5

- Changed the smart mowing sequence so normal mowing starts only after the mower finishes edge cutting, returns to the dock and recharges to the configured battery level.
- Added configurable post-edge battery target and maximum charge wait time.

## 0.1.4

- Fixed the edge-cut-to-normal-mowing handoff so the automation no longer stops after the edge pass.
- Replaced dynamic wait timeouts with explicit polling loops for better Home Assistant compatibility.
- Added confirmation waits and a second start attempt before treating normal mowing as failed.

## 0.1.3

- Required the Worx Vision Cloud PLUS edge cutting button in the smart mowing blueprint.
- Every planned smart mowing start now runs an edge-only pass first, waits for it to finish, and then starts normal mowing.

## 0.1.2

- Updated smart mowing documentation and blueprint labels for the renamed rain precipitation sensor.
- Kept the next planned mowing helper stable during daily recalculation: future dates are no longer pushed later unless the stored date has passed.

## 0.1.1

- Clarified that the smart mowing blueprint requires three Home Assistant helpers.
- Marked the next planned mowing helper as required in the blueprint instructions.

## 0.1.0

- Initial release of the separated automation repository.
- Added Smart mowing schedule blueprint.
- Added My Home Assistant import button.
- Added setup documentation and optional helper package example.
