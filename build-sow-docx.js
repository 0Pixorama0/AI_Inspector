/* Generate the AI Device Inspector Statement of Work as a branded .docx.
   Run: node build-sow-docx.js  →  AI-Device-Inspector-SOW.docx           */

const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  TableOfContents, PageBreak, Header, Footer, PageNumber, TabStopType,
  TabStopPosition, LevelFormat, Numbering,
} = require("docx");

/* ---- brand palette ---- */
const INK="0D0E1A", INK2="33354A", MUTED="6A6C83", FAINT="8A8CA0";
const VIOLET="7C3AED", BLUE="3A33C9", CYAN="0E9AAC", MAGENTA="B23FC9";
const LINE="D9DCEA", PAPER2="F4F5FA", VIOLETBG="F1ECFD", DARK="0B0B1C";
const OK="0F9D6B", WARN="B7791F", CRIT="D64545";

const FONT="Calibri", MONO="Consolas";
const CW = 9026; // content width (A4, 1" margins) in DXA

/* ---- helpers ---- */
const noBorder={ top:{style:BorderStyle.NONE},bottom:{style:BorderStyle.NONE},left:{style:BorderStyle.NONE},right:{style:BorderStyle.NONE} };
const hair=(c=LINE)=>({ style:BorderStyle.SINGLE, size:4, color:c });

function eyebrow(text,color=CYAN){
  return new Paragraph({ spacing:{ before:60, after:40 },
    children:[ new TextRun({ text:text.toUpperCase(), font:MONO, size:15, color, characterSpacing:60, bold:true }) ]});
}
function h1(num,title){
  return new Paragraph({ heading:HeadingLevel.HEADING_1, spacing:{ before:60, after:120 },
    children:[
      new TextRun({ text:num+"  ", font:MONO, size:26, color:VIOLET, bold:true }),
      new TextRun({ text:title, font:FONT, size:30, color:INK, bold:true }),
    ]});
}
function h2(title){
  return new Paragraph({ heading:HeadingLevel.HEADING_2, spacing:{ before:220, after:90 },
    children:[ new TextRun({ text:title, font:FONT, size:21, color:INK, bold:true }) ]});
}
function lead(text){
  return new Paragraph({ spacing:{ after:140 }, children:[ new TextRun({ text, font:FONT, size:21, color:INK2 }) ]});
}
function body(text,opts={}){
  return new Paragraph({ spacing:{ after:opts.after??100 },
    children:[ new TextRun({ text, font:FONT, size:20, color:opts.color??INK2 }) ]});
}
function bullet(text){
  return new Paragraph({ bullet:{ level:0 }, spacing:{ after:50 },
    children:[ new TextRun({ text, font:FONT, size:20, color:INK2 }) ]});
}
function rule(){
  return new Paragraph({ spacing:{ before:40, after:160 }, border:{ bottom:hair(VIOLET) }, children:[ new TextRun({ text:"", size:2 }) ]});
}
function spacer(sz=120){ return new Paragraph({ spacing:{ after:sz }, children:[ new TextRun({ text:"" }) ]}); }

/* generic table builder: header row + body rows, DXA widths */
function tbl(colW, headers, rows, opts={}){
  const total=colW.reduce((a,b)=>a+b,0);
  const cell=(txt,w,o={})=>new TableCell({
    width:{ size:w, type:WidthType.DXA },
    margins:{ top:70, bottom:70, left:110, right:110 },
    shading:o.shade?{ type:ShadingType.CLEAR, fill:o.shade, color:"auto" }:undefined,
    verticalAlign:"top",
    children:(Array.isArray(txt)?txt:[txt]).map(t=>
      typeof t==="string"
        ? new Paragraph({ children:[ new TextRun({ text:t, font:o.mono?MONO:FONT, size:o.size??18,
            bold:o.bold??false, color:o.color??INK2 }) ], alignment:o.align })
        : t ),
  });
  const headRow=new TableRow({ tableHeader:true, children:headers.map((h,i)=>
    cell(h,colW[i],{ shade:PAPER2, bold:true, size:15, mono:true, color:MUTED,
      align:(opts.rightCols||[]).includes(i)?AlignmentType.RIGHT:undefined }))});
  const bodyRows=rows.map(r=>new TableRow({ children:r.map((c,i)=>{
    const spec=(opts.colSpec&&opts.colSpec[i])||{};
    return cell(c,colW[i],{ ...spec, align:(opts.rightCols||[]).includes(i)?AlignmentType.RIGHT:spec.align });
  })}));
  return new Table({
    width:{ size:total, type:WidthType.DXA }, columnWidths:colW,
    borders:{ top:hair(),bottom:hair(),left:noBorder.left,right:noBorder.right,
      insideHorizontal:hair(LINE), insideVertical:noBorder.left },
    rows:[headRow,...bodyRows],
  });
}

/* clause list (numbered bold-lead + description) */
function clause(n,title,text){
  return new Paragraph({ spacing:{ after:110 }, children:[
    new TextRun({ text:String(n).padStart(2,"0")+"   ", font:MONO, size:16, color:VIOLET, bold:true }),
    new TextRun({ text:title+"  ", font:FONT, size:20, color:INK, bold:true }),
    new TextRun({ text:text, font:FONT, size:20, color:INK2 }),
  ]});
}

