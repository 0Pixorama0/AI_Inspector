# -*- coding: utf-8 -*-
"""Data ingestion + interpretation diagram for the AI Device Inspector.
How data comes IN, and how raw pixels are INTERPRETED into a grade.
Emits a draw.io file and a matching HTML preview from one shared layout."""
import html, os
OUT=r"C:\Work\Feature_List_AI_Inspector\AI-Device-Inspector-Data-Flow.drawio"
HTMLOUT=OUT.replace(".drawio","-preview.html")

VIOLET="#7C3AED"; BLUE="#3A33C9"; CYAN="#0E9AAC"; MAGENTA="#B23FC9"
GREEN="#0F9D6B"; GREY="#6A6C83"; INK="#1A1B2E"; MUTED="#6A6C83"
CARD="#FFFFFF"; LINE="#D9DCEA"; DESK="#F4F5FA"
def esc(s): return html.escape(str(s),quote=True)

COLX=[200,475,750,1025,1300,1575,1850]
ROWY=[130,360,650,860]
ROWH=[84,108,84,70]
CW=210

BANDS=[("HOW DATA ARRIVES · ingestion channels",CYAN),
       ("HOW DATA IS INTERPRETED · raw pixels → decision",VIOLET),
       ("OUTPUTS · where interpreted data goes",GREEN),
       ("DATA AT REST · storage",BLUE)]
ACCENT=[CYAN,VIOLET,GREEN,BLUE]

# id -> (title, sub_html, col, row)
C={
 # ingestion
 "cam":("Device cameras","6 angles &#8594; raw images",0,0),
 "scan":("Scanner + OCR","barcode / service tag &#8594; identity",1,0),
 "lookup":("Device lookup / ERP","model, spec, warranty, consignment",2,0),
 "op":("Operator actions","accept / reject / draw &#8594; corrections",3,0),
 "csv":("CSV import wizard","bulk intake / historical records",4,0),
 "cfg":("Admin config","taxonomy &#183; grade profiles &#183; rules",5,0),
 "tel":("Station telemetry","camera health &#183; calibration",6,0),
 # interpretation pipeline
 "v":("S1 · Capture & validate","<i>in</i> 6 raw frames<br><i>out</i> accepted, in-focus frames",0,1),
 "pp":("S2 · Pre-process","<i>in</i> frames<br><i>out</i> isolated &#183; corrected &#183; normalised tiles",1,1),
 "inf":("S3 · Inference","<i>in</i> tiles<br><i>out</i> raw detections (class, conf, region, severity)",2,1),
 "post":("S4 · Post-process","<i>in</i> raw detections<br><i>out</i> deduped &#183; gated detection set",3,1),
 "rev":("S5 · Human review","<i>in</i> detection set<br><i>out</i> confirmed set + ground-truth labels",4,1),
 "grd":("S6 · Grading","<i>in</i> confirmed set + profile<br><i>out</i> grades &#183; 0–100 health &#183; disposition",5,1),
 "agg":("S7 · Aggregate","<i>in</i> many graded records<br><i>out</i> KPIs &#183; Pareto &#183; agreement &#183; trends",6,1),
 # outputs
 "gout":("Grade & disposition","resell / repair / parts / recycle",0,2),
 "cert":("Certificate (PDF) + audit","tamper-evident record",1,2),
 "erpout":("ERP / WMS record","signed webhook",2,2),
 "feed":("Buyer feed","SFTP / S3 export",3,2),
 "ana":("Analytics","dashboards &#183; digest",4,2),
 "train":("Training data lake","labelled corrections &#8594; next model",5,2),
 # storage
 "objs":("Object store","raw + processed images",0,3),
 "pgs":("PostgreSQL (RLS)","records &#183; detections &#183; grades &#183; audit",2,3),
 "lakes":("Data lake","training labels",4,3),
 "mlf":("MLflow","model versions",5,3),
}

