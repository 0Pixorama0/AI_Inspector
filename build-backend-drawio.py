# -*- coding: utf-8 -*-
"""Backend architecture + data-flow diagram for the AI Device Inspector.
Emits a draw.io file and a matching HTML preview from one shared layout."""
import html, os

OUT   = r"C:\Work\Feature_List_AI_Inspector\AI-Device-Inspector-Backend.drawio"
HTMLOUT = OUT.replace(".drawio","-preview.html")

VIOLET="#7C3AED"; BLUE="#3A33C9"; CYAN="#0E9AAC"; MAGENTA="#B23FC9"
GREEN="#0F9D6B"; GREY="#6A6C83"; INK="#1A1B2E"; MUTED="#6A6C83"
CARD="#FFFFFF"; LINE="#D9DCEA"; DESK="#F4F5FA"
def esc(s): return html.escape(str(s),quote=True)

# geometry
COLX=[210,485,760,1035,1310,1585,1860]     # 7 columns (card 210 wide, 275 pitch)
ROWY=[120,320,520,760,980,1180]            # band card-top y per row
CW,CH=210,82
def cx(c): return COLX[c]+CW/2
def cy(r): return ROWY[r]+CH/2

# bands: row -> (name, accent)
BANDS=[
 ("CLIENTS",CYAN),
 ("EDGE NODE · on-site (one per facility)",MAGENTA),
 ("CORE API · cloud control plane",VIOLET),
 ("DATA & MODELS",BLUE),
 ("EXTERNAL SYSTEMS",GREY),
 ("PLATFORM & OPERATIONS (cross-cutting)",GREEN),
]
# components: id -> (title, sub, col, row)
C={
 "kiosk":("Station kiosk","Touch capture UI",0,0),
 "backoffice":("Back-office web","Supervisor / admin",1,0),
 "portal":("Client portal","Read-only buyer",2,0),
 "scanner":("Barcode / pedal","Asset-tag input",3,0),
 "printer":("Label printer","ZPL labels",4,0),

 "camera":("Camera controller","6× GigE trigger",0,1),
 "capture":("Capture service","Focus/exposure QA",1,1),
 "gpu":("GPU inference worker","TensorRT · ONNX",2,1),
 "cache":("Local image cache","Edge buffer",3,1),
 "syncq":("Offline sync queue","Store-and-forward",4,1),

 "api":("NestJS API","REST + OpenAPI",0,2),
 "auth":("Auth","OIDC/SAML · JWT",1,2),
 "ws":("WebSocket gateway","Live status/progress",2,2),
 "queue":("Job queue","Redis + BullMQ",3,2),
 "grading":("Grading engine","Profiles · rules",4,2),
 "outbox":("Webhook outbox","Signed · retried",5,2),
 "pdf":("PDF render worker","Headless Chromium",6,2),

 "pg":("PostgreSQL 16","Row-level security",0,3),
 "obj":("Object store","S3 / MinIO",1,3),
 "redis":("Redis","Queue · cache",2,3),
 "mlflow":("MLflow registry","Model versions",3,3),
 "lake":("Training data lake","Labelled corrections",4,3),

 "sso":("SSO IdP","Entra ID / Okta",0,4),
 "erp":("ERP / WMS","Records out",1,4),
 "buyer":("Buyer feed","SFTP / S3 cron",2,4),

 "platform":("Docker · Terraform · GitHub Actions","Reproducible deploys",0,5),
 "otel":("OpenTelemetry → Grafana · Sentry","Traces · errors",2,5),
 "backup":("Nightly PITR backups","30-day window",4,5),
}
ACCENT_BY_ROW=[CYAN,MAGENTA,VIOLET,BLUE,GREY,GREEN]

# flows: (from, to, label, number or "", dashed)
FLOW=[
 ("kiosk","auth","Sign in","1",False),
 ("auth","sso","OIDC / SAML","",True),
 ("kiosk","obj","Presigned image upload","2",False),
 ("kiosk","api","Create inspection","3",False),
 ("api","pg","write · RLS","",False),
 ("api","queue","Enqueue inference","4",False),
 ("queue","gpu","Run model","5",False),
 ("gpu","obj","pull images","",True),
 ("gpu","api","Detections + version","",False),
 ("api","ws","","",False),
 ("ws","backoffice","Live status","6",False),
 ("api","grading","Grade from profile","7",False),
 ("grading","pg","grade + audit","",False),
 ("api","pdf","Certificate","8",False),
 ("pdf","obj","store PDF","",True),
 ("outbox","erp","Push record (webhook)","",False),
 ("api","buyer","Scheduled feed","9",False),
 ("pg","lake","Corrections","10",False),
 ("lake","mlflow","train / evaluate","",True),
 ("mlflow","gpu","promote model","",True),
 ("queue","redis","","",True),
 ("api","otel","traces","",True),
]