/* ============================================================ DATA */

const deliverables = [
 ["WS1 · Platform foundations", [
   ["D-01","Access & authentication","Email/password with optional 2FA; enterprise SSO (SAML 2.0 / OIDC); rotating session tokens.","A user signs in by each method and receives correct role and tenant context."],
   ["D-02","Roles & permissions","Operator, Supervisor, Admin and Client roles with a published permission matrix enforced server-side.","Automated per-role permission tests pass; forbidden actions are refused by the API."],
   ["D-03","Multi-tenant isolation","Row-level security so one client's data is never returned to another.","Cross-tenant access tests return no data; verified in security testing (Section 13)."],
   ["D-04","Station kiosk sessions","Device-bound tokens, idle lock, fast operator switching.","A station authenticates as a device; operators switch without full re-login; idle lock engages."],
   ["D-05","Design system & app shell","Token set (colour, type, spacing, motion), component library, navigation and layouts for all three surfaces.","Component library published; all subsequent screens assembled from it."],
 ]],
 ["WS2 · Inspection station & capture", [
   ["D-06","Guided capture workflow","Six-state flow: scan, verify, position, capture, analyse, review.","An operator completes the full flow for a device end to end on station hardware."],
   ["D-07","Device identification","Barcode/QR scan and OCR service-tag reading, with manual entry fallback and device lookup (model, spec, prior inspections, warranty).","A scanned device resolves to its record; manual entry works where scan fails."],
   ["D-08","Six-angle capture","Single-trigger capture of six angles with per-angle retake and focus/exposure validation.","All six angles captured; blurred or over-exposed frames are rejected and re-shot."],
   ["D-09","Offline tolerance","Local capture queue with automatic sync on reconnect.","Captures taken with the network disabled complete and sync when it returns."],
 ]],
 ["WS3 · AI detection engine", [
   ["D-10","Defect taxonomy","20+ classes across cosmetic, display and hardware, signed off with the Client.","Taxonomy document approved by the Client in writing."],
   ["D-11","Detection model","Segmentation + classification, fine-tuned on Client intake photography; per-detection confidence, four-level severity, bounding region and heat map.","Model returns detections on live captures; accuracy gate in Section 13 met."],
   ["D-12","Inference service","Model served on the Edge Node GPU, with confidence thresholds and auto-escalation to review.","Inference completes within the per-image time budget on target hardware."],
   ["D-13","Model versioning & retrain loop","Every result stamped with its model version; operator corrections queued into the training set; candidate-vs-incumbent evaluation.","Results carry a version; a retrain run is demonstrated against the holdout set."],
 ]],
 ["WS4 · Review, grading & disposition", [
   ["D-14","Annotated review viewer","Bounding boxes, heat-map toggle, zoom-to-defect; cursor tool to resize an AI region or draw a missed one on the photo.","An operator resizes and draws regions; changes persist and are audited."],
   ["D-15","Detection management","Accept, reject, reclassify, change severity, merge duplicates; low-confidence queue with supervisor routing.","Each action updates the record and writes an audit entry."],
   ["D-16","Grading engine","Cosmetic and functional grades (A-F) and a 0-100 health score from configurable rules; per-client grade profiles.","A confirmed defect set produces the expected grade for a given profile."],
   ["D-17","Disposition & override","Recommended disposition (resell / repair / parts / recycle); supervisor override with mandatory reason code.","Overrides require a reason and are captured in the record."],
 ]],
 ["WS5 · Records, reporting & data", [
   ["D-18","Inspection history","Virtualised 16-column grid for 100k+ records; global search, advanced filters, saved presets, bulk actions, role-gated inline editing, saved views.","Grid performs at target with a representative dataset; filters and bulk actions behave."],
   ["D-19","Inspection record & report","Tabbed record (overview, images, AI results, audit, edit); full-res viewer; branded PDF certificate with tamper-evident hash; expiring read-only share link.","A certificate generates with correct data and hash; a share link expires as configured."],
   ["D-20","Import & export","Five-step CSV import wizard; export to CSV, XLSX, PDF and JSON, filtered or bulk.","A sample file imports with validation; exports produce correct content in each format."],
   ["D-21","Integrations","REST API with OpenAPI spec and signed webhooks; one ERP/WMS connector; ZPL label printing; scheduled buyer feeds (SFTP/S3).","A record change fires a signed webhook; the connector posts to the agreed endpoint."],
 ]],
 ["WS6 · Insight & administration", [
   ["D-22","Dashboard & live floor","Live station tiles, shift KPIs, throughput and defect-mix charts, alert feed, operator activity summary.","Dashboard reflects live station state and correct KPIs for a shift."],
   ["D-23","Analytics","Throughput, cycle time, yield and rework by station/shift; grade distribution; defect Pareto by supplier; AI-vs-human agreement; date ranges, CSV export, scheduled digest.","Reports compute correctly against known data; digest is delivered on schedule."],
   ["D-24","Administration","Client, user, role and station management with camera calibration; taxonomy and severity-rule editor; grade-profile builder with historic preview; notification rules; per-client branding; feature flags.","An administrator configures each area; changes take effect without a release."],
   ["D-25","Audit & compliance","Immutable audit log (actor, action, before, after, timestamp), exportable; retention/purge and right-to-erasure; encryption in transit and at rest; field-level redaction for Client-role users.","Every material change is logged; retention and erasure workflows execute; redaction applies."],
 ]],
];