# (from,to,label,dashed)
FLOW=[
 ("cam","v","raw images",False),
 ("v","pp","",False),("pp","inf","",False),("inf","post","",False),
 ("post","rev","",False),("rev","grd","",False),("grd","agg","",False),
 # non-image ingestion into the record / stages
 ("scan","pgs","identity",True),
 ("lookup","pgs","reference metadata",True),
 ("op","rev","corrections",False),
 ("csv","pgs","bulk records",True),
 ("cfg","inf","taxonomy · thresholds",True),
 ("cfg","grd","grade profiles",True),
 ("tel","ana","station health",True),
 # storage read/write
 ("inf","objs","images",True),
 ("grd","pgs","grades + audit",True),
 # outputs
 ("grd","gout","",False),("grd","cert","",False),("grd","erpout","",False),
 ("grd","feed","",False),("agg","ana","",False),
 # feedback loop
 ("rev","train","corrections",False),
 ("train","lakes","",True),("lakes","mlf","train / evaluate",True),
 ("mlf","inf","promote model",True),
]

INGEST=[
 ("Images","Six camera frames per device, uploaded to object storage via presigned URLs — the heavy bytes never transit the API."),
 ("Identity","Barcode / QR plus OCR service-tag reading resolves exactly which device is on the fixture."),
 ("Reference","Model, spec, warranty and consignment metadata pulled from device lookup / the ERP."),
 ("Corrections","Operator accept / reject / reclassify / draw actions during review — the human signal."),
 ("Bulk","CSV import wizard for historical or intake records that skip the vision pipeline."),
 ("Config","Taxonomy, grade profiles and rules from admin — these shape how later stages interpret."),
 ("Telemetry","Station and camera health, calibration and status."),
]
INTERP=[
 ("S1","Capture & validate","Six raw frames in; focus/exposure QA rejects and re-shoots bad frames. Only clean frames pass."),
 ("S2","Pre-process","Device isolation, perspective correction, normalisation and tiling — frames become model-ready tiles."),
 ("S3","Inference","The fine-tuned model segments and classifies each defect: class, confidence, region, severity, heat map."),
 ("S4","Post-process","Non-max suppression, cross-angle de-duplication, confidence gating and severity mapping clean the raw output."),
 ("S5","Human review","The operator confirms, corrects or adds detections. The confirmed set is both the record and new ground truth."),
 ("S6","Grading","The confirmed defects run through the client's grade profile to produce cosmetic/functional grades, a health score and a disposition."),
 ("S7","Aggregate","Many graded records roll up into throughput, yield, defect Pareto by supplier and AI-vs-human agreement."),
]

# ---------- draw.io ----------
cells=[]
def cell(x): cells.append(x)
BX,BW=60,2050
for r,(name,accent) in enumerate(BANDS):
    y=ROWY[r]-26; h=ROWH[r]+52
    cell(f'<mxCell id="band{r}" value="" style="rounded=1;arcSize=4;fillColor={DESK};strokeColor={accent};dashed=1;opacity=60;" vertex="1" parent="1"><mxGeometry x="{BX}" y="{y}" width="{BW}" height="{h}" as="geometry"/></mxCell>')
    cell(f'<mxCell id="bl{r}" value="{esc(name)}" style="text;html=1;align=left;verticalAlign=top;fontColor={accent};fontStyle=1;fontSize=11;fontFamily=Courier New;" vertex="1" parent="1"><mxGeometry x="{BX+8}" y="{y+4}" width="{BW-16}" height="16" as="geometry"/></mxCell>')
for cid,(title,sub,col,row) in C.items():
    accent=ACCENT[row]; x=COLX[col]; y=ROWY[row]; h=ROWH[row]
    val=f'<b style="color:{accent}">{title}</b><br><span style="color:{MUTED};font-size:10px">{sub}</span>'
    cell(f'<mxCell id="{cid}" value="{esc(val)}" style="rounded=1;arcSize=10;fillColor={CARD};strokeColor={accent};strokeWidth=1.5;fontColor={INK};fontSize=12;fontFamily=Helvetica;align=left;verticalAlign=middle;spacingLeft=9;whiteSpace=wrap;html=1;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{CW}" height="{h}" as="geometry"/></mxCell>')
