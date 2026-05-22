# Changelog

## Unreleased

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
