import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from lib import *
from reportlab.lib.pagesizes import letter, landscape
def build(path):
    W,H=landscape(letter)
    C=canvas_for('Tablero de control')
    c=C(path,pagesize=(W,H))
    draw_tablero(c,28,H-34-372,W-56,372)
    c.showPage(); c.save()
if __name__=='__main__':
    build(os.path.join(os.environ.get('ARGOS_SALIDA','.'),'Tablero_'+d.NUMF+'.pdf'))