eid=0
for (s,t,lab,dashed) in FLOW:
    eid+=1
    stroke=MUTED if dashed else VIOLET; dash="dashed=1;" if dashed else ""; sw=1 if dashed else 2
    cell(f'<mxCell id="fe{eid}" value="{esc(lab)}" style="edgeStyle=orthogonalEdgeStyle;rounded=1;{dash}strokeColor={stroke};strokeWidth={sw};endArrow=block;endFill=1;fontColor={INK};fontSize=10;fontFamily=Helvetica;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="{s}" target="{t}"><mxGeometry relative="1" as="geometry"/></mxCell>')
cell(f'<mxCell id="banner" value="AI Device Inspector — Data Ingestion &amp; Interpretation" style="text;html=1;align=left;fontColor={VIOLET};fontSize=24;fontStyle=1;fontFamily=Helvetica;" vertex="1" parent="1"><mxGeometry x="60" y="20" width="1300" height="34" as="geometry"/></mxCell>')
cell(f'<mxCell id="sub" value="Left/top = how data enters &#183; centre = the S1–S7 interpretation pipeline (raw pixels &#8594; grade) &#183; dashed = config, storage &amp; the retrain feedback loop." style="text;html=1;align=left;fontColor={MUTED};fontSize=12;fontFamily=Helvetica;" vertex="1" parent="1"><mxGeometry x="60" y="56" width="1500" height="20" as="geometry"/></mxCell>')
ly=ROWY[3]+ROWH[3]+60
# raw HTML here — the whole panel value is esc()'d once below (mirrors the card pattern)
inlines="".join(f'<b style="color:{CYAN}">{t}</b> — {d}<br>' for t,d in INGEST)
splines="".join(f'<b style="color:{VIOLET}">{n} {t}</b> — {d}<br>' for n,t,d in INTERP)
cell(f'<mxCell id="legA" value="{esc("<b>How data comes to the platform</b><br><br>"+inlines)}" style="rounded=1;fillColor={CARD};strokeColor={LINE};fontColor={INK};fontSize=11;fontFamily=Helvetica;align=left;verticalAlign=top;spacing=12;whiteSpace=wrap;html=1;" vertex="1" parent="1"><mxGeometry x="60" y="{ly}" width="1000" height="220" as="geometry"/></mxCell>')
cell(f'<mxCell id="legB" value="{esc("<b>How data is interpreted</b><br><br>"+splines)}" style="rounded=1;fillColor={CARD};strokeColor={LINE};fontColor={INK};fontSize=11;fontFamily=Helvetica;align=left;verticalAlign=top;spacing=12;whiteSpace=wrap;html=1;" vertex="1" parent="1"><mxGeometry x="1090" y="{ly}" width="1020" height="220" as="geometry"/></mxCell>')

