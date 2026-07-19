# Changelog

## Unreleased

- Added a fast technical retry after interrupted starts when the mower is docked and current conditions are still safe, instead of waiting for the backup hour.
- Reworked mowing notifications into readable multi-section messages with preserved line breaks.
- Stabilized dock confirmation after edge cutting and normal mowing so brief Worx Cloud `returning`/`unknown` flaps do not interrupt the cycle when RTK still shows the mower at the station.
- Added a weather-source note recommending Tomorrow.io when the user does not have a local weather station.
- Limited hourly forecast processing to the planning horizon so long Pirate Weather responses no longer exceed Home Assistant's template output limit.
- Fixed missing final notifications for interrupted mowing cycles after the edge pass had already started.
- Clarified "no safe slot" notification text so it no longer labels the planned retry time as the next condition refresh.
- Reworked the GitHub README and blueprint description into clearer sections for new users.
- Limited notifications to the daily growth calculation, mowing start, and mowing completion/interruption after a real start.
- Kept the 30-minute condition refresh silent so forecast changes no longer show fluctuating projected growth as stored accumulated growth.

## 0.4.1 - 2026-06-29

- Fixed automatic planning so an unsafe preferred hour is replaced with the nearest safe daytime forecast slot instead of being reported as a planned start.
- Added a daytime fallback search from `06:00` to `22:00` when no safe slot exists inside the selected non-night mowing window.
- Planning, postponement and completion notifications now show accumulated grass growth and the forecast conditions for the selected mowing time.
- The 30-minute condition refresh now updates the notification when it changes the planned mowing time.

## 0.4.0 - 2026-06-28

- Added a `22:00-05:00` night mowing preset with a required FiatLux accessory confirmation.
- Fixed forecast window calculations for mowing windows that cross midnight.
- Reworked notifications to show clear start, finish, measured duration, postponement reason and next attempt.
- Added silent condition and forecast refresh every 30 minutes without double-counting grass growth.
- Kept immediate condition recalculation after completed and postponed mowing cycles.
- Added configurable minimum and maximum outdoor mowing temperatures, defaulting to `10-25 C`.
- Automatic forecast planning now rejects slots outside the allowed temperature range.
- Added hard temperature checks before the edge pass and again before normal mowing after charging.
- Added postponement notifications that include the measured temperature, allowed limit and next attempt.

## 0.3.0 - 2026-06-20

- Reordered planned mowing so the verified edge-only command runs first.
- Added required confirmation that the edge pass finished and the mower returned to the dock.
- Added an eight-hour charge wait with a fixed minimum battery level of 80% before normal one-time mowing can start.
- Added clear failure notifications and stopped normal mowing when the edge start, dock return or battery target is not confirmed.

## 0.2.9 - 2026-06-18

- Changed the planned mowing cycle to run normal one-time mowing first and then start a separate edge-only pass after the mower returns to the dock.
- Fixed planned-start failure paths so the next mowing helper is moved to the calculated retry time when rain or no-start confirmation blocks the run.
- Guarded the edge-cut step so it is skipped with a notification if the mower does not return to the dock before the edge stage.

## 0.2.8 - 2026-06-17

- Changed the minimum mow gap logic for whole-day values: `1 day` now means the next calendar day, so daily robotic mowing is preferred when growth, rain, wet-grass and battery conditions are safe.

## 0.2.7 - 2026-06-16

- Increased the forecast delay penalty when grass growth is already high, so the automation prefers the nearest safe same-day mowing window over ideal weather on a later day.
- Raised rain and high rain-probability penalties so urgent mowing still never wins over unsafe wet-weather conditions.
- Updated mowing-planning notifications to explain when high growth makes the automation choose the nearest safe window.
- Added manual mowing synchronization: if the mower is started outside the automation and mows for at least 10 minutes before returning to the dock, the growth and last-mow helpers are reset.

## 0.2.6 - 2026-06-14

- Changed the automatic mowing threshold to a robotic-mowing model: frequent light cuts around 2-4.5 mm of estimated growth, while the one-third blade rule is kept as a safety limit instead of a start threshold.
- Updated blueprint, README and setup documentation to explain the new robot-oriented mowing logic.

## 0.2.5 - 2026-06-13

- Rewritten the blueprint description in Polish so it is clearer and more professional for end users.
- Removed obsolete edge-only, post-edge charging and compatibility inputs from the smart mowing blueprint.
- Cleaned the planned mowing start flow so it sends exactly one one-time mowing command with edge cutting enabled, waits for confirmation, and retries once if the mower stays docked or paused.
- Updated start failure and rain notifications to describe the simplified edge-plus-mowing command.

## 0.2.4 - 2026-06-12

- Simplified the mowing start sequence: planned starts now send one one-time mowing command with edge cutting enabled, without a separate edge-only pass, dock/charge wait, or separate normal mowing command.

## 0.2.3 - 2026-06-12

- Added simple mowing window presets: morning, before noon, noon, afternoon, evening and custom hours.
- Added automatic mowing threshold calculation from cutting height (`20-60 mm`) using the one-third grass blade rule.
- Kept the manual growth threshold as an advanced fallback for users who want full control.
- Updated schedule notifications so they show the calculated start threshold and cutting height source.

## 0.2.2 - 2026-06-12

- Added a Worx Cloud status recovery guard: when RTK shows the mower at the station for 5 minutes while the cloud still reports an active mowing/returning state, the automation starts a 1-minute mowing command and sends the mower back to the dock.
- Added Home Assistant notifications explaining when this cloud status recovery is being sent.

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
