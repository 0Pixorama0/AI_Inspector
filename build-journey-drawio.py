# -*- coding: utf-8 -*-
"""Build a draw.io user-journey diagram of the AI Device Inspector front end,
with an embedded screenshot of every screen and what-happens/what-next notes."""
import base64, io, os, html
from PIL import Image

SNIPS = r"C:\Users\udesh\AppData\Local\Temp\claude\C--Work\d63cc349-4626-43aa-8420-0c3668c0f23a\scratchpad\snips"
OUT   = r"C:\Work\Feature_List_AI_Inspector\AI-Device-Inspector-User-Journey.drawio"

VIOLET="#7C3AED"; BLUE="#3A33C9"; CYAN="#0E9AAC"; INK="#1A1B2E"; MUTED="#6A6C83"
CARD="#FFFFFF"; CARDLINE="#D9DCEA"; DESKBG="#F4F5FA"; BANNER="#0B0B1C"

IMG_W, IMG_H = 300, 188   # display size (16:10-ish)
TITLE_H = 34
DESC_H  = 132
COL = [40, 430, 820, 1210, 1600]
ROW = [150, 610, 1070]

def b64(fn):
    im=Image.open(os.path.join(SNIPS,fn)).convert("RGB").resize((480,300),Image.LANCZOS)
    buf=io.BytesIO(); im.save(buf,"JPEG",quality=74,optimize=True)
    return base64.b64encode(buf.getvalue()).decode()

def esc(s): return html.escape(s,quote=True)

# key, file, number, title, route, what-happens, what-next, col, row
S=[
 ("login","01-login.png","1","Sign in","/login",
  "Entry point. Operator, supervisor or admin authenticates by email + password (optional 2FA) or enterprise SSO (SAML/OIDC). Client chip shows the tenant.",
  "On success the user lands on their role home (Dashboard). A station kiosk starts a device-bound session with fast operator switching.",0,0),
 ("dashboard","02-dashboard.png","2","Dashboard & live floor","/dashboard",
  "Role home / hub. Live station tiles (idle / busy / offline), shift KPIs (units, cycle time, AI accuracy, defect & approval rate), trend + defect-mix charts and a live activity feed.",
  "Click a station or KPI to drill in; use the sidebar to reach any screen. Supervisors jump to review queues; admins to management.",1,0),
 ("import","07-import.png","7","Import wizard","/history/import",
  "Five-step CSV importer: download template, upload, map fields, validate, preview & commit. Reached from Inspection History.",
  "On commit, rows are created and the user returns to History with the new inspections listed.",2,0),
 ("station","03-station.png","3","Inspection Station","/station",
  "The operator's workflow. Six guided states shown on the right: 1 Scan barcode → 2 Verify asset → 3 Position device → 4 Capture (6 cameras) → 5 AI analysis → 6 Review. Live camera feed centre.",
  "A completed capture is sent to the model; detections come back and the operator moves to AI Review. Offline captures queue and sync on reconnect.",0,1),
 ("review","04-review.png","4","AI Review & annotation","/review",
  "Model output on the six images: bounding boxes, heat-map, zoom-to-defect. Right rail lists each detection with confidence & severity. Cursor tool resizes an AI box or draws a missed one; accept / reject / reclassify / merge.",
  "Every edit is audited and fed back to training. Approve Result → grade is set and the record is saved; Reject sends it back.",1,1),
 ("history","05-history.png","5","Inspection History","/history",
  "The master list: virtualised 16-column grid over 100k+ records, global search, advanced filters with saved presets, bulk actions (approve / reject / assign / archive / re-run AI / export) and role-gated inline editing.",
  "Click a row to open its full record; use Import to add rows; export the current view to CSV / XLSX / PDF / JSON.",2,1),
 ("detail","06-detail.png","6","Inspection Detail","/history/[id]",
  "One device's record across tabs — Overview, Images (drag-to-reorder), AI Results (defect viewer + health/grade), Audit Trail, Edit. Health score, cosmetic & functional grades and suggested disposition.",
  "Generate the branded PDF certificate (with tamper-evident hash) or an expiring share link for a buyer; supervisors override the grade with a reason.",3,1),
 ("analytics","08-analytics.png","8","Analytics","/analytics",
  "Management view: throughput, cycle time, first-pass yield & rework by station and shift, grade distribution over time, defect Pareto by supplier and AI-vs-human agreement.",
  "Filter by date range, export to CSV, or schedule an email digest. Findings drive taxonomy and grading-profile changes in Admin.",0,2),
 ("clients","09-clients.png","9","Clients","/clients",
  "Admin: manage client tenants — their branding, grading profiles and data isolation. Each client sees only their own consignments.",
  "Open a client to edit its grade profile or report branding; changes take effect without a release.",1,2),
 ("stations","10-stations.png","10","Stations","/stations",
  "Admin: register inspection stations and their six cameras, with calibration profiles and health/online status.",
  "Add or recalibrate a station; its live status then appears on the Dashboard floor view.",2,2),
 ("users","11-users.png","11","Users","/users",
  "Admin: manage user accounts and roles (Operator / Supervisor / Admin / Client) against the published permission matrix, enforced server-side.",
  "Invite or deactivate users, change roles; permissions apply immediately across every screen and the API.",3,2),
 ("settings","12-settings.png","12","Settings","/settings",
  "System: defect taxonomy & severity rules, grading-profile builder (with historic preview), notification rules, retention/erasure policy and per-tenant feature flags.",
  "Edits here reconfigure grading, capture and alerts across the platform — configuration, not a code release.",4,2),
]