body="\n".join(cells)
xml=(f'<mxfile host="app.diagrams.net" version="24.0.0"><diagram name="Data Ingestion &amp; Interpretation" id="dataflow">'
     f'<mxGraphModel dx="1400" dy="900" grid="0" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" '
     f'pageScale="1" pageWidth="2240" pageHeight="1400" background="{DESK}" math="0" shadow="0">'
     f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{body}</root></mxGraphModel></diagram></mxfile>')
open(OUT,"w",encoding="utf-8").write(xml)
print("saved",OUT,"| components:",len(C),"| flows:",len(FLOW),"| size:",os.path.getsize(OUT)//1024,"KB")

# ---------- HTML preview ----------
SCALE=0.62
def sx(x): return x*SCALE
def sy(y): return y*SCALE
Wpx=int(2180*SCALE); Hpx=int((ROWY[3]+ROWH[3]+40)*SCALE)
band_divs=""
for r,(name,accent) in enumerate(BANDS):
    y=ROWY[r]-26; h=ROWH[r]+52
    band_divs+=f'<div class="band" style="left:{sx(BX)}px;top:{sy(y)}px;width:{sx(BW)}px;height:{sy(h)}px;border-color:{accent}"><span style="color:{accent}">{esc(name)}</span></div>'
divs=""
for cid,(title,sub,col,row) in C.items():
    accent=ACCENT[row]; x=COLX[col]; y=ROWY[row]; h=ROWH[row]
    divs+=(f'<div class="c" style="left:{sx(x)}px;top:{sy(y)}px;width:{sx(CW)}px;height:{sy(h)}px;border-left-color:{accent}">'
           f'<b style="color:{accent}">{title}</b><span>{sub}</span></div>')
def anchor(cid):
    _,_,col,row=C[cid]; return COLX[col]+CW/2, ROWY[row]+ROWH[row]/2
segs=""
for (s,t,lab,dashed) in FLOW:
    x1,y1=anchor(s); x2,y2=anchor(t); x1,y1,x2,y2=sx(x1),sy(y1),sx(x2),sy(y2)
    col=MUTED if dashed else VIOLET; da='stroke-dasharray="5 4"' if dashed else ''; sw=1.2 if dashed else 2
    segs+=f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{col}" stroke-width="{sw}" {da} marker-end="url(#a)"/>'
inL="".join(f'<div class="li"><b style="color:{CYAN}">{esc(t)}</b> — {esc(d)}</div>' for t,d in INGEST)
spL="".join(f'<div class="li"><b style="color:{VIOLET}">{n} {esc(t)}</b> — {esc(d)}</div>' for n,t,d in INTERP)
hp=f'''<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}body{{background:{DESK};font-family:Helvetica,Arial,sans-serif;color:{INK};padding:24px}}
h1{{color:{VIOLET};font-size:24px}}.sub{{color:{MUTED};margin:6px 0 14px;font-size:13px}}
.stage{{position:relative;width:{Wpx}px;height:{Hpx}px}}
svg{{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}}
.band{{position:absolute;border:1px dashed;border-radius:6px;opacity:.5}}
.band span{{font:700 10px 'Courier New';position:absolute;top:3px;left:6px;letter-spacing:.06em}}
.c{{position:absolute;background:{CARD};border:1px solid {LINE};border-left:4px solid;border-radius:8px;padding:5px 8px;display:flex;flex-direction:column;justify-content:center;box-shadow:0 1px 3px rgba(0,0,0,.05)}}
.c b{{font-size:11.5px;line-height:1.15}}.c span{{color:{MUTED};font-size:9px;margin-top:2px;line-height:1.3}}
.c span i{{font-style:normal;color:{VIOLET};font-weight:700;margin-right:3px}}
.cols{{display:flex;gap:18px;margin-top:18px;flex-wrap:wrap}}
.legend{{flex:1;min-width:440px;background:{CARD};border:1px solid {LINE};border-radius:8px;padding:14px 16px}}
.legend h3{{margin-bottom:8px;font-size:14px}}.li{{font-size:11.5px;line-height:1.45;margin:4px 0;color:#33354a}}
</style>
<h1>AI Device Inspector — Data Ingestion &amp; Interpretation</h1>
<div class="sub">Top = how data enters &#183; centre = the S1–S7 interpretation pipeline (raw pixels &#8594; grade) &#183; dashed = config, storage & retrain loop.</div>
<div class="stage">{band_divs}<svg viewBox="0 0 {Wpx} {Hpx}"><defs>
<marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="{VIOLET}"/></marker></defs>{segs}</svg>{divs}</div>
<div class="cols"><div class="legend"><h3 style="color:{CYAN}">How data comes to the platform</h3>{inL}</div>
<div class="legend"><h3 style="color:{VIOLET}">How data is interpreted</h3>{spL}</div></div>'''
open(HTMLOUT,"w",encoding="utf-8").write(hp)
print("saved",HTMLOUT)