const milestones = [
 ["M1","Foundations live","D-01 to D-05 — environments, auth, RBAC, app shell; taxonomy sign-off underway.","End W2 · Demo"],
 ["M2","First device graded","D-06 to D-13 — capture and the AI pipeline; a real device returned with detections.","End W4 · Demo"],
 ["M3","Review & grading","D-14 to D-17 — annotation, correction, grading engine and disposition.","End W6 · Demo"],
 ["M4","Feature complete","D-18 to D-25 — records, data, dashboard, analytics, admin, audit. Code freeze.","End W8 · Gate"],
 ["M5","UAT & accuracy signed off","UAT passed; model meets the accuracy gate in Section 13.","End W10 · Gate"],
 ["M6","Production go-live & handover","Pilot line stable; documentation and training delivered; handover accepted.","End W12 · Gate"],
];

const payments = [
 ["Mobilisation","On signature of this SOW","15%","[            ]"],
 ["M2 · End W4","First device graded end to end","15%","[            ]"],
 ["M3 · End W6","Review & grading accepted","15%","[            ]"],
 ["M4 · End W8","Feature complete · code freeze","20%","[            ]"],
 ["M5 · End W10","UAT & accuracy signed off","15%","[            ]"],
 ["M6 · End W12","Go-live & handover accepted","15%","[            ]"],
 ["Warranty end","End of the warranty period (Section 16)","5%","[            ]"],
];

const severities = [
 ["S1 · Critical", CRIT, "Capture, grading or data integrity is unusable, with no workaround.","Same Business Day"],
 ["S2 · Major",    WARN, "A key function fails or a workaround is costly.","2 Business Days"],
 ["S3 · Minor",    "9A7B1F", "A non-critical issue with an easy workaround.","Next release"],
 ["S4 · Cosmetic", OK,   "Visual or textual polish; no functional impact.","As scheduled"],
];

const risks = [
 ["Insufficient labelled training data","High",CRIT,"Pretrained backbone; Week-1 labelling sprint; active learning from operator corrections; sub-threshold detections route to human review."],
 ["Hardware arrives late","High",CRIT,"Mock camera driver and recorded image set in Sprint 2; hardware spec frozen at Week 3; software never blocked on hardware."],
 ["Lighting / positioning variance","Medium",WARN,"Fixed rig geometry, per-station calibration, automatic exposure/focus validation."],
 ["Integration access delayed","Medium",WARN,"Contract-first connector against an agreed schema with a stub; swapped to live on credentials. Not on the critical path."],
 ["Scope growth","Medium",WARN,"Fixed deliverable list; change control (Section 14); equal-size swaps."],
 ["Operator adoption","Low",OK,"Client operators involved from Week 1, in every demo, and run UAT themselves."],
];

/* ============================================================ BODY */

const children = [];

/* ---- title block ---- */
children.push(
  new Paragraph({ spacing:{ after:30 }, border:{ bottom:hair(VIOLET) },
    children:[ new TextRun({ text:"PIXORAMA", font:FONT, size:22, bold:true, color:VIOLET, characterSpacing:40 }),
               new TextRun({ text:".", font:FONT, size:22, bold:true, color:MAGENTA }) ]}),
  new Paragraph({ spacing:{ before:260, after:40 },
    children:[ new TextRun({ text:"STATEMENT OF WORK  ·  SOW-2026-011", font:MONO, size:16, color:CYAN, bold:true, characterSpacing:60 }) ]}),
  new Paragraph({ spacing:{ after:60 }, children:[ new TextRun({ text:"AI Device Inspector", font:FONT, size:52, bold:true, color:INK }) ]}),
  new Paragraph({ spacing:{ after:200 }, children:[ new TextRun({ text:"Platform — Statement of Work", font:FONT, size:32, bold:true, color:VIOLET }) ]}),
  new Paragraph({ spacing:{ after:240 }, children:[ new TextRun({
    text:"This Statement of Work sets out the deliverables, acceptance criteria, timeline, responsibilities and commercial terms for the design, build and delivery of the AI Device Inspector platform. It operationalises the accompanying platform proposal and, once signed, governs the engagement.",
    font:FONT, size:21, color:INK2 }) ]}),
);

/* document control table */
children.push(tbl([1500,3013,1500,3013],
  ["Field","Value","Field","Value"],
  [
    ["Client","Hugo Martinez","Supplier","Pixorama Group"],
    ["Document","SOW-2026-011 · v1.0","Date of issue","24 July 2026"],
    ["Engagement","Fixed scope · 12 weeks","Related document","AI Device Inspector — Platform Proposal"],
  ],
  { colSpec:[ {mono:true,bold:true,color:MUTED,size:15}, {bold:true,color:INK}, {mono:true,bold:true,color:MUTED,size:15}, {bold:true,color:INK} ] }
));
children.push(new Paragraph({ spacing:{ before:120 }, children:[
  new TextRun({ text:"Status:  ", font:MONO, size:15, color:MUTED, bold:true }),
  new TextRun({ text:"For review & signature — prevails over prior scope discussions on execution.", font:FONT, size:18, color:INK2, italics:true }) ]}));

