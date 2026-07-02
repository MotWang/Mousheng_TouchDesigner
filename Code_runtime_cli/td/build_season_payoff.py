"""Season payoff: when the painting reaches full color, a season-specific
sprite animation bursts from the frame (spring willow leaves / summer lotus
bloom / autumn maple fill / winter snow) over ~5s, then fades back to the art.

Self-contained module 09_season_payoff + a frame driver reading reveal coverage.
Composited into 07 just before the final level. Has a Payoffenable toggle.
Idempotent.
"""
ROOT = '/mosheng_project'
SPR = project.folder + '/assets/mosheng/sprites/'


def sp(node, name, value):
    if node is None:
        return
    p = getattr(node.par, name, None)
    if p is not None:
        try:
            p.val = value
        except Exception:
            pass


def expr(node, name, e):
    p = getattr(node.par, name, None)
    if p is not None:
        try:
            p.expr = e
        except Exception:
            pass


def ensure(parent, typ, name, x, y):
    o = parent.op(name) or parent.create(typ, name)
    o.nodeX, o.nodeY = x, y
    return o


def conn(dst, idx, src):
    try:
        dst.inputConnectors[idx].disconnect()
    except Exception:
        pass
    dst.inputConnectors[idx].connect(src)


root = op(ROOT)
comp = root.op('09_season_payoff') or root.create('baseCOMP', '09_season_payoff')
comp.nodeX, comp.nodeY = 100, -1500

# enable toggle
try:
    if not hasattr(comp.par, 'Payoffenable'):
        comp.appendCustomPage('Mosheng').appendToggle('Payoffenable', label='Payoff Enable')
    comp.par.Payoffenable = 1
except Exception:
    pass

# --- sprites (spring willow / summer petal / autumn maple / winter snow) ---
files = ['spring_willow.png', 'summer_petal.png', 'autumn_maple.png', 'winter_snow.png']
swt = ensure(comp, 'switchTOP', 'sprite_select', -500, 100)
for i, fn in enumerate(files):
    m = ensure(comp, 'moviefileinTOP', 'spr_%d' % i, -780, 240 - i * 130)
    sp(m, 'file', SPR + fn)
    conn(swt, i, m)
# index = current season - 1
expr(swt, 'index', "max(0,min(3,int(op('/mosheng_project/00_control_panel').fetch('auto_current_season',1))-1))")

# --- GLSL falling-sprite field ---
field = ensure(comp, 'glslTOP', 'payoff_field', -280, 100)
sp(field, 'outputresolution', 'custom')
sp(field, 'resolutionw', 1280)
sp(field, 'resolutionh', 720)
sp(field, 'format', 'rgba16float')
conn(field, 0, swt)
sp(field, 'vec0name', 'P')          # x=env y=season z=time w=aspect
sp(field, 'vec0valuex', 0.0)
sp(field, 'vec0valuey', 3.0)
expr(field, 'vec0valuez', 'absTime.seconds')
sp(field, 'vec0valuew', 1280.0 / 720.0)