# edges: (source, target, label)
E=[
 ("login","dashboard","Sign in → role home"),
 ("dashboard","station","Start / open a station"),
 ("station","review","Capture done → detections ready"),
 ("review","history","Approve / Reject → record saved"),
 ("history","detail","Click a row"),
 ("import","history","Commit CSV → rows added"),
 ("dashboard","history","View all inspections"),
 ("dashboard","analytics","Drill into metrics"),
 ("detail","analytics","Trends feed insight"),
]
# sidebar access (dashed) to admin/system
SIDE=[("dashboard","clients"),("dashboard","stations"),("dashboard","users"),("dashboard","settings")]

cells=[]
def cell(xml): cells.append(xml)

def pos(col,row):
    x=COL[col]; y=ROW[row]
    return x,y

for (key,fn,num,title,route,what,nxt,col,row) in S:
    x,y=pos(col,row)
    data=b64(fn)
    # title bar
    cell(f'<mxCell id="ttl_{key}" value="{esc(num+" · "+title)}" '
         f'style="rounded=1;arcSize=8;fillColor={VIOLET};strokeColor=none;fontColor=#ffffff;fontStyle=1;fontSize=13;fontFamily=Helvetica;align=left;spacingLeft=12;verticalAlign=middle;" '
         f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{IMG_W}" height="{TITLE_H}" as="geometry"/></mxCell>')
    # image
    cell(f'<mxCell id="img_{key}" value="" '
         f'style="shape=image;imageAspect=0;image=data:image/jpeg,{data};strokeColor={CARDLINE};" '
         f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y+TITLE_H+2}" width="{IMG_W}" height="{IMG_H}" as="geometry"/></mxCell>')
    # route chip
    cell(f'<mxCell id="rt_{key}" value="{esc(route)}" '
         f'style="text;html=1;align=right;verticalAlign=middle;fontColor={CYAN};fontSize=10;fontFamily=Courier New;fontStyle=1;" '
         f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{IMG_W-10}" height="{TITLE_H}" as="geometry"/></mxCell>')
    # description — build raw HTML, then escape the WHOLE thing for the XML attribute
    raw=(f'<b>What happens</b><br>{what}<br><br>'
         f'<b style="color:{VIOLET}">&#8594; Next</b><br>{nxt}')
    body=esc(raw)
    cell(f'<mxCell id="dsc_{key}" value="{body}" '
         f'style="rounded=1;arcSize=6;fillColor={CARD};strokeColor={CARDLINE};fontColor={INK};fontSize=11;fontFamily=Helvetica;align=left;verticalAlign=top;spacing=8;spacingLeft=10;spacingTop=8;whiteSpace=wrap;html=1;" '
         f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y+TITLE_H+IMG_H+6}" width="{IMG_W}" height="{DESC_H}" as="geometry"/></mxCell>')

eid=0
for (s,t,lab) in E:
    eid+=1
    cell(f'<mxCell id="e{eid}" value="{esc(lab)}" '
         f'style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor={VIOLET};strokeWidth=2;fontColor={INK};fontSize=10;fontFamily=Helvetica;endArrow=block;endFill=1;labelBackgroundColor=#ffffff;" '
         f'edge="1" parent="1" source="img_{s}" target="img_{t}"><mxGeometry relative="1" as="geometry"/></mxCell>')
for (s,t) in SIDE:
    eid+=1
    cell(f'<mxCell id="e{eid}" value="" '
         f'style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor={MUTED};strokeWidth=1;dashed=1;endArrow=open;endFill=0;" '
         f'edge="1" parent="1" source="img_{s}" target="img_{t}"><mxGeometry relative="1" as="geometry"/></mxCell>')

# banner + legend
cell(f'<mxCell id="banner" value="AI Device Inspector — Front-End User Journey" '
     f'style="text;html=1;align=left;verticalAlign=middle;fontColor={VIOLET};fontSize=26;fontStyle=1;fontFamily=Helvetica;" '
     f'vertex="1" parent="1"><mxGeometry x="40" y="40" width="900" height="40" as="geometry"/></mxCell>')
cell(f'<mxCell id="sub" value="Every screen, in the order a user moves through it. Solid arrows = primary flow &#183; dashed = sidebar access. Prepared by Pixorama." '
     f'style="text;html=1;align=left;verticalAlign=middle;fontColor={MUTED};fontSize=12;fontFamily=Helvetica;" '
     f'vertex="1" parent="1"><mxGeometry x="40" y="80" width="1100" height="24" as="geometry"/></mxCell>')
# phase labels down the left
for lab,ry in [("ENTRY &amp; HUB",ROW[0]),("OPERATIONS — the core loop",ROW[1]),("MANAGEMENT &amp; SYSTEM (admin)",ROW[2])]:
    cell(f'<mxCell id="ph_{ry}" value="{lab}" '
         f'style="text;html=1;align=left;verticalAlign=middle;fontColor={CYAN};fontSize=11;fontStyle=1;fontFamily=Courier New;rotation=-90;" '
         f'vertex="1" parent="1"><mxGeometry x="-70" y="{ry+90}" width="240" height="20" as="geometry"/></mxCell>')

body="\n".join(cells)
xml=(f'<mxfile host="app.diagrams.net" version="24.0.0">'
     f'<diagram name="Front-End User Journey" id="journey">'
     f'<mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" '
     f'arrows="1" fold="1" page="1" pageScale="1" pageWidth="1920" pageHeight="1400" background="{DESKBG}" math="0" shadow="0">'
     f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{body}</root>'
     f'</mxGraphModel></diagram></mxfile>')
open(OUT,"w",encoding="utf-8").write(xml)
print("saved",OUT)
print("screens:",len(S),"| edges:",len(E)+len(SIDE),"| size:",os.path.getsize(OUT)//1024,"KB")

# ---- companion HTML preview (flat, viewable / screenshottable) ----
bykey={s[0]:s for s in S}
order_ops=["station","review","history","detail"]
phases=[("Entry & hub",["login","dashboard","import"]),
        ("Operations — the core loop",order_ops),
        ("Management & system (admin)",["analytics","clients","stations","users","settings"])]
def card(key):
    k,fn,num,title,route,what,nxt,_,_=bykey[key]
    d=b64(fn)
    return (f'<div class="card"><div class="ttl"><span>{esc(num+" · "+title)}</span>'
            f'<code>{esc(route)}</code></div>'
            f'<img src="data:image/jpeg;base64,{d}"/>'
            f'<div class="d"><b>What happens</b><p>{esc(what)}</p>'
            f'<b class="nx">&#8594; Next</b><p>{esc(nxt)}</p></div></div>')
sections=""
for name,keys in phases:
    cards="<span class='arw'>&#8594;</span>".join(card(k) for k in keys)
    sections+=f'<div class="phase"><h2>{esc(name)}</h2><div class="row">{cards}</div></div>'
hp=f'''<!doctype html><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}body{{background:{DESKBG};font-family:Helvetica,Arial,sans-serif;padding:32px;color:{INK}}}
h1{{color:{VIOLET};font-size:28px}}.sub{{color:{MUTED};margin:6px 0 20px}}
.phase{{margin:26px 0}}.phase h2{{font:700 12px 'Courier New';letter-spacing:.15em;color:{CYAN};text-transform:uppercase;margin-bottom:12px}}
.row{{display:flex;align-items:stretch;gap:0;flex-wrap:wrap}}
.card{{width:300px;background:{CARD};border:1px solid {CARDLINE};border-radius:10px;overflow:hidden;margin:6px}}
.ttl{{background:{VIOLET};color:#fff;font-weight:700;font-size:13px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center}}
.ttl code{{color:#d9c9ff;font-size:10px;font-weight:400}}
.card img{{width:100%;display:block;border-bottom:1px solid {CARDLINE}}}
.d{{padding:10px 12px;font-size:11px}}.d b{{font-size:11px}}.d .nx{{color:{VIOLET}}}.d p{{color:#33354a;margin:3px 0 8px;line-height:1.45}}
.arw{{align-self:center;color:{VIOLET};font-size:26px;font-weight:700;padding:0 2px}}
</style><h1>AI Device Inspector — Front-End User Journey</h1>
<div class="sub">Every screen in the order a user moves through it, with what happens and what comes next.</div>
{sections}'''
HTMLOUT=OUT.replace(".drawio","-preview.html")
open(HTMLOUT,"w",encoding="utf-8").write(hp)
print("saved",HTMLOUT)
