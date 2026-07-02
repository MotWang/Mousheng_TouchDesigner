"""Refine for classical elegance:
- restore brighter grade (undo exposure pullback)
- smaller spring/autumn elements, slightly translucent
- guzheng pentatonic chime as the payoff 'special' sound (per season)
"""
root = op('/mosheng_project')


def sp(node, name, value):
    if node is None:
        return
    p = getattr(node.par, name, None)
    if p is not None:
        try:
            p.val = value
        except Exception:
            pass


# ---- 1. brighter, richer grade (restore the fuller look) ----
g = root.op('07_grade_and_frame')
lf = g.op('level_final_grade')
sp(lf, 'brightness1', 1.05)
sp(lf, 'outhigh', 1.0)
sp(lf, 'contrast', 1.05)
sp(lf, 'gamma1', 0.95)
v = g.op('hsv_vibrance_final')
sp(v, 'saturationmult', 1.18)
sp(v, 'valuemult', 1.03)
b = g.op('bloom_restrained')
sp(b, 'bloomthreshold', 0.72)
sp(b, 'bloomintensity', 0.22)
lc = root.op('02_visual_assets/level_color_rich')
sp(lc, 'gamma1', 0.97)

# ---- 2. shader: smaller spring/autumn + slight translucency ----
comp = root.op('09_season_payoff')
dat = comp.op('payoff_field_pixeldat')
dat.text = '''out vec4 fragColor;
uniform vec4 P;   // x=env y=season z=time w=aspect
vec2 h22(vec2 p){ return fract(sin(vec2(dot(p,vec2(127.1,311.7)),dot(p,vec2(269.5,183.3))))*43758.5453); }
mat2 rot(float a){ float c=cos(a),s=sin(a); return mat2(c,-s,s,c); }
vec4 layer(vec2 uv,float sg,float spd,float t,float dir,float dens,float szb,float sway,float asp){
  vec2 g=uv*vec2(sg*asp,sg);
  g.y += dir*t*spd*sg;
  vec2 base=floor(g);
  vec4 acc=vec4(0.0);
  for(int dy=-1;dy<=1;dy++){
    for(int dx=-1;dx<=1;dx++){
      vec2 cell=base+vec2(float(dx),float(dy));
      vec2 r=h22(cell);
      if(r.x>dens) continue;
      vec2 j=(h22(cell+5.3)-0.5)*0.9;
      vec2 center=cell+vec2(0.5)+j;
      center.x += sin(t*1.0 + r.x*6.2831)*sway;
      float scl=szb*(0.35+0.8*r.y);
      float ang=t*(0.22+0.5*r.x) + r.y*6.2831;
      vec2 pc=rot(ang)*(g-center);
      vec2 loc=pc/max(scl,0.001)+0.5;
      if(loc.x<0.0||loc.x>1.0||loc.y<0.0||loc.y>1.0) continue;
      vec4 s=texture(sTD2DInputs[0], loc);
      acc.rgb=mix(acc.rgb,s.rgb,s.a);
      acc.a=max(acc.a,s.a);
    }
  }
  return acc;
}
void main(){
  vec2 uv=vUV.st; float env=P.x; int se=int(P.y+0.5); float t=P.z; float asp=P.w;
  if(env<=0.001){ fragColor=vec4(0.0); return; }
  float cols=6.0, fall=0.13, sway=0.10, dens=0.55, szb=0.9, dir=1.0;
  if(se==1){ cols=7.0; fall=0.08; sway=0.20; dens=0.30; szb=0.40; dir=1.0; }   // spring small
  else if(se==2){ cols=5.0; fall=0.05; sway=0.15; dens=0.30; szb=0.85; dir=-1.0; }
  else if(se==3){ cols=7.0; fall=0.12; sway=0.11; dens=0.52; szb=0.55; dir=1.0; } // autumn smaller
  else if(se==4){ cols=9.0; fall=0.05; sway=0.08; dens=0.58; szb=0.45; dir=1.0; }
  vec4 l0=layer(uv,cols,     fall,     t,      dir,dens,    szb,    sway,    asp);
  vec4 l1=layer(uv,cols*1.7, fall*1.4, t+11.0, dir,dens*0.8,szb*0.7,sway*1.2,asp);
  l1.a*=0.8;
  vec4 acc; acc.rgb=mix(l1.rgb,l0.rgb,l0.a); acc.a=max(l0.a,l1.a);
  acc.a *= 0.90;   // a touch translucent for delicacy
  if(se==2){ float d=length((uv-0.5)*vec2(asp,1.0)); float gl=smoothstep(0.7,0.0,d)*0.26;
    acc.rgb=mix(acc.rgb,vec3(1.0,0.87,0.58),gl); acc.a=max(acc.a,gl*0.5); }
  if(se==4){ float veil=smoothstep(0.0,0.7,(1.0-uv.y))*0.28;
    acc.rgb=mix(acc.rgb,vec3(0.96,0.98,1.0),veil); acc.a=max(acc.a,veil); }
  // faint warm gold dust for autumn (classical accent)
  if(se==3){ vec2 q=uv*vec2(220.0*asp,220.0); vec2 r=h22(floor(q));
    float dust=step(0.985,r.x)*smoothstep(0.5,0.0,length(fract(q)-0.5));
    acc.rgb=mix(acc.rgb,vec3(1.0,0.84,0.45),dust*0.7); acc.a=max(acc.a,dust*0.6); }
  acc*=env;
  fragColor=TDOutputSwizzle(acc);
}
'''

