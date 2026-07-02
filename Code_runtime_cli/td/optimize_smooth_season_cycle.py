"""Smooth cycle: reveal current color, then dissolve into next season mono."""

CONTROLLER = "/mosheng_project/00_control_panel/automation_heartbeat_controller"

controller = op(CONTROLLER)
if controller is None:
    raise Exception("Missing " + CONTROLLER)

text = controller.text

if "OPEN_DURATION = " not in text:
    text = text.replace(
        "AMBIENT_LEVELS = (0.075, 0.065, 0.07, 0.065)\n",
        "AMBIENT_LEVELS = (0.075, 0.065, 0.07, 0.065)\n"
        "OPEN_DURATION = 5.5\n"
        "TURN_DURATION = 8.0\n",
        1,
    )
text = text.replace("TURN_DURATION = 8.0", "TURN_DURATION = 10.0")
if "COLOR_TO_MONO_PORTION" not in text:
    text = text.replace(
        "TURN_DURATION = 10.0\n",
        "TURN_DURATION = 10.0\n"
        "COLOR_TO_MONO_PORTION = 0.45\n",
        1,
    )

if "def _smoothstep01" not in text:
    text = text.replace(
        "def _node(path):\n    return op(path)\n",
        "def _node(path):\n"
        "    return op(path)\n\n"
        "def _smoothstep01(value):\n"
        "    value = max(0.0, min(1.0, value))\n"
        "    return value * value * (3.0 - 2.0 * value)\n\n"
        "def _smootherstep01(value):\n"
        "    value = max(0.0, min(1.0, value))\n"
        "    return value * value * value * (value * (value * 6.0 - 15.0) + 10.0)\n",
        1,
    )

start = text.find("    if state == 'opening':")
end = text.find("    # Sealed/revealing: motion paints color into the scroll.")
if start < 0 or end < 0 or end <= start:
    raise Exception("Could not locate opening/turning state block safely")

new_block = """    if state == 'opening':
        raw = (now - state_started) / OPEN_DURATION
        fraction = _smootherstep01(raw)
        # Gently complete the current season before beginning the page turn.
        transition_mask.par.cross = fraction
        shape_guard.par.brightness1 = 1.0
        brush_guard.par.brightness1 = 1.5
        dim.par.value0 = 0
        _set_audio_mix(current)
        if raw >= 1.0:
            parent_comp.store('auto_state', 'turning')
            parent_comp.store('state_started', now)
        return

    if state == 'turning':
        raw = (now - state_started) / TURN_DURATION
        next_season = 1 if current >= 4 else current + 1

        # Three-beat transition:
        # current color -> current mono -> next mono. This avoids overlapping
        # two richly colored compositions, which reads as a harsh double image.
        transition_mask.par.cross = 1.0
        brush_guard.par.brightness1 = 0
        dim.par.value0 = 0

        if raw < COLOR_TO_MONO_PORTION:
            fade = _smootherstep01(raw / COLOR_TO_MONO_PORTION)
            mono.par.index = current
            color.par.index = current
            shape_guard.par.brightness1 = 1.0 - fade
            _set_audio_mix(current)
        else:
            season_fraction = _smootherstep01(
                (raw - COLOR_TO_MONO_PORTION) / (1.0 - COLOR_TO_MONO_PORTION)
            )
            index = float(current) + season_fraction
            mono.par.index = index
            color.par.index = index
            shape_guard.par.brightness1 = 0
            _set_audio_mix(current, next_season, season_fraction)

        if raw >= 1.0:
            current = next_season
            mono.par.index = current
            color.par.index = current
            transition_mask.par.cross = 0
            _reset_feedback()
            shape_guard.par.brightness1 = 1.0
            brush_guard.par.brightness1 = 1.5
            dim.par.value0 = 1
            parent_comp.store('auto_current_season', current)
            parent_comp.store('auto_state', 'sealed')
            parent_comp.store('state_started', now)
            parent_comp.store('auto_last_motion', now)
            _set_audio_mix(current)
        return

"""

text = text[:start] + new_block + text[end:]
controller.text = text

note_parent = op("/mosheng_project/00_control_panel")
note = note_parent.op("README_smooth_season_cycle") or note_parent.create("textDAT", "README_smooth_season_cycle")
note.text = (
    "Smooth season cycle:\n"
    "1. opening: current season reveal smoothly completes over 5.5s.\n"
    "2. turning: current color -> current mono -> next mono over 10s.\n"
    "3. motion brush is gated during turning; next season starts sealed mono.\n"
    "All reveal, season and audio transitions use smootherstep curves."
)

print("SMOOTH_SEASON_CYCLE_OK open=5.5s turn=10.0s color-to-mono=45%")
