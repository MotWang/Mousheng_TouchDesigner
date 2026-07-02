"""Replace grid-tiled sprites with organic scattered falling leaves/snow.
Persists the comp_payoff input order (payoff over scene). Previews autumn peak."""
root = op('/mosheng_project')
comp = root.op('09_season_payoff')
field = comp.op('payoff_field')
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
      center.x += sin(t*1.1 + r.x*6.2831)*sway;
      float scl=szb*(0.35+0.8*r.y);
      float ang=t*(0.25+0.6*r.x) + r.y*6.2831;
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
  float cols=6.0, fall=0.14, sway=0.10, dens=0.55, szb=0.9, dir=1.0;
  if(se==1){ cols=5.0; fall=0.08; sway=0.22; dens=0.28; szb=0.8; dir=1.0; }
  else if(se==2){ cols=5.0; fall=0.05; sway=0.16; dens=0.32; szb=0.95; dir=-1.0; }
  else if(se==3){ cols=6.0; fall=0.13; sway=0.12; dens=0.55; szb=1.0; dir=1.0; }
  else if(se==4){ cols=8.0; fall=0.05; sway=0.08; dens=0.6; szb=0.5; dir=1.0; }
  vec4 l0=layer(uv,cols,     fall,     t,      dir,dens,    szb,    sway,    asp);
  vec4 l1=layer(uv,cols*1.7, fall*1.4, t+11.0, dir,dens*0.8,szb*0.7,sway*1.2,asp);
  l1.a*=0.8;
  vec4 acc; acc.rgb=mix(l1.rgb,l0.rgb,l0.a); acc.a=max(l0.a,l1.a);
  if(se==2){ float d=length((uv-0.5)*vec2(asp,1.0)); float gl=smoothstep(0.7,0.0,d)*0.28;
    acc.rgb=mix(acc.rgb,vec3(1.0,0.86,0.55),gl); acc.a=max(acc.a,gl*0.5); }
  if(se==4){ float veil=smoothstep(0.0,0.7,(1.0-uv.y))*0.30;
    acc.rgb=mix(acc.rgb,vec3(0.95,0.97,1.0),veil); acc.a=max(acc.a,veil); }
  acc*=env;
  fragColor=TDOutputSwizzle(acc);
}
'''
# persist comp_payoff order: payoff (input0) over scene (input1)
g = root.op('07_grade_and_frame')
cp = g.op('comp_payoff')
cp.inputConnectors[0].disconnect(); cp.inputConnectors[1].disconnect()
cp.inputConnectors[0].connect(g.op('IN_payoff'))
cp.inputConnectors[1].connect(g.op('hsv_vibrance_final'))

# preview autumn peak (driver paused, forced)
drv = comp.op('payoff_driver'); drv.par.frameend = False
comp.op('sprite_select').par.index = 2
field.par.vec0valuex = 1.0
field.par.vec0valuey = 3.0
field.cook(force=True)
op('/mosheng_project/07_grade_and_frame/OUT_final_projection_graded').save(project.folder + '/outputs/payoff_autumn2.png')
print('FIX_PAYOFF_SCATTER_DONE; field err:', list(field.errors()))