dat = ensure(comp, 'textDAT', 'payoff_field_pixeldat', -280, -120)
dat.text = '''out vec4 fragColor;
uniform vec4 P;   // x=env y=season z=time w=aspect
vec2 h22(vec2 p){ return fract(sin(vec2(dot(p,vec2(127.1,311.7)),dot(p,vec2(269.5,183.3))))*43758.5453); }
mat2 rot(float a){ float c=cos(a),s=sin(a); return mat2(c,-s,s,c); }
vec4 spr(vec2 loc, float scale, float ang){
  vec2 p=(loc-0.5)/max(scale,0.001); p=rot(ang)*p; vec2 uv=p+0.5;
  if(uv.x<0.0||uv.x>1.0||uv.y<0.0||uv.y>1.0) return vec4(0.0);
  return texture(sTD2DInputs[0], uv);
}
void main(){
  vec2 uv=vUV.st; float env=P.x; int se=int(P.y+0.5); float t=P.z; float asp=P.w;
  if(env<=0.001){ fragColor=vec4(0.0); return; }
  float cols=8.0, fall=0.14, sway=0.10, dens=0.95, szb=0.95, dir=1.0;
  if(se==1){ cols=6.0; fall=0.07; sway=0.20; dens=0.45; szb=0.75; dir=1.0; }
  else if(se==2){ cols=6.0; fall=0.05; sway=0.14; dens=0.50; szb=0.85; dir=-1.0; }
  else if(se==3){ cols=8.0; fall=0.14; sway=0.10; dens=0.95; szb=0.95; dir=1.0; }
  else if(se==4){ cols=10.0; fall=0.05; sway=0.07; dens=0.92; szb=0.55; dir=1.0; }
  vec4 acc=vec4(0.0);
  for(int L=0; L<3; L++){
    float lf=float(L);
    float sg=cols*(1.0+lf*0.5);
    float spd=fall*(1.0+lf*0.4);
    vec2 g=uv*vec2(sg*asp, sg);
    g.y += dir*t*spd*sg;
    vec2 cell=floor(g), loc=fract(g);
    vec2 rnd=h22(cell+lf*37.0);
    if(rnd.x>dens) continue;
    float scl=szb*(0.5+0.7*rnd.y);
    float ang=t*(0.4+rnd.x) + rnd.y*6.2831 + sin(t*0.7+rnd.x*6.2831)*0.3;
    loc.x += sin(t*1.3 + rnd.x*6.2831)*sway;
    vec4 s=spr(loc, scl, ang);
    s.a *= (1.0-lf*0.22);
    acc.rgb=mix(acc.rgb, s.rgb, s.a);
    acc.a=max(acc.a, s.a);
  }
  if(se==2){ // summer bloom radiance
    float d=length((uv-0.5)*vec2(asp,1.0));
    float glow=smoothstep(0.65,0.0,d)*0.30;
    acc.rgb=mix(acc.rgb, vec3(1.0,0.86,0.55), glow);
    acc.a=max(acc.a, glow*0.6);
  }
  if(se==4){ // winter veil rising from bottom
    float veil=smoothstep(0.0,0.65,(1.0-uv.y))*0.32;
    acc.rgb=mix(acc.rgb, vec3(0.95,0.97,1.0), veil);
    acc.a=max(acc.a, veil);
  }
  acc *= env;
  fragColor=TDOutputSwizzle(acc);
}
'''
sp(field, 'pixeldat', dat.path)

out = ensure(comp, 'nullTOP', 'OUT_payoff', -60, 100)
conn(out, 0, field)

# --- composite into 07 (over the graded scene, before final level) ---
grade = root.op('07_grade_and_frame')
hsv = grade.op('hsv_vibrance_final')
lf = grade.op('level_final_grade')
inpay = ensure(grade, 'selectTOP', 'IN_payoff', lf.nodeX - 30, lf.nodeY - 170)
sp(inpay, 'top', '../09_season_payoff/OUT_payoff')
cpay = ensure(grade, 'compositeTOP', 'comp_payoff', lf.nodeX - 150, lf.nodeY)
sp(cpay, 'outputresolution', 'custom')
sp(cpay, 'resolutionw', 1280)
sp(cpay, 'resolutionh', 720)
sp(cpay, 'operand', 'over')
conn(cpay, 0, inpay)   # payoff on top
conn(cpay, 1, hsv)     # scene below
conn(lf, 0, cpay)

# --- frame driver: watch coverage, fire payoff envelope ---
drv = comp.op('payoff_driver') or comp.create('executeDAT', 'payoff_driver')
drv.nodeX, drv.nodeY = 200, 100
try:
    drv.par.frameend = True
except Exception:
    pass
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
    files = {1: 'ambient_spring_birdsong.mp4', 2: 'fx_water_drop.mp4',
             3: 'ambient_autumn_wind_leaves.mp4', 4: 'ambient_winter_snow.mp4'}
    base = project.folder + '/assets/mosheng/audio/new_fx/'
    a.par.file = base + files.get(season, 'fx_brush.mp4')
    a.par.volume = 0.22
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

# --- payoff sound node (added to audio mix if possible) ---
AUD = root.op('04_audio_reactivity')
fxp = AUD.op('fx_payoff') or AUD.create('audiofileinCHOP', 'fx_payoff')
fxp.nodeX, fxp.nodeY = -1000, -560
sp(fxp, 'file', project.folder + '/assets/mosheng/audio/new_fx/ambient_autumn_wind_leaves.mp4')
sp(fxp, 'volume', 0.22)
sp(fxp, 'play', False)
mix = AUD.op('audio_mix')
if mix is not None:
    try:
        n = len(mix.inputs)
        if fxp not in mix.inputs:
            mix.inputConnectors[n].connect(fxp)
    except Exception:
        pass

print('SEASON PAYOFF built; driver live, Payoffenable=1')
print('BUILD_SEASON_PAYOFF_DONE')
