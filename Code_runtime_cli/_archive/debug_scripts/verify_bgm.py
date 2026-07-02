"""Verify BGM playback/loop/gain state."""
AUD = op('/mosheng_project/04_audio_reactivity')
ctrl = op('/mosheng_project/00_control_panel')
active = ctrl.fetch('auto_current_season', '?') if ctrl else '?'
print('active_season_index:', active)
for s in ('spring', 'summer', 'autumn', 'winter'):
    n = AUD.op('bgm_' + s)
    if n is None:
        print(s, 'MISSING'); continue
    looppars = [p.name + '=' + str(p.eval()) for p in n.pars()
                if any(k in p.name.lower() for k in ('loop', 'repeat', 'cue', 'play'))]
    g = AUD.op('bgm_' + s + '_gain')
    gain = g.par.gain.eval() if (g and hasattr(g.par, 'gain')) else 'NA'
    nchan = n.numChans
    print('bgm_%-6s' % s, '| file=', n.par.file.eval().split('/')[-1],
          '| nchan=', nchan, '| gain=', gain, '|', looppars)
ado = AUD.op('audio_device_out')
print('audio_device_out:', ado.type if ado else None,
      '| active par=', (ado.par.active.eval() if (ado and hasattr(ado.par, 'active')) else 'NA'))
print('VERIFY_BGM_DONE')