LIFECYCLE=[
 ("1","Sign in","Client authenticates via SSO (OIDC/SAML); the API issues a short-lived JWT. Row-level security ties every query to the tenant."),
 ("2","Capture upload","The station uploads six images straight to object storage using presigned URLs — the heavy bytes never transit the API."),
 ("3","Create inspection","The station calls the NestJS API, which writes the inspection record to PostgreSQL under row-level security."),
 ("4","Enqueue","The API places an inference job on the Redis / BullMQ queue (retryable, ordered)."),
 ("5","Inference","The on-site GPU worker pulls the images, runs the TensorRT model, and returns detections (stamped with model version) to the API → Postgres."),
 ("6","Realtime","The API pushes station status and analysis progress over the WebSocket gateway to the dashboard and station."),
 ("7","Grade","Operator corrections hit the API; the grading engine applies the client's grade profile and writes the grade plus an immutable audit entry."),
 ("8","Report & hand-off","The PDF worker renders the certificate to object storage; the transactional outbox delivers signed webhooks to the ERP/WMS; buyer feeds go to SFTP/S3."),
 ("9","Buyer feed","Scheduled exports are pushed to the buyer's SFTP or S3 bucket on a cron."),
 ("10","Retrain loop","Operator corrections flow to the training data lake; MLflow trains and evaluates a candidate; a model that beats the incumbent is promoted to the edge worker."),
]

# ---------------- draw.io ----------------
cells=[]
def cell(x): cells.append(x)
# bands (behind)
BX,BW=60,2010
for r,(name,accent) in enumerate(BANDS):
    y=ROWY[r]-26; h=CH+52
    cell(f'<mxCell id="band{r}" value="" style="rounded=1;arcSize=4;fillColor={DESK};strokeColor={accent};strokeWidth=1;dashed=1;opacity=60;" vertex="1" parent="1"><mxGeometry x="{BX}" y="{y}" width="{BW}" height="{h}" as="geometry"/></mxCell>')
    cell(f'<mxCell id="bl{r}" value="{esc(name)}" style="text;html=1;align=left;verticalAlign=top;fontColor={accent};fontStyle=1;fontSize=11;fontFamily=Courier New;spacingLeft=6;" vertex="1" parent="1"><mxGeometry x="{BX+8}" y="{y+4}" width="{BW-16}" height="16" as="geometry"/></mxCell>')
# cards
for cid,(title,sub,col,row) in C.items():
    accent=ACCENT_BY_ROW[row]; x=COLX[col]; y=ROWY[row]
    w=CW if row!=5 else (CW+120)  # cross-cutting cards a bit wider
    val=(f'<b style="color:{accent}">{esc(title)}</b><br><span style="color:{MUTED};font-size:10px">{esc(sub)}</span>')
    cell(f'<mxCell id="{cid}" value="{esc(val)}" style="rounded=1;arcSize=10;fillColor={CARD};strokeColor={accent};strokeWidth=1.5;fontColor={INK};fontSize=12;fontFamily=Helvetica;align=left;verticalAlign=middle;spacingLeft=10;whiteSpace=wrap;html=1;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{CH}" as="geometry"/></mxCell>')
# edges
eid=0
for (s,t,lab,num,dashed) in FLOW:
    eid+=1
    txt=(f"{num} · {lab}" if num and lab else (num or lab))
    stroke = MUTED if dashed else VIOLET
    dash = "dashed=1;" if dashed else ""
    sw = 1 if dashed else 2
    cell(f'<mxCell id="fe{eid}" value="{esc(txt)}" style="edgeStyle=orthogonalEdgeStyle;rounded=1;{dash}strokeColor={stroke};strokeWidth={sw};endArrow=block;endFill=1;fontColor={INK};fontSize=10;fontFamily=Helvetica;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="{s}" target="{t}"><mxGeometry relative="1" as="geometry"/></mxCell>')
# banner
cell(f'<mxCell id="banner" value="AI Device Inspector — Backend Architecture &amp; Data Flow" style="text;html=1;align=left;fontColor={VIOLET};fontSize=24;fontStyle=1;fontFamily=Helvetica;" vertex="1" parent="1"><mxGeometry x="60" y="20" width="1200" height="34" as="geometry"/></mxCell>')
cell(f'<mxCell id="sub" value="Solid violet = primary request lifecycle (numbered 1–10) &#183; dashed = async / events / model promotion. Prepared by Pixorama." style="text;html=1;align=left;fontColor={MUTED};fontSize=12;fontFamily=Helvetica;" vertex="1" parent="1"><mxGeometry x="60" y="56" width="1400" height="20" as="geometry"/></mxCell>')
# lifecycle legend panel (right/bottom)
ly=ROWY[5]+CH+70
lines="".join(f'<b style="color:{VIOLET}">{n}</b> &#183; <b>{esc(t)}</b> — {esc(d)}<br>' for n,t,d in LIFECYCLE)
cell(f'<mxCell id="legend" value="{esc("<b>Request lifecycle</b><br><br>"+lines)}" style="rounded=1;arcSize=3;fillColor={CARD};strokeColor={LINE};fontColor={INK};fontSize=11;fontFamily=Helvetica;align=left;verticalAlign=top;spacing=12;whiteSpace=wrap;html=1;" vertex="1" parent="1"><mxGeometry x="60" y="{ly}" width="2010" height="230" as="geometry"/></mxCell>')