# ---- 3. driver: guzheng chime as the special payoff sound ----
drv = comp.op('payoff_driver')
drv.text = '''import math
COMP = '/mosheng_project/09_season_payoff'
DUR = 5.0

def _coverage():
    for p in ('/mosheng_project/00_control_panel/reveal_coverage_value',
              '/mosheng_project/03_ink_reveal_composite/reveal_coverage_value'):
        n = op(p)
        if n is not None and n.numChans:
            try:
                return float(n[0].eval())
            except Exception:
                pass
    return 0.0

def _season():
    c = op('/mosheng_project/00_control_panel')
    try:
        return int(c.fetch('auto_current_season', 1))
    except Exception:
        return 1

def _play_sound(season):
    a = op('/mosheng_project/04_audio_reactivity/fx_payoff')
    if a is None:
        return
    names = {1: 'payoff_spring.wav', 2: 'payoff_summer.wav',
             3: 'payoff_autumn.wav', 4: 'payoff_winter.wav'}
    base = project.folder + '/assets/mosheng/audio/payoff/'
    a.par.file = base + names.get(season, 'payoff_autumn.wav')
    a.par.volume = 0.34
    try:
        a.par.cuepulse.pulse(); a.par.play = True
    except Exception:
        pass

def onFrameEnd(frame):
    comp = op(COMP)
    field = comp.op('payoff_field')
    if field is None:
        return
    if not comp.par.Payoffenable.eval():
        field.par.vec0valuex = 0.0
        return
    cov = _coverage()
    now = absTime.seconds
    armed = comp.fetch('payoff_armed', True)
    start = comp.fetch('payoff_start', -100.0)
    if armed and cov >= 0.9:
        start = now
        comp.store('payoff_start', now)
        comp.store('payoff_season', _season())
        comp.store('payoff_armed', False)
        _play_sound(_season())
    if cov < 0.3:
        comp.store('payoff_armed', True)
    te = (now - start) / DUR
    env = math.sin(te * math.pi) if 0.0 <= te <= 1.0 else 0.0
    field.par.vec0valuex = max(0.0, env)
    field.par.vec0valuey = float(comp.fetch('payoff_season', _season()))
    return
'''
fxp = root.op('04_audio_reactivity/fx_payoff')
sp(fxp, 'file', project.folder + '/assets/mosheng/audio/payoff/payoff_autumn.wav')
sp(fxp, 'volume', 0.34)

# ---- 4. preview spring & autumn (smaller) ----
field = comp.op('payoff_field')
swt = comp.op('sprite_select')
out = g.op('OUT_final_projection_graded')
drv.par.frameend = False
ebak = swt.par.index.expr
swt.par.index.expr = ''
field.par.vec0valuex = 1.0
for s, name in ((1, 'spring'), (3, 'autumn')):
    swt.par.index = s - 1
    field.par.vec0valuey = float(s)
    field.cook(force=True)
    out.cook(force=True)
    out.save(project.folder + '/outputs/refine_%s.png' % name)
    print('saved refine_%s.png' % name)
swt.par.index.expr = ebak
field.par.vec0valuex = 0.0
drv.par.frameend = True
print('REFINE_PAYOFF_DONE')
