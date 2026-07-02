"""Whisper-quiet, colorless ink wisps. Anti-flicker, won't overpower the painting.
- Neutral ink grey (no saturated color competing with the art)
- Gradual growth + high decay => no strobing/flicker
- 'over' blend (adds faint ink, never brightens), opacity ~0.12
"""
fx = op('/mosheng_project/08_motion_fx')
accum = fx.op('drift_accum')
dat = fx.op('drift_accum_pixeldat')
blur = fx.op('drift_blur')
lvl = fx.op('petals_opacity')
comp = op('/mosheng_project/07_grade_and_frame/comp_motion_petals')

dat.text = '''out vec4 fragColor;
uniform vec4 params;  // x=decay y=driftSpeed z=emitThresh w=time
float hash21(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
float vnoise(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
  return mix(mix(hash21(i),hash21(i+vec2(1,0)),f.x),
             mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),f.x), f.y); }
void main(){
  vec2 uv = vUV.st;
  vec2 ts = 1.0/vec2(textureSize(sTD2DInputs[1],0));
  float t = params.w;
  float ang = vnoise(uv*3.0 + vec2(0.0, t*0.3)) * 6.2831;
  vec2 curl = vec2(cos(ang), sin(ang)) * 0.4;
  vec2 drift = (vec2(0.0, 1.0) + curl) * params.y;
  vec2 suv = uv - drift * ts * 34.0;
  // diffuse previous density (stored in alpha)
  float p0 = texture(sTD2DInputs[1], suv).a;
  float pl = texture(sTD2DInputs[1], suv + vec2(-ts.x*1.5,0.0)).a;
  float pr = texture(sTD2DInputs[1], suv + vec2( ts.x*1.5,0.0)).a;
  float pu = texture(sTD2DInputs[1], suv + vec2(0.0, ts.y*1.5)).a;
  float pd = texture(sTD2DInputs[1], suv + vec2(0.0,-ts.y*1.5)).a;
  float prev = (p0*0.40 + (pl+pr+pu+pd)*0.15) * params.x;
  // smoothed, gradual emission -> no flash, no flicker
  float m = texture(sTD2DInputs[0], uv).r;
  float e = smoothstep(params.z, params.z + 0.25, m);
  float ink = clamp(prev + e * 0.05 * (1.0 - prev), 0.0, 1.0);
  vec3 inkcol = vec3(0.10, 0.10, 0.13);   // neutral deep ink, faint cool
  fragColor = TDOutputSwizzle(vec4(inkcol, ink));
}
'''
accum.par.vec0valuex = 0.985   # slow decay -> stable, no flicker
accum.par.vec0valuey = 0.40    # gentle drift
accum.par.vec0valuez = 0.12    # only deliberate motion
accum.cook(force=True)

if blur:
    blur.par.size = 4.0

# 'over' so the ink only deepens tone (never adds color or brightness)
if comp is not None and hasattr(comp.par, 'operand'):
    comp.par.operand = 'over'

# very low opacity, gated by Petalsenable
if lvl is not None and hasattr(lvl.par, 'opacity'):
    try:
        lvl.par.opacity.expr = "0.12 * op('/mosheng_project/08_motion_fx').par.Petalsenable"
    except Exception:
        lvl.par.opacity = 0.12

fx.par.Petalsenable = 1
print('REDESIGN_SUBTLE_INK_DONE  (neutral ink, opacity 0.12, anti-flicker)')