body="\n".join(cells)
xml=(f'<mxfile host="app.diagrams.net" version="24.0.0"><diagram name="Backend Architecture" id="backend">'
     f'<mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" '
     f'pageScale="1" pageWidth="2200" pageHeight="1600" background="{DESK}" math="0" shadow="0">'
     f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{body}</root></mxGraphModel></diagram></mxfile>')
open(OUT,"w",encoding="utf-8").write(xml)
print("saved",OUT,"| components:",len(C),"| flows:",len(FLOW),"| size:",os.path.getsize(OUT)//1024,"KB")

# ---------------- HTML preview (SVG arrows, matching coords) ----------------
SCALE=0.62
def sx(x): return x*SCALE
def sy(y): return y*SCALE
Wpx=int(2140*SCALE); Hpx=int((ROWY[5]+CH+330)*SCALE)
# card divs
divs=""
for cid,(title,sub,col,row) in C.items():
    accent=ACCENT_BY_ROW[row]; x=COLX[col]; y=ROWY[row]; w=CW if row!=5 else CW+120
    divs+=(f'<div class="c" style="left:{sx(x)}px;top:{sy(y)}px;width:{sx(w)}px;height:{sy(CH)}px;border-left-color:{accent}">'
           f'<b style="color:{accent}">{esc(title)}</b><span>{esc(sub)}</span></div>')
band_divs=""
for r,(name,accent) in enumerate(BANDS):
    y=ROWY[r]-26; h=CH+52
    band_divs+=(f'<div class="band" style="left:{sx(BX)}px;top:{sy(y)}px;width:{sx(BW)}px;height:{sy(h)}px;border-color:{accent}">'
                f'<span style="color:{accent}">{esc(name)}</span></div>')
# svg arrows
def anchor(cid):
    _,_,col,row=C[cid]; w=CW if row!=5 else CW+120
    return COLX[col]+w/2, ROWY[row]+CH/2
segs=""
for (s,t,lab,num,dashed) in FLOW:
    x1,y1=anchor(s); x2,y2=anchor(t)
    x1,y1,x2,y2=sx(x1),sy(y1),sx(x2),sy(y2)
    col=MUTED if dashed else VIOLET
    da='stroke-dasharray="5 4"' if dashed else ''
    sw=1.3 if dashed else 2
    segs+=f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{col}" stroke-width="{sw}" {da} marker-end="url(#a)"/>'
    if num:
        mx,my=(x1+x2)/2,(y1+y2)/2
        segs+=f'<circle cx="{mx:.0f}" cy="{my:.0f}" r="9" fill="{VIOLET}"/><text x="{mx:.0f}" y="{my+3:.0f}" fill="#fff" font-size="10" font-weight="700" text-anchor="middle">{num}</text>'
life="".join(f'<div class="li"><span class="n">{n}</span><b>{esc(t)}</b> — {esc(d)}</div>' for n,t,d in LIFECYCLE)
hp=f'''<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}body{{background:{DESK};font-family:Helvetica,Arial,sans-serif;color:{INK};padding:24px}}
h1{{color:{VIOLET};font-size:24px}}.sub{{color:{MUTED};margin:6px 0 14px;font-size:13px}}
.stage{{position:relative;width:{Wpx}px;height:{Hpx}px}}
svg{{position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none}}
.band{{position:absolute;border:1px dashed;border-radius:6px;opacity:.5}}
.band span{{font:700 10px 'Courier New';position:absolute;top:3px;left:6px;letter-spacing:.08em}}
.c{{position:absolute;background:{CARD};border:1px solid {LINE};border-left:4px solid;border-radius:8px;padding:6px 9px;display:flex;flex-direction:column;justify-content:center;box-shadow:0 1px 3px rgba(0,0,0,.05)}}
.c b{{font-size:12px;line-height:1.2}}.c span{{color:{MUTED};font-size:9.5px;margin-top:2px}}
.legend{{margin-top:20px;background:{CARD};border:1px solid {LINE};border-radius:8px;padding:16px 18px;max-width:1300px}}
.legend h3{{color:{VIOLET};margin-bottom:10px}}
.li{{font-size:12px;line-height:1.5;margin:5px 0;padding-left:30px;position:relative;color:#33354a}}
.li .n{{position:absolute;left:0;top:0;background:{VIOLET};color:#fff;font-weight:700;font-size:10px;width:18px;height:18px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center}}
.li b{{color:{INK}}}
</style>
<h1>AI Device Inspector — Backend Architecture &amp; Data Flow</h1>
<div class="sub">Solid violet = primary request lifecycle (1–10) &#183; dashed = async / events / model promotion.</div>
<div class="stage">{band_divs}<svg viewBox="0 0 {Wpx} {Hpx}"><defs>
<marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="{VIOLET}"/></marker>
</defs>{segs}</svg>{divs}</div>
<div class="legend"><h3>Request lifecycle</h3>{life}</div>'''
open(HTMLOUT,"w",encoding="utf-8").write(hp)
print("saved",HTMLOUT)