children.push(new Paragraph({ children:[ new PageBreak() ] }));

/* ---- table of contents ---- */
children.push(new Paragraph({ spacing:{ after:120 }, children:[ new TextRun({ text:"Contents", font:FONT, size:28, bold:true, color:INK }) ]}));
children.push(new TableOfContents("Contents", { hyperlink:true, headingStyleRange:"1-1" }));
children.push(new Paragraph({ children:[ new PageBreak() ] }));

/* ---- 01 Introduction ---- */
children.push(eyebrow("Purpose & structure"), h1("01","Introduction"),
  lead("This document is the definitive statement of what Pixorama will deliver, how each deliverable will be accepted, and the terms under which the work proceeds."),
  body("Where this Statement of Work and the platform proposal differ, this document prevails on matters of scope, acceptance, schedule and commercials. Anything not expressly listed as in scope in Section 05 or 06 is out of scope and is handled through the change-control process in Section 14."),
  h2("How this document is organised"),
  clause(1,"Scope","Sections 04-06 define exactly what is built; Section 07 states what is not."),
  clause(2,"Delivery","Sections 10-11 set the method, timeline and milestones."),
  clause(3,"Acceptance","Sections 12-13 define how deliverables are tested and signed off."),
  clause(4,"Commercials","Sections 14-16 govern change, payment and warranty."),
);

/* ---- 02 Definitions ---- */
children.push(eyebrow("Terms"), h1("02","Definitions"),
  body("Capitalised terms used throughout this document carry the meanings below.", {after:140}));
[
 ["Platform","The AI Device Inspector software system described in Sections 04-06, in all its surfaces (station kiosk, back-office application, client portal) and services."],
 ["Deliverable","A discrete, identified output listed in Section 05 or 06, each with its own acceptance basis."],
 ["Edge Node","The on-site hardware and software that owns the cameras and runs inference at a facility."],
 ["Detection","A single defect identified by the model on a captured image, with class, confidence, severity and region."],
 ["Grade Profile","A configurable, versioned rule set that converts a confirmed defect set into a commercial grade for a given buyer."],
 ["Holdout Set","A frozen, labelled sample of images used once to measure model accuracy and never used for training."],
 ["UAT","User Acceptance Testing — structured testing performed by the Client's own operators and supervisors against agreed scripts."],
 ["Go-Live","The point at which the Platform is used to process live production stock on at least one line."],
 ["Business Day","Monday to Friday excluding public holidays in the Client's jurisdiction."],
].forEach(([t,d])=>children.push(new Paragraph({ spacing:{ after:70 }, children:[
  new TextRun({ text:t+" — ", font:FONT, size:20, bold:true, color:INK }),
  new TextRun({ text:d, font:FONT, size:20, color:INK2 }) ]})));

/* ---- 03 Objectives ---- */
children.push(eyebrow("Why"), h1("03","Project objectives"),
  lead("The Platform is accepted as meeting its purpose when it delivers against these objectives, evidenced by the acceptance criteria in Sections 12-13."),
  bullet("Consistent grading — one model and one rule set applied to every device, independent of operator or shift."),
  bullet("Speed — capture-to-grade in under 60 seconds per device on the target hardware."),
  bullet("Defensibility — every grade backed by photographs, a defect map and a complete audit trail."),
  bullet("Measurable accuracy — detection performance proven against a frozen holdout set to an agreed threshold."),
  bullet("Operational visibility — throughput, yield and defect trends visible to supervisors and administrators."),
  bullet("Integration — records flow to the Client's existing systems without manual re-keying."),
);

/* ---- 04 Scope overview ---- */
children.push(eyebrow("What is being built"), h1("04","Scope overview"),
  lead("The engagement delivers a production-ready, multi-tenant platform of 12 functional modules comprising 60 features, organised for delivery into six workstreams, plus the AI model, infrastructure and documentation."),
  body("The detailed deliverables follow in Section 05; the technical deliverables in Section 06.", {after:120}));
children.push(tbl([1400,7626],
  ["Workstream","Covers"],
  [
   ["WS1 · Foundations","Access, roles, tenancy, environments, design system, app shell."],
   ["WS2 · Capture","Inspection station and the six-angle capture workflow."],
   ["WS3 · AI engine","Detection model, inference service and the training loop."],
   ["WS4 · Review & grading","Annotation, correction, grading engine and disposition."],
   ["WS5 · Records & data","History, reporting, imports, exports and integrations."],
   ["WS6 · Insight & admin","Dashboard, analytics, administration and audit."],
  ],
  { colSpec:[ {mono:true,bold:true,color:VIOLET,size:16}, {} ] }));

/* ---- 05 Detailed deliverables ---- */
children.push(new Paragraph({ children:[ new PageBreak() ] }),
  eyebrow("In scope"), h1("05","Detailed deliverables"),
  lead("Every deliverable below is committed to the build and is individually acceptance-tested. Deliverable IDs (D-xx) are referenced by the acceptance and milestone schedules."));
deliverables.forEach(([ws,rows])=>{
  children.push(new Paragraph({ spacing:{ before:200, after:80 },
    children:[ new TextRun({ text:ws, font:FONT, size:20, bold:true, color:INK }) ]}));
  children.push(tbl([680,1900,3620,2826],
    ["ID","Deliverable","Includes","Acceptance basis"],
    rows,
    { colSpec:[ {mono:true,bold:true,color:VIOLET,size:16}, {bold:true,color:INK,size:18}, {size:17}, {size:16,color:MUTED} ] }));
});

