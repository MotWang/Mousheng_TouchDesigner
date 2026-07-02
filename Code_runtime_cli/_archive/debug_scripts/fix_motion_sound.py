"""Quieter, non-repetitive, season-matched motion SFX. Reversible.
- fx_ink_heavy volume 0.45 -> 0.20
- _ink_sound: motion gate 0.035 -> 0.08, debounce 0.60s -> 2.0s
- season-matched motion FX file (spring flower / summer water / autumn brush / winter ink)
"""
AUD = op('/mosheng_project/04_audio_reactivity')
fx = AUD.op('fx_ink_heavy')
if fx is not None and hasattr(fx.par, 'volume'):
    print('fx volume', fx.par.volume.eval(), '-> 0.2')
    fx.par.volume = 0.2

ctrl = op('/mosheng_project/00_control_panel/automation_heartbeat_controller')
t = ctrl.text
i = t.find('def _ink_sound(')
j = t.find('return motion', i)
if i < 0 or j < 0:
    raise Exception('could not locate _ink_sound')
j = t.find('\n', j) + 1

new_func = (
    "def _ink_sound(now, parent_comp):\n"
    "    last = parent_comp.fetch('last_ink_sound', 0.0)\n"
    "    motion_node = _node('../04_audio_reactivity/motion_mask_to_chop')\n"
    "    motion = motion_node['motion'].eval() if motion_node and motion_node['motion'] else 0.0\n"
    "    sound = _node('../04_audio_reactivity/fx_ink_heavy')\n"
    "    season = int(parent_comp.fetch('auto_current_season', 1))\n"
    "    fxmap = {1: 'fx_flower.mp4', 2: 'fx_water_drop.mp4', 3: 'fx_brush.mp4', 4: 'fx_ink_diffusion.mp4'}\n"
    "    if sound and parent_comp.fetch('last_fx_season', 0) != season:\n"
    "        sound.par.file = project.folder + '/assets/mosheng/audio/new_fx/' + fxmap.get(season, 'fx_ink_diffusion.mp4')\n"
    "        sound.par.volume = 0.2\n"
    "        parent_comp.store('last_fx_season', season)\n"
    "    # Only real, sustained motion; long debounce so it never machine-guns.\n"
    "    if motion >= 0.08 and now - last >= 2.0:\n"
    "        if sound:\n"
    "            sound.par.cuepulse.pulse()\n"
    "            sound.par.play = True\n"
    "        parent_comp.store('last_ink_sound', now)\n"
    "    return motion\n"
)
ctrl.text = t[:i] + new_func + t[j:]
print('rewrote _ink_sound (gate 0.08, debounce 2.0s, season-matched, vol 0.2)')
print('FIX_MOTION_SOUND_DONE')
