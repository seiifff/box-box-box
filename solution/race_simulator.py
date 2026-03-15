#!/usr/bin/env python3
"""
Box Box Box - F1 Race Simulator
Reverse-engineered from 30,000 historical races.

Model: lap_time = base_lap_time + offset[C] + rate[C] * max(0, tire_age - cliff[C]) * temp_factor
  where temp_factor = track_temp^0.358 / 4.06

Parameters discovered through data analysis:
  SOFT:   offset = -1.0,  rate = 2.0,  cliff = 10
  MEDIUM: offset =  0.0,  rate = 1.0,  cliff = 20
  HARD:   offset =  0.8,  rate = 0.5,  cliff = 30

Temperature scaling: temp^0.358 / 4.06 (applied to degradation only, not offset)
Pit stop: flat time penalty per stop (from race config)
Tire age: resets to 0 on pit stop, increments by 1 at start of each lap
Tie-breaking: lower driver ID wins (D001 before D002)
"""

import json
import sys


# Model parameters
OFFSET = {'SOFT': -1.0, 'MEDIUM': 0.0, 'HARD': 0.8}
RATE = {'SOFT': 2.0, 'MEDIUM': 1.0, 'HARD': 0.5}
CLIFF = {'SOFT': 10, 'MEDIUM': 20, 'HARD': 30}
TEMP_ALPHA = 0.358
TEMP_SCALE = 4.06


def simulate_race(race_data):
    rc = race_data['race_config']
    base_lap_time = rc['base_lap_time']
    pit_lane_time = rc['pit_lane_time']
    total_laps = rc['total_laps']
    temp_factor = rc['track_temp'] ** TEMP_ALPHA / TEMP_SCALE

    driver_times = []

    for pos_idx in range(1, 21):
        strategy = race_data['strategies'][f'pos{pos_idx}']
        driver_id = strategy['driver_id']
        current_tire = strategy['starting_tire']

        # Build pit stop lookup
        pit_stops = {ps['lap']: ps['to_tire'] for ps in strategy['pit_stops']}

        total_time = 0.0
        tire_age = 0

        for lap in range(1, total_laps + 1):
            tire_age += 1

            # Calculate lap time: offset is flat, degradation scales with temp
            offset = OFFSET[current_tire]
            degradation = RATE[current_tire] * max(0, tire_age - CLIFF[current_tire]) * temp_factor
            lap_time = base_lap_time + offset + degradation

            total_time += lap_time

            # Handle pit stop at end of lap
            if lap in pit_stops:
                total_time += pit_lane_time
                current_tire = pit_stops[lap]
                tire_age = 0

        driver_times.append((total_time, driver_id))

    # Sort by total time (ties broken by driver_id due to stable sort + iteration order)
    driver_times.sort(key=lambda x: (x[0], x[1]))
    finishing_positions = [driver_id for _, driver_id in driver_times]

    return finishing_positions


def main():
    test_case = json.load(sys.stdin)

    race_id = test_case['race_id']
    finishing_positions = simulate_race(test_case)

    output = {
        'race_id': race_id,
        'finishing_positions': finishing_positions
    }

    print(json.dumps(output))


if __name__ == '__main__':
    main()
