from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
from matplotlib.backends.backend_pdf import PdfPages
R=Path(__file__).resolve().parent
with PdfPages(R/'drawings/Turned_parts_drafts.pdf') as pdf:
 fig,axs=plt.subplots(2,1,figsize=(11.7,8.3))
 ax=axs[0];pts=[(0,-6),(38,-6),(38,-7.5),(86,-7.5),(86,-6),(124,-6),(124,6),(86,6),(86,7.5),(38,7.5),(38,6),(0,6)]
 ax.add_patch(Polygon(pts,fill=False));ax.axhline(0,ls='-.',lw=.5,color='grey')
 ax.text(3,11,'M12x1.75 x38',fontsize=10);ax.text(45,11,'D15 bearing seat x48',fontsize=10);ax.text(90,11,'M12x1.75 x38',fontsize=10)
 ax.annotate('',xy=(124,-14),xytext=(0,-14),arrowprops=dict(arrowstyle='<->'));ax.text(62,-14,'124 overall',ha='center',va='bottom')
 ax.set_xlim(-5,130);ax.set_ylim(-20,24);ax.set_aspect('equal');ax.set_title('G06 Spindle / C45 (S45C) / thread relief and bearing fit TO BE APPROVED')
 ax=axs[1]
 outer=[(0,-21),(28,-21),(28,21),(0,21)];inside=[(0,-16),(9,-16),(9,-12),(19,-12),(19,-16),(28,-16),(28,16),(19,16),(19,12),(9,12),(9,16),(0,16)]
 ax.add_patch(Polygon(outer,fill=False));ax.add_patch(Polygon(inside,facecolor='white',edgecolor='black'))
 ax.annotate('',xy=(28,-26),xytext=(0,-26),arrowprops=dict(arrowstyle='<->'));ax.text(14,-26,'28',ha='center');ax.text(2,25,'D42 core / two D32 bearing seats, depth9 each / middle boreD24',fontsize=9)
 ax.text(40,15,'6002DDU:15x32x9 (two per roller)\nInner spacer OD21/ID15.2/L10\nEnd spacers OD21/ID15.2/L10, two per roller\nPU90A finished OD50; radial crown0.5\nOuter race retention and seat fit: supplier review',fontsize=10,va='top')
 ax.set_xlim(-5,150);ax.set_ylim(-32,34);ax.set_aspect('equal');ax.set_title('G02 Core axial section / 6061-T6 / bearing seats finish-machine after bonding')
 for ax in axs:ax.set_xlabel('mm');ax.grid(alpha=.15)
 fig.suptitle('TURNED PARTS - MACHINING DRAFT, NOT RELEASED');fig.tight_layout();pdf.savefig(fig);fig.savefig(R/'drawings/08_Turned_parts.png',dpi=160);plt.close(fig)
print('Turned part draft complete')
