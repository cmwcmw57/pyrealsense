from pathlib import Path
import json,math,csv
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
R=Path(__file__).resolve().parent;p=json.loads((R/'chassis_parameters.json').read_text());L=p['wheelbase_mm']/1000;a=p['guide_half_pitch_mm']/1000;g=p['guide_gap_mm']/1000;v=p['speed_kmh']/3.6;G=p['rail_center_spacing_mm']/1000
rows=[]
for rad in [25,50,100,150,200,300,500]:
 for sy in [-1,1]:
  r=rad+sy*G/2;x=L/2
  f=lambda xx:r-math.sqrt(r*r-xx*xx)
  err=[f(x+z)-f(x) for z in [-a,a]]
  required=(max(err)-min(err))/2
  rows.append({'center_radius_m':rad,'rail_radius_m':r,'wheel_yaw_required_deg':math.degrees(math.asin(x/r)),'guide_mismatch_centered_mm':max(abs(e) for e in err)*1000,'guide_min_gap_after_optimal_lateral_shift_mm':required*1000,'gap_1mm_geometry_pass':required<=g,'inner_outer_speed_difference_percent':100*G/rad,'lateral_acceleration_m_s2':v*v/rad,'note':'Geometric screen only; tolerance/PU/loaded dynamics not included'})
with (R/'Curve_screen.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
grades=[]
for grade in [0,10,20,35,50,80]:
 t=math.atan(grade/1000);normal=p['mass_for_traction_kg']*9.81*math.cos(t);grav=p['mass_for_traction_kg']*9.81*math.sin(t);F=grav+normal*p['rolling_resistance_assumed'];rear=normal*p['rear_normal_fraction_assumed']
 grades.append({'grade_permille':grade,'grade_percent':grade/10,'angle_deg':math.degrees(t),'wheel_torque_each_Nm':F*p['tire_radius_mm']/1000/2,'total_mechanical_power_W':F*v,'minimum_mu_assumed_rear_half_load':F/rear,'gravity_only_downhill_force_N':grav,'note':'steady speed; no acceleration, motor map, thermal limit, wet grip or braking validation'})
with (R/'Grade_screen.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=grades[0]);w.writeheader();w.writerows(grades)
with PdfPages(R/'Route_checks.pdf') as pdf:
 fig,axs=plt.subplots(1,2,figsize=(12,7));rads=sorted(set(row['center_radius_m'] for row in rows));errs=[max(r['guide_min_gap_after_optimal_lateral_shift_mm'] for r in rows if r['center_radius_m']==rad) for rad in rads]
 axs[0].plot(rads,errs,'o-');axs[0].axhline(1,color='red',label='nominal side gap1mm');axs[0].set(xlabel='Curve center radius m',ylabel='Minimum guide gap required mm',title='Rigid module / L=1m, guide pitch440mm');axs[0].legend();axs[0].grid()
 axs[1].plot([r['grade_permille'] for r in grades],[r['wheel_torque_each_Nm'] for r in grades],'o-');axs[1].set(xlabel='Grade permille',ylabel='Required torque per drive wheel Nm',title='200kg / steady20kmh / Crr=0.02 assumed');axs[1].grid();fig.suptitle('KINEMATIC AND STEADY FORCE SCREEN / NOT A DYNAMIC SIMULATION');pdf.savefig(fig);fig.savefig(R/'Route_summary.png',dpi=150);plt.close(fig)
 fig,ax=plt.subplots(figsize=(12,7))
 # magnify local right-front guide deviations without concealing scale.
 for rad in [25,50,100,200]:
  rr=rad-G/2;xs=[L/2-a+i*(2*a)/100 for i in range(101)];yy=[(rr-math.sqrt(rr*rr-x*x)-(rr-math.sqrt(rr*rr-(L/2)**2)))*1000 for x in xs];ax.plot([x*1000 for x in xs],yy,label=f'R={rad}m')
 ax.axhline(1,color='red',ls='--');ax.axhline(-1,color='red',ls='--');ax.scatter([(L/2-a)*1000,(L/2+a)*1000],[0,0],label='Rigid module guide stations');ax.set(xlabel='X from chassis center mm',ylabel='Rail side displacement relative to wheel mm',title='Front inner module / rigid orientation / lateral scale magnified');ax.legend();ax.grid();pdf.savefig(fig);fig.savefig(R/'Curve_guide_detail.png',dpi=150);plt.close(fig)
print('Route screen generated')
