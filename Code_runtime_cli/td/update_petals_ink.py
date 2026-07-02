"""Replace blocky specks with smooth flowing season-tinted ink traces."""
fx = op('/mosheng_project/08_motion_fx')
accum = fx.op('drift_accum')
dat = fx.op('drift_accum_pixeldat')
dat.text = '''out vec4 fragColor;
uniform vec4 params;  // x=decay y=driftSpeed z=emitThresh w=time
uniform vec4 scol;    // rgb=season color
float hash21(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
float vnoise(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
  return mix(mix(hash21(i),hash21(i+vec2(1,0)),f.x),
             mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),f.x), f.y); }
void main(){
  vec2 uv = vUV.st;
  vec2 ts = 1.0/vec2(textureSize(sTD2DInputs[1],0));
  float t = params.w;
  // Curl-ish flow, biased upward -> ink rises and curls like smoke/water.
  float ang = vnoise(uv*3.0 + vec2(0.0, t*0.35)) * 6.2831;
  vec2 curl = vec2(cos(ang), sin(ang)) * 0.45;
  vec2 drift = (vec2(0.0, 1.0) + curl) * params.y;
  vec2 suv = uv - drift * ts * 42.0;
  // Diffuse previous field (ink bleeding in water).
  vec4 p0 = texture(sTD2DInputs[1], suv);
  vec4 pl = texture(sTD2DInputs[1], suv + vec2(-ts.x*1.5, 0.0));
  vec4 pr = texture(sTD2DInputs[1], suv + vec2( ts.x*1.5, 0.0));
  vec4 pu = texture(sTD2DInputs[1], suv + vec2(0.0,  ts.y*1.5));
  vec4 pd = texture(sTD2DInputs[1], suv + vec2(0.0, -ts.y*1.5));
  vec4 prev = (p0*0.36 + (pl+pr+pu+pd)*0.16) * params.x;
  // Smoothly emit season-tinted ink where the hand moves.
  float m = texture(sTD2DInputs[0], uv).r;
  float e = smoothstep(params.z, params.z + 0.12, m);
  vec4 newc = vec4(scol.rgb, 1.0) * e;
  fragColor = TDOutputSwizzle(max(prev, newc));
}
'''
accum.par.vec0valuex = 0.965   # decay (a touch longer trails)
accum.par.vec0valuey = 0.55    # flow speed
accum.par.vec0valuez = 0.05    # emit threshold (real waves trigger)
blur = fx.op('drift_blur')
if blur:
    blur.par.size = 5.0
accum.cook(force=True)
print('petals -> smooth flowing ink; emitThresh=0.05, blur=5')
print('UPDATE_PETALS_INK_DONE')