/* ---- 06 Technical deliverables ---- */
children.push(new Paragraph({ children:[ new PageBreak() ] }),
  eyebrow("Build & hand-over"), h1("06","Technical deliverables"),
  body("Beyond the functional modules, the engagement delivers the following engineering and documentation assets.", {after:140}),
  h2("Front end"),
  bullet("Next.js 16 / React 19 / TypeScript application serving station, back-office and client-portal surfaces"),
  bullet("Tokenised design system on Tailwind v4; dark-first station UI"),
  bullet("Virtualised data grids (100k+ rows); real-time station status (WebSocket + SSE fallback)"),
  bullet("Offline-tolerant capture (service worker + IndexedDB)"),
  bullet("WCAG 2.2 AA on operator and supervisor journeys; LCP < 2.0s, INP < 200ms budgets"),
  h2("Back end"),
  bullet("NestJS / TypeScript API with OpenAPI specification"),
  bullet("PostgreSQL 16 with row-level security; Redis + BullMQ job queue"),
  bullet("S3-compatible object storage with presigned uploads"),
  bullet("Python FastAPI inference service; TensorRT model serving on the Edge Node"),
  bullet("Transactional-outbox webhooks; headless-Chromium PDF reporting"),
  h2("Infrastructure & operations"),
  bullet("Dockerised services; Terraform-defined environments (staging + production)"),
  bullet("GitHub Actions CI/CD with SCA, SAST and secret scanning"),
  bullet("OpenTelemetry tracing to Grafana; Sentry error tracking"),
  bullet("Cloud control plane plus one on-site Edge Node configuration"),
  bullet("Nightly point-in-time backups with a 30-day recovery window"),
  h2("Documentation & enablement"),
  bullet("Architecture overview and data-model reference"),
  bullet("API reference (OpenAPI) and integration/webhook guide"),
  bullet("Administrator, supervisor and operator user guides"),
  bullet("Model retraining and evaluation guide"),
  bullet("Operational runbooks and recorded training walkthroughs"),
);

/* ---- 07 Out of scope ---- */
children.push(eyebrow("Exclusions"), h1("07","Out of scope"),
  lead("The following are explicitly excluded from this Statement of Work. Any of them may be added later under change control (Section 14)."),
  bullet("Native mobile applications — the web app is responsive and installable"),
  bullet("Automated repair-cost estimation and parts pricing"),
  bullet("Marketplace listing sync (eBay, Back Market and similar)"),
  bullet("Interface languages other than English"),
  bullet("Robotic device handling and conveyor control"),
  bullet("Functional/electrical testing of the device itself (battery cycles, port continuity, screen response)"),
  bullet("Integrations beyond the one ERP/WMS endpoint in D-21"),
  bullet("Procurement of camera, lighting or GPU hardware"),
  bullet("Ongoing managed hosting or a support retainer beyond warranty (Section 16)"),
);

/* ---- 08 Assumptions ---- */
children.push(eyebrow("Basis of estimate"), h1("08","Assumptions & dependencies"),
  lead("The scope, timeline and price in this document rely on the following. A material change to any of them is handled under change control."),
  h2("Assumptions"),
  bullet("The Client provides sample devices covering its real intake mix, plus 1,500-3,000 photographs for training"),
  bullet("Camera rig, lighting and GPU hardware are procured by the Client and on site by Week 3"),
  bullet("One ERP/WMS integration endpoint is in scope"),
  bullet("Interface and documentation are English-only"),
  bullet("Cloud hosting and third-party licences are billed to the Client at cost"),
  h2("Client dependencies"),
  bullet("Defect taxonomy and grading rules signed off in Week 1"),
  bullet("Two operators and one supervisor available for one day per sprint (labelling, review, UAT)"),
  bullet("Timely access to environments, the SSO tenant and the integration endpoint"),
  bullet("Decisions and approvals returned within two Business Days of request"),
  bullet("A nominated Client project owner empowered to accept deliverables"),
  new Paragraph({ spacing:{ before:60, after:80 }, shading:{ type:ShadingType.CLEAR, fill:PAPER2, color:"auto" },
    border:{ left:{ style:BorderStyle.SINGLE, size:18, color:WARN } },
    children:[ new TextRun({ text:"Effect of delay.  ", font:FONT, size:19, bold:true, color:WARN }),
      new TextRun({ text:"Where a Client dependency is not met by the date required, Pixorama will notify the Client; affected milestone dates move by the period of the delay, and any resulting standing time is handled under change control.", font:FONT, size:19, color:INK2 }) ]}),
);

/* ---- 09 Responsibilities ---- */
children.push(eyebrow("Who does what"), h1("09","Responsibilities"),
  lead("Obligations are stated at the level of each party. Pixorama resources the engagement at its own discretion to meet the deliverables and dates in this document."));
