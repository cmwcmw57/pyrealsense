from pathlib import Path
import json,math,csv
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
R=Path(__file__).resolve().parent;p=json.loads((R/'parameters.json').read_text());rad=p['wheel_d']/2000;G=p['rail_centers']/1000;L=p['wheelbase']/1000;v=p['design_speed_kmh']/3.6;ratio=p['stage1_large']/p['stage1_small']*p['stage2_large']/p['stage2_small'];eta=p['chain_efficiency_each']**2
rpm=v/(2*math.pi*rad)*60;mrpm=rpm*ratio
rows=[]
for grade in [0,20,35,50,80]:
 for acc in [0,.3]:
  theta=math.atan(grade/1000);normal=p['total_mass_for_force']*9.81*math.cos(theta);F=p['total_mass_for_force']*9.81*math.sin(theta)+normal*p['assumed_Crr']+p['total_mass_for_force']*acc
  tq=F*rad;rows.append({'grade_permille':grade,'acceleration_m_s2':acc,'tractive_force_N':F,'rear_axle_torque_Nm':tq,'required_motor_torque_Nm':tq/(ratio*eta),'required_motor_shaft_power_W_at20kmh':F*v/eta,'minimum_mu_rear50percent_load':F/(normal*.5)})
with (R/'reports/Traction_screen.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
curves=[]
for rr in [15,25,50,100,200]:
 # common axle equal-rpm pure rolling requires r_out/r_in=(R+G/2)/(R-G/2).
 delta=rad*G/rr;shift=delta/(2*p['wheel_taper']);available=2*p['wheel_taper']*p['guide_gap']/1000
 curves.append({'radius_m':rr,'bogie_yaw_deg':math.degrees(math.asin(L/(2*rr))),'each_wheel_slip_ratio_if_equal_radii':G/(2*rr),'slip_speed_each_m_s_at20kmh':v*G/(2*rr),'rolling_radius_difference_needed_mm':delta*1000,'conical_lateral_shift_needed_mm':shift*1000,'available_radius_difference_at1mm_guide_gap_mm':available*1000,'ideal_guide_sagitta_mm':((rr-G/2)-math.sqrt((rr-G/2)**2-(p['guide_station']/1000)**2))*1000,'status':'Yaw removes attack-angle mismatch; equal-rpm slip remains. No pass certification'})
with (R/'reports/Curve_equalRPM_screen.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=curves[0]);w.writeheader();w.writerows(curves)
summary={'wheel_rpm_at20kmh':rpm,'motor_output_shaft_rpm_required_at20kmh':mrpm,'external_reduction':ratio,'two_chain_efficiency_assumed':eta,'rated_motor_power_W_catalogue':p['motor_power'],'theoretical_motor_torque_if_2kW_available_at_required_rpm_Nm':p['motor_power']/(mrpm*2*math.pi/60),'available_continuous_torque_at_rpm':'NOT VERIFIED: OEM curve required','no_load_rpm_catalogue':3200,'no_load_geometric_speed_kmh':3200/ratio*2*math.pi*rad*60/1000,'rear_axle_screen_torque_limit_Nm':60,'axle_D40_nominal_shear_at60Nm_MPa':16*60000/(math.pi*40**3),'curve_dynamics_validated':False,'pitch_roll_pose_track_contact_validated':False,'reverse_power_validated':False,'bogie_yaw_alignment':'No linkage/actuator designed; passive aligning moment not validated'}
(R/'reports/Drive_sizing.json').write_text(json.dumps(summary,indent=2))
with PdfPages(R/'drawings/Engineering_screen.pdf') as pdf:
 fig,axs=plt.subplots(1,2,figsize=(12,7));q=[r for r in rows if r['acceleration_m_s2']==0];axs[0].plot([r['grade_permille'] for r in q],[r['required_motor_shaft_power_W_at20kmh'] for r in q],'o-');axs[0].axhline(2000,color='red',ls='--',label='catalogue2kW, operating curve unverified');axs[0].set(xlabel='grade permille',ylabel='Required motor shaft W',title='200kg, Crr0.02, eta0.9025 assumed');axs[0].legend(fontsize=8);axs[0].grid();axs[1].plot([r['radius_m'] for r in curves],[r['each_wheel_slip_ratio_if_equal_radii']*100 for r in curves],'o-');axs[1].set(xlabel='curve radius m',ylabel='Each wheel nominal slip %',title='Common axle: SAME RPM, equal rolling radii');axs[1].grid();fig.suptitle('STEADY FORCE AND KINEMATIC SCREEN ONLY');pdf.savefig(fig);fig.savefig(R/'drawings/Engineering_screen.png',dpi=150);plt.close(fig)
print(summary)