children.push(tbl([4513,4513],
  ["Pixorama will","The Client will"],
  [[
    [ new Paragraph({ bullet:{level:0}, spacing:{after:50}, children:[new TextRun({text:"Design, build, test and deliver all deliverables in Sections 05-06",font:FONT,size:18,color:INK2})]}),
      new Paragraph({ bullet:{level:0}, spacing:{after:50}, children:[new TextRun({text:"Train and evaluate the detection model to the accuracy gate in Section 13",font:FONT,size:18,color:INK2})]}),
      new Paragraph({ bullet:{level:0}, spacing:{after:50}, children:[new TextRun({text:"Run system and integration testing, and support Client UAT",font:FONT,size:18,color:INK2})]}),
      new Paragraph({ bullet:{level:0}, spacing:{after:50}, children:[new TextRun({text:"Provide the documentation and training in Section 06",font:FONT,size:18,color:INK2})]}),
      new Paragraph({ bullet:{level:0}, spacing:{after:50}, children:[new TextRun({text:"Report progress on an agreed cadence; maintain the change log and risk register",font:FONT,size:18,color:INK2})]}),
      new Paragraph({ bullet:{level:0}, spacing:{after:20}, children:[new TextRun({text:"Nominate a single point of contact for the Client",font:FONT,size:18,color:INK2})]}) ],
    [ new Paragraph({ bullet:{level:0}, spacing:{after:50}, children:[new TextRun({text:"Provide sample devices, training photography and the signed-off taxonomy and grading rules",font:FONT,size:18,color:INK2})]}),
      new Paragraph({ bullet:{level:0}, spacing:{after:50}, children:[new TextRun({text:"Procure and install the camera, lighting and GPU hardware by Week 3",font:FONT,size:18,color:INK2})]}),
      new Paragraph({ bullet:{level:0}, spacing:{after:50}, children:[new TextRun({text:"Make operators and a supervisor available for labelling, review and UAT",font:FONT,size:18,color:INK2})]}),
      new Paragraph({ bullet:{level:0}, spacing:{after:50}, children:[new TextRun({text:"Provide access to environments, the SSO tenant and the integration endpoint",font:FONT,size:18,color:INK2})]}),
      new Paragraph({ bullet:{level:0}, spacing:{after:50}, children:[new TextRun({text:"Review deliverables and return acceptance decisions within the windows in Section 12",font:FONT,size:18,color:INK2})]}),
      new Paragraph({ bullet:{level:0}, spacing:{after:20}, children:[new TextRun({text:"Nominate an empowered project owner to accept deliverables and resolve escalations",font:FONT,size:18,color:INK2})]}) ],
  ]],
  { colSpec:[ {}, {} ] }));

/* ---- 10 Timeline ---- */
children.push(new Paragraph({ children:[ new PageBreak() ] }),
  eyebrow("How & when"), h1("10","Delivery approach & timeline"),
  lead("Twelve weeks: four two-week sprints to feature-complete, then a four-week test and acceptance phase. Each sprint ends in a working demo on staging and a stated exit criterion. Code freezes at the end of Week 8."));
children.push(tbl([2400,1600,5026],
  ["Phase","Weeks","Focus"],
  [
   ["Sprint 1 · Foundations","W1-W2","Auth, RBAC, app shell (WS1)"],
   ["Sprint 2 · Capture & AI","W3-W4","Inspection station, inference pipeline (WS2-3)"],
   ["Sprint 3 · Review & grade","W5-W6","Annotation, grading engine (WS4)"],
   ["Sprint 4 · Records & admin","W7-W8","History, reporting, admin (WS5-6). Code freeze."],
   ["Model training","W3-W10","Label, train, evaluate, promote (continuous)"],
   ["SIT & regression","W9","System integration and automated regression"],
   ["UAT & accuracy","W10","Client UAT; model scored on the holdout set"],
   ["Perf · security · a11y","W11","Load, penetration test, accessibility audit"],
   ["Pilot & handover","W12","Live pilot line, training, cutover"],
  ],
  { colSpec:[ {bold:true,color:INK,size:18}, {mono:true,color:VIOLET,size:16}, {size:18} ] }));

/* ---- 11 Milestones ---- */
children.push(eyebrow("Schedule"), h1("11","Milestones & deliverable schedule"),
  lead("Each milestone is either a demonstration (Demo) or a formal gate (Gate). Payment is linked to the milestones in Section 15."));
children.push(tbl([620,2200,4380,1826],
  ["ID","Milestone","Deliverables","Timing · type"],
  milestones,
  { colSpec:[ {mono:true,bold:true,color:VIOLET,size:16}, {bold:true,color:INK,size:18}, {size:17}, {mono:true,size:15,color:MUTED} ] }));

/* ---- 12 Acceptance ---- */
children.push(new Paragraph({ children:[ new PageBreak() ] }),
  eyebrow("Sign-off"), h1("12","Acceptance process & criteria"),
  lead("How each deliverable and milestone is reviewed, corrected and accepted."),
  clause(1,"Review window","On submission of a deliverable, the Client has five Business Days to review it against its acceptance basis (Section 05) and either accept it or issue a written list of defects referencing specific criteria."),
  clause(2,"Correction","Pixorama corrects valid defects and re-submits. The review window restarts for the re-submitted deliverable, limited to the previously raised items."),
  clause(3,"Deemed acceptance","A deliverable is deemed accepted if the Client raises no written defects within the review window, or if it is used in production."),
  clause(4,"Partial acceptance","A deliverable is not rejected as a whole for minor (S3/S4) defects; it is accepted with those items logged for correction inside the warranty period."),
  clause(5,"Milestone gates","Gate milestones (M4-M6) require the associated deliverables to be accepted and the relevant tests in Section 13 to have passed."),
  h2("Defect severity & correction targets"));
children.push(tbl([1900,5300,1826],
  ["Severity","Description","Correction target"],
  severities.map(s=>[s[0],s[2],s[3]]),
  { colSpec:[ {bold:true,color:INK,size:18}, {size:18}, {mono:true,size:16,color:INK2} ] }));

/* ---- 13 Testing ---- */
children.push(eyebrow("Four-week test phase"), h1("13","Testing & quality assurance"),
  lead("Testing is a resourced, gated phase — not a hope. Each gate below must pass before the associated milestone is accepted."),
  h2("Acceptance gates — quantified thresholds"),
  bullet("Detection recall >= 0.90 and precision >= 0.85 on the top ten defect classes, measured on the holdout set"),
  bullet("API p95 < 300 ms at 3x expected peak throughput"),
  bullet("Zero open S1/S2 defects; regression suite green on three consecutive runs"),
  bullet("No critical or high security findings open"),
  bullet("WCAG 2.2 AA audit passed on operator and supervisor journeys"),
  h2("Evidence provided"),
  bullet("Per-class model scorecard against the holdout set"),
  bullet("Grade-agreement study — platform grade vs expert human grade"),
  bullet("Load and soak test reports"),
  bullet("Penetration test report and remediation log"),
  bullet("UAT results with a fix-or-defer decision on every item"),
);

/* ---- 14 Change control ---- */
children.push(eyebrow("Managing scope"), h1("14","Change control"),
  lead("The deliverables in Sections 05-06 are the agreed scope. Any change to them follows this process; nothing outside it alters price or timeline."),
  clause(1,"Raising a change","Either party may raise a change request in writing, describing the change and its reason."),
  clause(2,"Impact assessment","Pixorama assesses the impact on scope, timeline and price and issues a change note, normally within three Business Days."),
  clause(3,"Approval","Work on a change begins only once the Client approves the change note in writing. Approved changes are appended to this Statement of Work."),
  clause(4,"Swaps","By agreement, a new item of equivalent size may be exchanged for an unstarted deliverable at no change to price or timeline."),
  clause(5,"Standing changes","Rules, taxonomy, grade profiles and branding are configurable and are changed by the Client without a release — these are not change requests."),
);

/* ---- 15 Commercials ---- */
children.push(new Paragraph({ children:[ new PageBreak() ] }),
  eyebrow("Fees & payment"), h1("15","Commercials & payment schedule"),
  lead("The engagement is delivered for a fixed fee against the fixed scope in this document. Payment is linked to milestone acceptance. Figures are completed on execution."));
children.push(tbl([2000,3600,1400,2026],
  ["Trigger","Milestone","Share","Amount"],
  [...payments, ["Total","Fixed engagement fee","100%","[   total   ]"]],
  { rightCols:[2,3],
    colSpec:[ {bold:true,color:INK,size:18}, {size:18}, {mono:true,bold:true,color:VIOLET,size:17}, {mono:true,size:16,color:MUTED} ] }));
children.push(new Paragraph({ spacing:{ before:120, after:40 }, shading:{ type:ShadingType.CLEAR, fill:PAPER2, color:"auto" },
  border:{ left:{ style:BorderStyle.SINGLE, size:18, color:WARN } },
  children:[ new TextRun({ text:"Commercial notes.  ", font:FONT, size:19, bold:true, color:WARN }),
    new TextRun({ text:"Amounts, currency, tax treatment and invoice terms are inserted on execution and are governed by the parties' master agreement. Cloud hosting and third-party licences are billed to the Client at cost and are additional to the fixed fee. Invoices are payable within the agreed terms of each accepted milestone.", font:FONT, size:19, color:INK2 }) ]}));

/* ---- 16 Warranty & IP ---- */
children.push(eyebrow("After go-live"), h1("16","Warranty, support & IP"),
  h2("Warranty & support"),
  clause(1,"Hypercare","Thirty days of close monitoring and priority defect response from Go-Live, at no additional cost."),
  clause(2,"Warranty period","Ninety days from Go-Live during which S1 and S2 defects in delivered scope are corrected at no cost."),
  clause(3,"Exclusions","Warranty excludes issues caused by Client changes to configuration, unsupported environments, or third-party systems outside the delivered scope."),
  clause(4,"Ongoing support","Support or a managed-service arrangement beyond warranty is available under a separate agreement."),
  h2("Intellectual property & confidentiality"),
  clause(1,"Ownership","On full payment, intellectual property in the bespoke deliverables and the trained model weights transfers to the Client."),
  clause(2,"Pre-existing IP","Pixorama retains its pre-existing tools, libraries and know-how, and grants the Client a licence to use them as embedded in the deliverables."),
  clause(3,"Third-party components","Open-source and third-party components remain under their own licences, disclosed on handover."),
  clause(4,"Confidentiality & data","Each party protects the other's confidential information; personal data is handled per the parties' data-processing terms."),
  new Paragraph({ spacing:{ before:120, after:40 }, shading:{ type:ShadingType.CLEAR, fill:PAPER2, color:"auto" },
    border:{ left:{ style:BorderStyle.SINGLE, size:18, color:WARN } },
    children:[ new TextRun({ text:"Precedence.  ", font:FONT, size:19, bold:true, color:WARN }),
      new TextRun({ text:"This Statement of Work governs scope, acceptance, schedule and commercials for this engagement. Legal terms (liability, warranties, IP, data protection, termination) are governed by the parties' master services agreement; where that agreement is silent, the clauses above apply. Nothing here is legal advice, and the parties should have this document reviewed before signature.", font:FONT, size:19, color:INK2 }) ]}),
);

/* ---- 17 Governance ---- */
children.push(eyebrow("Running the engagement"), h1("17","Governance & reporting"),
  bullet("Weekly demo — a working demonstration on staging at the end of each week."),
  bullet("Written status — a weekly note covering progress, upcoming work, risks and any blocked dependencies."),
  bullet("Shared board — a live board the Client can view at any time."),
  bullet("Single points of contact — each party nominates one contact for day-to-day decisions."),
  bullet("Change & risk logs — maintained throughout and reviewed at the weekly checkpoint."),
  bullet("Escalation — unresolved items escalate to each party's nominated owner within two Business Days."),
);

/* ---- 18 Risk ---- */
children.push(eyebrow("Managed openly"), h1("18","Key risks & mitigation"));
children.push(tbl([2600,1200,5226],
  ["Risk","Level","Mitigation"],
  risks.map(r=>[ r[0], r[1], r[3] ]),
  { colSpec:[ {bold:true,color:INK,size:18}, {mono:true,bold:true,size:15}, {size:17} ] }));

/* ---- 19 Sign-off ---- */
children.push(new Paragraph({ children:[ new PageBreak() ] }),
  eyebrow("Authorisation"), h1("19","Acceptance & signature"),
  lead("By signing below, each party agrees to the scope, deliverables, acceptance criteria, timeline and commercial terms set out in this Statement of Work."),
  spacer(240));
function sigBlock(role,name,sub){
  return [
    new Paragraph({ spacing:{ after:60 }, children:[ new TextRun({ text:role.toUpperCase(), font:MONO, size:15, color:MUTED, bold:true, characterSpacing:40 }) ]}),
    spacer(360),
    new Paragraph({ spacing:{ after:30 }, border:{ bottom:hair(INK) }, children:[ new TextRun({ text:"", size:2 }) ]}),
    new Paragraph({ spacing:{ after:10 }, children:[ new TextRun({ text:name, font:FONT, size:20, bold:true, color:INK }) ]}),
    new Paragraph({ children:[ new TextRun({ text:sub, font:FONT, size:17, color:MUTED }) ]}),
  ];
}
children.push(tbl([4513,4513], ["Accepted for the Client","For and on behalf of Pixorama Group"],
  [[ sigBlock("Client","Hugo Martinez","Signature · Date"), sigBlock("Supplier","Authorised signatory","Signature · Date") ]],
));

/* ============================================================ DOC */

const doc = new Document({
  creator:"Pixorama Group",
  title:"AI Device Inspector — Statement of Work",
  subject:"Statement of Work · SOW-2026-011 · prepared for Hugo Martinez",
  description:"Deliverables, acceptance criteria, timeline and commercial terms.",
  styles:{
    default:{ document:{ run:{ font:FONT, size:20, color:INK2 } } },
    paragraphStyles:[
      { id:"Heading1", name:"Heading 1", basedOn:"Normal", next:"Normal", quickFormat:true,
        run:{ font:FONT, size:30, bold:true, color:INK }, paragraph:{ spacing:{ before:60, after:120 } } },
      { id:"Heading2", name:"Heading 2", basedOn:"Normal", next:"Normal", quickFormat:true,
        run:{ font:FONT, size:21, bold:true, color:INK }, paragraph:{ spacing:{ before:220, after:90 } } },
    ],
  },
  numbering:{ config:[
    { reference:"b, level=0" , levels:[] }, // placeholder unused
  ]},
  sections:[{
    properties:{ page:{ margin:{ top:1440, bottom:1440, left:1440, right:1440 } } },
    headers:{ default:new Header({ children:[ new Paragraph({ alignment:AlignmentType.RIGHT, border:{ bottom:hair(LINE) },
      children:[ new TextRun({ text:"AI Device Inspector — Statement of Work", font:MONO, size:14, color:FAINT, characterSpacing:20 }) ]}) ]}) },
    footers:{ default:new Footer({ children:[ new Paragraph({ border:{ top:hair(LINE) }, tabStops:[{ type:TabStopType.RIGHT, position:CW }],
      children:[
        new TextRun({ text:"Confidential · SOW-2026-011 · Prepared for Hugo Martinez", font:MONO, size:14, color:FAINT }),
        new TextRun({ text:"\t", font:MONO, size:14 }),
        new TextRun({ children:["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES], font:MONO, size:14, color:FAINT }),
      ]}) ]}) },
    children,
  }],
});

Packer.toBuffer(doc).then(buf=>{
  fs.writeFileSync("AI-Device-Inspector-SOW.docx", buf);
  console.log("written AI-Device-Inspector-SOW.docx", Math.round(buf.length/1024)+"KB");
});
