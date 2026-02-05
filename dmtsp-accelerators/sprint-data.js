/**
 * DMTSP Fabric Migration — Sprint Plan Data
 * Source: Sprint_Plan_Synapse_to_Fabric.md
 */

const PHASE1_SPRINTS = [
    {
        id: 0,
        name: "Discovery & Planning",
        hours: 700,
        tasks: [
            { task: "Project kickoff & governance setup", subtasks: "Charter, RACI, communication plan, sprint ceremonies", hours: 120, owners: "PM" },
            { task: "Architecture design & target-state definition", subtasks: "Fabric workspace topology, capacity sizing, networking design, lakehouse vs. warehouse decisions", hours: 200, owners: "Architect, DBA" },
            { task: "Source environment inventory & assessment", subtasks: "DACPAC extraction, ADF assessment tool, SP complexity classification, ADLS inventory", hours: 200, owners: "Sr Data Engineers, DBA" },
            { task: "Migration wave planning", subtasks: "Dependency mapping, batch groupings, cutover sequencing", hours: 100, owners: "Architect, PM" },
            { task: "Knowledge transfer & team onboarding", subtasks: "Fabric fundamentals, migration tooling walkthroughs, coding standards", hours: 80, owners: "Architect, Sr Data Engineers" }
        ],
        milestones: []
    },
    {
        id: 1,
        name: "Foundation Setup",
        hours: 700,
        tasks: [
            { task: "Fabric workspace provisioning", subtasks: "Dev/SIT/UAT/Prod workspaces, capacity assignment, admin roles", hours: 140, owners: "Architect, DBA" },
            { task: "Networking & security configuration", subtasks: "Private endpoints, VNet data gateways, managed identities, Entra ID groups", hours: 160, owners: "Architect, DBA" },
            { task: "Git integration setup", subtasks: "Azure DevOps/GitHub repo structure, branch policies, workspace-to-repo connection", hours: 80, owners: "Sr Data Engineer" },
            { task: "Fabric Data Warehouse creation", subtasks: "Target warehouse, schema creation (16 schemas), security roles (40 objects)", hours: 120, owners: "DBA, Data Engineers" },
            { task: "Development environment tooling", subtasks: "VS Code extensions, notebook environment, PowerShell modules", hours: 60, owners: "Sr Data Engineers" },
            { task: "CI/CD pipeline scaffolding (manual)", subtasks: "Basic deployment scripts, environment promotion procedures", hours: 80, owners: "Sr Data Engineer" },
            { task: "PM governance & reporting", subtasks: "Sprint tracking setup, risk register, status reporting cadence", hours: 60, owners: "PM" }
        ],
        milestones: []
    },
    {
        id: 2,
        name: "Foundation Completion & Migration Start",
        hours: 700,
        tasks: [
            { task: "CI/CD pipeline completion", subtasks: "End-to-end manual deployment pipeline, validation scripts", hours: 100, owners: "Sr Data Engineer" },
            { task: "Schema/security migration", subtasks: "Remaining schema + security objects (Functions: 4, Schema: 16, Security: 40)", hours: 19, owners: "DBA" },
            { task: "Synapse Tables — Batch 1 (170 tables)", subtasks: "DACPAC-based schema deploy, data copy, validation", hours: 680, owners: "Data Engineers (4), DBA" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting, risk management", hours: 40, owners: "PM" },
            { task: "Architecture guidance", subtasks: "Pattern validation, issue escalation", hours: 40, owners: "Architect" }
        ],
        milestones: ["Tables: 170 / 1,538"]
    },
    {
        id: 3,
        name: "Synapse DW Migration",
        hours: 700,
        tasks: [
            { task: "Synapse Tables — Batch 2 (170 tables)", subtasks: "Schema deploy, data copy, per-table validation", hours: 680, owners: "Data Engineers (4), DBA" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" },
            { task: "Architecture guidance", subtasks: "Pattern review, edge-case resolution", hours: 40, owners: "Architect" }
        ],
        milestones: ["Tables: 340 / 1,538"]
    },
    {
        id: 4,
        name: "Synapse DW Migration",
        hours: 700,
        tasks: [
            { task: "Synapse Tables — Batch 3 (170 tables)", subtasks: "Schema deploy, data copy, per-table validation", hours: 680, owners: "Data Engineers (4), DBA" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" },
            { task: "Architecture guidance", subtasks: "Pattern review", hours: 40, owners: "Architect" }
        ],
        milestones: ["Tables: 510 / 1,538"]
    },
    {
        id: 5,
        name: "Synapse DW Migration",
        hours: 700,
        tasks: [
            { task: "Synapse Tables — Batch 4 (170 tables)", subtasks: "Schema deploy, data copy, per-table validation", hours: 680, owners: "Data Engineers (4), DBA" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" },
            { task: "Architecture guidance", subtasks: "Pattern review", hours: 40, owners: "Architect" }
        ],
        milestones: ["Tables: 680 / 1,538"]
    },
    {
        id: 6,
        name: "Synapse DW Migration",
        hours: 700,
        tasks: [
            { task: "Synapse Tables — Batch 5 (170 tables)", subtasks: "Schema deploy, data copy, per-table validation", hours: 680, owners: "Data Engineers (4), DBA" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" },
            { task: "Architecture guidance", subtasks: "Pattern review", hours: 40, owners: "Architect" }
        ],
        milestones: ["Tables: 850 / 1,538"]
    },
    {
        id: 7,
        name: "Synapse DW Migration + ADF Pipeline Start",
        hours: 700,
        tasks: [
            { task: "Synapse Tables — Batch 6 (170 tables)", subtasks: "Schema deploy, data copy, per-table validation", hours: 480, owners: "Data Engineers (3), DBA" },
            { task: "Synapse Views — Batch 1 (120 views)", subtasks: "View migration, dependency validation", hours: 180, owners: "Data Engineer (1)" },
            { task: "ADF Pipeline Assessment & Planning", subtasks: "Run assessment tool, categorize pipelines, create resolution files", hours: 40, owners: "Sr Data Engineer" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: ["Tables: 1,020 / 1,538", "Views: 120 / 362"]
    },
    {
        id: 8,
        name: "Synapse DW Migration + ADF Migration",
        hours: 700,
        tasks: [
            { task: "Synapse Tables — Batch 7 (170 tables)", subtasks: "Schema deploy, data copy, validation", hours: 480, owners: "Data Engineers (3)" },
            { task: "Synapse Views — Batch 2 (120 views)", subtasks: "View migration, dependency validation", hours: 180, owners: "Data Engineer (1)" },
            { task: "ADF Pipelines — Batch 1 (100 pipelines)", subtasks: "Import, convert, resolve, deploy, validate", hours: 200, owners: "Sr Data Engineers (2)" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: ["Tables: 1,190 / 1,538", "Views: 240 / 362", "Pipelines: 100 / 609"]
    },
    {
        id: 9,
        name: "Synapse DW Completion + ADF Migration",
        hours: 700,
        tasks: [
            { task: "Synapse Tables — Batch 8 (178 tables)", subtasks: "Schema deploy, data copy, validation", hours: 480, owners: "Data Engineers (3)" },
            { task: "Synapse Views — Batch 3 (122 views)", subtasks: "View migration, remaining functions validation", hours: 183, owners: "Data Engineer (1)" },
            { task: "ADF Pipelines — Batch 2 (100 pipelines)", subtasks: "Import, convert, resolve, deploy, validate", hours: 200, owners: "Sr Data Engineers (2)" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: ["Tables: 1,368 / 1,538", "Views: 362 / 362 \u2713", "Pipelines: 200 / 609"]
    },
    {
        id: 10,
        name: "Synapse DW Completion + ADF + SP Start",
        hours: 700,
        tasks: [
            { task: "Synapse Tables — Batch 9 (170 tables, final)", subtasks: "Schema deploy, data copy, final validation", hours: 480, owners: "Data Engineers (3)" },
            { task: "ADF Pipelines — Batch 3 (100 pipelines)", subtasks: "Import, convert, resolve, deploy, validate", hours: 200, owners: "Sr Data Engineers (2)" },
            { task: "ADF Datasets — Batch 1 (150 datasets)", subtasks: "Repoint and validate", hours: 200, owners: "Data Engineer (1)" },
            { task: "Stored Procs — Standard Batch 1 (90 SPs)", subtasks: "Convert to Spark SQL, validate", hours: 180, owners: "Sr Data Engineer" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: ["Tables: 1,538 / 1,538 \u2713", "Pipelines: 300 / 609", "Datasets: 150 / 450"]
    },
    {
        id: 11,
        name: "ADF Migration + Stored Proc Conversion",
        hours: 700,
        tasks: [
            { task: "ADF Pipelines — Batch 4 (100 pipelines)", subtasks: "Import, convert, resolve, deploy, validate", hours: 200, owners: "Sr Data Engineer, Data Engineer" },
            { task: "ADF Datasets — Batch 2 (150 datasets)", subtasks: "Repoint and validate", hours: 200, owners: "Data Engineer" },
            { task: "ADF Triggers — Batch 1 (70 triggers)", subtasks: "Migrate and validate", hours: 140, owners: "Data Engineer" },
            { task: "Stored Procs — Standard Batch 2 (90 SPs)", subtasks: "Convert to Spark SQL, validate", hours: 180, owners: "Sr Data Engineer, Data Engineer" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: ["Pipelines: 400 / 609", "Datasets: 300 / 450", "Triggers: 70 / 142"]
    },
    {
        id: 12,
        name: "ADF Completion + Stored Proc Conversion",
        hours: 700,
        tasks: [
            { task: "ADF Pipelines — Batch 5 (109 pipelines)", subtasks: "Import, convert, resolve, deploy, validate", hours: 218, owners: "Sr Data Engineer, Data Engineer" },
            { task: "ADF Datasets — Batch 3 (150 datasets, final)", subtasks: "Repoint and validate", hours: 200, owners: "Data Engineer" },
            { task: "ADF Triggers — Batch 2 (72 triggers, final)", subtasks: "Migrate and validate", hours: 144, owners: "Data Engineer" },
            { task: "Stored Procs — Standard Batch 3 (90 SPs)", subtasks: "Convert to Spark SQL, validate", hours: 180, owners: "Sr Data Engineer, Data Engineer" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: ["Pipelines: 509 / 609", "Datasets: 450 / 450 \u2713", "Triggers: 142 / 142 \u2713"]
    },
    {
        id: 13,
        name: "ADF Final + Stored Proc Conversion",
        hours: 700,
        tasks: [
            { task: "ADF Pipelines — Batch 6 (100 pipelines, final)", subtasks: "Import, convert, resolve, deploy, validate", hours: 200, owners: "Sr Data Engineer, Data Engineer" },
            { task: "Stored Procs — Standard Batch 4 (90 SPs)", subtasks: "Convert to Spark SQL, validate", hours: 180, owners: "Data Engineers (2)" },
            { task: "Stored Procs — Spark Low (25 SPs)", subtasks: "Template-driven PySpark conversion", hours: 200, owners: "Sr Data Engineers (2)" },
            { task: "Stored Procs — Spark Medium Batch 1 (12 SPs)", subtasks: "PySpark DataFrame conversion", hours: 192, owners: "Sr Data Engineer, Architect" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: ["Pipelines: 609 / 609 \u2713", "Standard SPs: 360 / 540", "Spark SPs: 37 / 75"]
    },
    {
        id: 14,
        name: "Stored Proc Conversion + Logic Apps & ADLS",
        hours: 700,
        tasks: [
            { task: "Stored Procs — Standard Batch 5 (90 SPs)", subtasks: "Convert to Spark SQL, validate", hours: 180, owners: "Data Engineers (2)" },
            { task: "Stored Procs — Spark Medium Batch 2 (13 SPs)", subtasks: "PySpark DataFrame conversion", hours: 208, owners: "Sr Data Engineers (2)" },
            { task: "Logic Apps — Batch 1 (75 apps)", subtasks: "Connection repointing, validation", hours: 150, owners: "Data Engineer" },
            { task: "ADLS Accounts — Batch 1 (26 accounts)", subtasks: "OneLake shortcuts or data copy, validation", hours: 104, owners: "Data Engineer, DBA" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: ["Standard SPs: 450 / 540", "Spark SPs: 50 / 75", "Logic Apps: 75 / 147"]
    },
    {
        id: 15,
        name: "Stored Proc Completion + Logic Apps & ADLS",
        hours: 700,
        tasks: [
            { task: "Stored Procs — Standard Batch 6 (90 SPs, final)", subtasks: "Convert to Spark SQL, validate", hours: 180, owners: "Data Engineers (2)" },
            { task: "Stored Procs — Spark High (25 SPs)", subtasks: "Full PySpark refactoring, medallion architecture", hours: 360, owners: "Sr Data Engineers (2), Architect" },
            { task: "Logic Apps — Batch 2 (72 apps, final)", subtasks: "Connection repointing, validation", hours: 144, owners: "Data Engineer" },
            { task: "ADLS Accounts — Batch 2 (27 accounts, final)", subtasks: "OneLake shortcuts or data copy, validation", hours: 108, owners: "Data Engineer, DBA" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: ["Standard SPs: 540 / 540 \u2713", "Spark SPs: 75 / 75 \u2713", "Logic Apps: 147 / 147 \u2713", "ADLS: 53 / 53 \u2713"]
    },
    {
        id: 16,
        name: "SP High Completion + Dev Hardening",
        hours: 700,
        tasks: [
            { task: "Stored Procs — Spark High (remaining)", subtasks: "Final refactoring, edge-case resolution", hours: 240, owners: "Sr Data Engineers (2), Architect" },
            { task: "Dev environment hardening", subtasks: "End-to-end regression, integration testing, performance baseline", hours: 280, owners: "Data Engineers (4), DBA" },
            { task: "SIT preparation", subtasks: "Test plan finalization, SIT environment deployment, test data setup", hours: 120, owners: "QA Lead, PM" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 60, owners: "PM" }
        ],
        milestones: ["All Dev Migration Complete"]
    },
    {
        id: 17,
        name: "SIT Cycle 1",
        hours: 700,
        tasks: [
            { task: "SIT deployment", subtasks: "Full artifact promotion to SIT environment", hours: 100, owners: "Sr Data Engineer, DBA" },
            { task: "Schema & data validation", subtasks: "Automated row counts, checksums, schema comparison across all 1,538 tables", hours: 200, owners: "QA Lead, Data Engineers" },
            { task: "Pipeline execution testing", subtasks: "End-to-end pipeline runs, trigger validation, error handling", hours: 200, owners: "Data Engineers, Sr Data Engineers" },
            { task: "Stored procedure functional testing", subtasks: "Execute all SPs against SIT data, compare outputs", hours: 150, owners: "Sr Data Engineers, DBA" },
            { task: "Defect triage & remediation", subtasks: "Fix critical/high defects from SIT Cycle 1", hours: 100, owners: "All Engineers" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting, stakeholder updates", hours: 50, owners: "PM" }
        ],
        milestones: ["SIT: 700 / 2,380"]
    },
    {
        id: 18,
        name: "SIT Cycle 2",
        hours: 700,
        tasks: [
            { task: "Logic App & ADLS validation", subtasks: "End-to-end Logic App flows, ADLS shortcut validation", hours: 150, owners: "Data Engineers" },
            { task: "Performance testing", subtasks: "Query performance benchmarks, pipeline throughput, capacity stress", hours: 200, owners: "DBA, Architect" },
            { task: "Regression testing (Cycle 1 fixes)", subtasks: "Re-validate all Cycle 1 defect fixes", hours: 150, owners: "QA Lead, Data Engineers" },
            { task: "Security & access testing", subtasks: "Role-based access, Entra ID integration, row-level security", hours: 100, owners: "DBA" },
            { task: "Defect triage & remediation", subtasks: "Fix remaining SIT defects", hours: 100, owners: "All Engineers" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: ["SIT: 1,400 / 2,380"]
    },
    {
        id: 19,
        name: "SIT Cycle 3",
        hours: 700,
        tasks: [
            { task: "Full regression (all workstreams)", subtasks: "Complete end-to-end regression across tables, pipelines, SPs, Logic Apps", hours: 300, owners: "All Engineers" },
            { task: "Data reconciliation sign-off", subtasks: "Final row-count, checksum, and business rule validation", hours: 150, owners: "QA Lead, DBA" },
            { task: "SIT exit criteria validation", subtasks: "Test summary report, defect closure, go/no-go assessment", hours: 100, owners: "QA Lead, PM" },
            { task: "UAT preparation", subtasks: "UAT environment deployment, test script handoff, business user onboarding", hours: 100, owners: "PM, QA Lead" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 50, owners: "PM" }
        ],
        milestones: ["SIT: 2,100 / 2,380"]
    },
    {
        id: 20,
        name: "SIT Closeout + UAT Start",
        hours: 700,
        tasks: [
            { task: "SIT final remediation", subtasks: "Remaining SIT defects, re-test, formal SIT sign-off", hours: 280, owners: "All Engineers, QA Lead" },
            { task: "UAT environment validation", subtasks: "Verify UAT deployment, connection health, data freshness", hours: 120, owners: "Sr Data Engineer, DBA" },
            { task: "UAT Cycle 1 — business user testing", subtasks: "Guided business user walkthroughs, report validation, pipeline verification", hours: 240, owners: "PM, QA Lead, Data Engineers" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 60, owners: "PM" }
        ],
        milestones: ["SIT: 2,380 / 2,380 \u2713", "UAT: 360 / 1,190"]
    },
    {
        id: 21,
        name: "UAT Cycle 2",
        hours: 700,
        tasks: [
            { task: "UAT business scenario testing", subtasks: "Full business process walkthroughs, edge-case scenarios", hours: 250, owners: "PM, QA Lead, Data Engineers" },
            { task: "UAT defect remediation", subtasks: "Fix UAT-discovered defects, re-test", hours: 200, owners: "All Engineers" },
            { task: "Performance acceptance testing", subtasks: "Business-critical query performance under UAT load", hours: 100, owners: "DBA, Architect" },
            { task: "UAT progress tracking & communication", subtasks: "Stakeholder updates, defect dashboards", hours: 50, owners: "PM" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: ["UAT: 960 / 1,190"]
    },
    {
        id: 22,
        name: "UAT Closeout",
        hours: 540,
        tasks: [
            { task: "UAT final remediation", subtasks: "Remaining defects, re-test, regression", hours: 130, owners: "All Engineers" },
            { task: "UAT exit criteria & sign-off", subtasks: "Formal UAT sign-off, acceptance documentation", hours: 50, owners: "PM, QA Lead" },
            { task: "Production readiness review", subtasks: "Go/no-go checklist, rollback plan, cutover runbook", hours: 80, owners: "Architect, PM" },
            { task: "Production environment preparation", subtasks: "Prod workspace validation, deployment pipeline dry-run", hours: 120, owners: "Sr Data Engineer, DBA" },
            { task: "Cutover planning", subtasks: "Detailed cutover schedule, communication plan, war room setup", hours: 60, owners: "PM, Architect" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: ["UAT: 1,190 / 1,190 \u2713"]
    },
    {
        id: 23,
        name: "Pre-Production & Cutover Prep",
        hours: 500,
        tasks: [
            { task: "Production deployment dry-run", subtasks: "Full deployment rehearsal to Prod-mirror environment", hours: 200, owners: "Sr Data Engineers, DBA" },
            { task: "Cutover runbook finalization", subtasks: "Step-by-step cutover instructions, rollback triggers, escalation paths", hours: 80, owners: "Architect, PM" },
            { task: "Stakeholder communication", subtasks: "Go-live readiness confirmation, business communication", hours: 40, owners: "PM" },
            { task: "Monitoring & alerting setup", subtasks: "Fabric capacity monitoring, pipeline alerting, SLA dashboards", hours: 100, owners: "Sr Data Engineer, DBA" },
            { task: "Team readiness", subtasks: "War room logistics, on-call rotation, escalation matrix", hours: 40, owners: "PM" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM" }
        ],
        milestones: []
    },
    {
        id: 24,
        name: "Production Cutover",
        hours: 357,
        tasks: [
            { task: "Production deployment execution", subtasks: "Full artifact deployment to Production", hours: 100, owners: "Sr Data Engineers, DBA" },
            { task: "Connection rerouting", subtasks: "Reroute all upstream/downstream connections to Fabric", hours: 57, owners: "Data Engineers, DBA" },
            { task: "Post-deployment validation", subtasks: "Smoke tests, critical path verification, data spot-checks", hours: 80, owners: "QA Lead, All Engineers" },
            { task: "Go-live monitoring", subtasks: "Real-time monitoring for first 48 hours, issue triage", hours: 80, owners: "All Engineers" },
            { task: "PM governance", subtasks: "Go-live communication, escalation management", hours: 40, owners: "PM" }
        ],
        milestones: ["Prod Cutover: 357 \u2713"]
    },
    {
        id: 25,
        name: "Hypercare & Closeout",
        hours: 532,
        tasks: [
            { task: "Hypercare support (2 weeks)", subtasks: "Production issue triage, hotfixes, performance tuning", hours: 200, owners: "All Engineers" },
            { task: "Knowledge transfer", subtasks: "Runbooks, operational documentation, client team training", hours: 120, owners: "Architect, Sr Data Engineers" },
            { task: "Synapse decommissioning plan", subtasks: "Source environment shutdown planning, data retention verification", hours: 60, owners: "Architect, DBA" },
            { task: "Project closeout", subtasks: "Lessons learned, final status report, accelerator feedback", hours: 80, owners: "PM, Architect" },
            { task: "PM governance", subtasks: "Final sprint ceremonies, project closeout", hours: 72, owners: "PM" }
        ],
        milestones: ["Project Complete"]
    }
];

const PHASE2_SPRINTS = [
    {
        id: 0,
        name: "Discovery + Accelerator Setup",
        hours: 700,
        tasks: [
            { task: "Project kickoff & governance", subtasks: "Charter, RACI, communication plan", hours: 100, owners: "PM", accelerator: "\u2014" },
            { task: "Architecture design", subtasks: "Fabric workspace topology, capacity, networking", hours: 160, owners: "Architect, DBA", accelerator: "\u2014" },
            { task: "Source assessment (automated)", subtasks: "DACPAC extraction, ADF assessment tool, SP complexity classification", hours: 120, owners: "Sr Data Engineers", accelerator: "Acc 1, Acc 2" },
            { task: "Accelerator deployment & config", subtasks: "Install PowerShell modules, configure Copilot, deploy validation frameworks, set up prompt library", hours: 160, owners: "Sr Data Engineers, Architect", accelerator: "All" },
            { task: "Migration wave planning", subtasks: "Dependency mapping, accelerated batch groupings", hours: 80, owners: "Architect, PM", accelerator: "\u2014" },
            { task: "Knowledge transfer", subtasks: "Fabric + accelerator tooling training", hours: 80, owners: "Architect, Sr Data Engineers", accelerator: "\u2014" }
        ],
        milestones: []
    },
    {
        id: 1,
        name: "Foundation + CI/CD Automation",
        hours: 671,
        tasks: [
            { task: "Fabric workspace provisioning", subtasks: "Dev/SIT/UAT/Prod workspaces, capacity, admin roles", hours: 100, owners: "Architect, DBA", accelerator: "Acc 4 (ARM/Bicep)" },
            { task: "Networking & security", subtasks: "Private endpoints, VNet gateways, Entra ID", hours: 120, owners: "Architect, DBA", accelerator: "\u2014" },
            { task: "Git integration + CI/CD automation", subtasks: "Repo structure, branch policies, automated deployment pipelines, GitHub Actions/ADO workflows", hours: 160, owners: "Sr Data Engineers", accelerator: "Acc 4" },
            { task: "Fabric DW creation + schema/security", subtasks: "Target warehouse, schemas (16), security (40), functions (4)", hours: 80, owners: "DBA", accelerator: "Acc 1" },
            { task: "Validation framework setup", subtasks: "Deploy schema/row-level/business rule validation notebooks", hours: 100, owners: "QA Lead, Sr Data Engineer", accelerator: "Acc 5" },
            { task: "Dev environment tooling", subtasks: "VS Code, notebook env, PowerShell, Copilot config", hours: 60, owners: "Sr Data Engineers", accelerator: "Acc 6" },
            { task: "PM governance", subtasks: "Sprint tracking, risk register", hours: 40, owners: "PM", accelerator: "\u2014" },
            { task: "Schema/security/functions migration", subtasks: "All 60 objects (schema 16, security 40, functions 4)", hours: 11, owners: "DBA", accelerator: "Acc 1" }
        ],
        milestones: []
    },
    {
        id: 2,
        name: "Synapse DW Migration Batch 1",
        hours: 700,
        tasks: [
            { task: "Synapse Tables — Batch 1 (380 tables)", subtasks: "DACPAC-driven migration, Copilot-assisted fix resolution, automated validation", hours: 646, owners: "Data Engineers (4), DBA, Sr Data Engineers", accelerator: "Acc 1 + Acc 6" },
            { task: "Synapse Views — Batch 1 (180 views)", subtasks: "Automated view migration with dependency awareness", hours: 136, owners: "Data Engineer", accelerator: "Acc 1 + Acc 6" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["Tables: 380 / 1,538", "Views: 180 / 362"]
    },
    {
        id: 3,
        name: "Synapse DW Migration Batch 2 + Views Complete",
        hours: 700,
        tasks: [
            { task: "Synapse Tables — Batch 2 (380 tables)", subtasks: "DACPAC migration, Copilot fix resolution, validation", hours: 646, owners: "Data Engineers (4), DBA, Sr Data Engineers", accelerator: "Acc 1 + Acc 6" },
            { task: "Synapse Views — Batch 2 (182 views, final)", subtasks: "View migration, dependency validation", hours: 136, owners: "Data Engineer", accelerator: "Acc 1 + Acc 6" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["Tables: 760 / 1,538", "Views: 362 / 362 \u2713"]
    },
    {
        id: 4,
        name: "Synapse DW Migration Batch 3 + ADF Start",
        hours: 700,
        tasks: [
            { task: "Synapse Tables — Batch 3 (380 tables)", subtasks: "DACPAC migration, Copilot fix resolution, validation", hours: 500, owners: "Data Engineers (3), DBA", accelerator: "Acc 1 + Acc 6" },
            { task: "ADF Assessment + Pipelines Batch 1 (150 pipelines)", subtasks: "PowerShell import/convert/resolve/export, validate", hours: 180, owners: "Sr Data Engineers (2), Data Engineer", accelerator: "Acc 2 + Acc 6" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["Tables: 1,140 / 1,538", "Pipelines: 150 / 609"]
    },
    {
        id: 5,
        name: "Synapse DW Complete + ADF Migration",
        hours: 700,
        tasks: [
            { task: "Synapse Tables — Batch 4 (398 tables, final)", subtasks: "DACPAC migration, final validation, sign-off", hours: 500, owners: "Data Engineers (3), DBA", accelerator: "Acc 1 + Acc 6" },
            { task: "ADF Pipelines — Batch 2 (150 pipelines)", subtasks: "PowerShell conversion, validate", hours: 180, owners: "Sr Data Engineers (2), Data Engineer", accelerator: "Acc 2 + Acc 6" },
            { task: "ADF Datasets — Batch 1 (225 datasets)", subtasks: "Automated repointing, validate", hours: 120, owners: "Data Engineer", accelerator: "Acc 2 + Acc 6" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["Tables: 1,538 / 1,538 \u2713", "Pipelines: 300 / 609", "Datasets: 225 / 450"]
    },
    {
        id: 6,
        name: "ADF Completion + SP Start",
        hours: 700,
        tasks: [
            { task: "ADF Pipelines — Batch 3 (159 pipelines)", subtasks: "PowerShell conversion, validate", hours: 191, owners: "Sr Data Engineer, Data Engineer", accelerator: "Acc 2 + Acc 6" },
            { task: "ADF Datasets — Batch 2 (225 datasets, final)", subtasks: "Repointing, validate", hours: 120, owners: "Data Engineer", accelerator: "Acc 2 + Acc 6" },
            { task: "ADF Pipelines — Batch 4 (150 pipelines)", subtasks: "PowerShell conversion, validate", hours: 180, owners: "Sr Data Engineer, Data Engineer", accelerator: "Acc 2 + Acc 6" },
            { task: "ADF Triggers (142 triggers)", subtasks: "Automated migration, validate", hours: 142, owners: "Data Engineer", accelerator: "Acc 2 + Acc 6" },
            { task: "Stored Procs — Standard Batch 1 (180 SPs)", subtasks: "Template-driven Spark SQL conversion, Copilot-assisted", hours: 252, owners: "Sr Data Engineer, Data Engineer", accelerator: "Acc 3 + Acc 6" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["Pipelines: 609 / 609 \u2713", "Datasets: 450 / 450 \u2713", "Triggers: 142 / 142 \u2713", "Standard SPs: 180 / 540"]
    },
    {
        id: 7,
        name: "Stored Proc Conversion",
        hours: 698,
        tasks: [
            { task: "Stored Procs — Standard Batch 2 (180 SPs)", subtasks: "Spark SQL conversion with templates", hours: 252, owners: "Data Engineers (2)", accelerator: "Acc 3 + Acc 6" },
            { task: "Stored Procs — Standard Batch 3 (180 SPs, final)", subtasks: "Spark SQL conversion with templates", hours: 252, owners: "Data Engineers (2)", accelerator: "Acc 3 + Acc 6" },
            { task: "Stored Procs — Spark Low (25 SPs)", subtasks: "Template-driven PySpark, starter notebooks", hours: 154, owners: "Sr Data Engineers (2)", accelerator: "Acc 3 + Acc 6" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["Standard SPs: 540 / 540 \u2713", "Spark Low: 25 / 25 \u2713"]
    },
    {
        id: 8,
        name: "Complex SP Conversion",
        hours: 685,
        tasks: [
            { task: "Stored Procs — Spark Medium (25 SPs)", subtasks: "PySpark DataFrames, pattern library", hours: 328, owners: "Sr Data Engineers (2), Architect", accelerator: "Acc 3 + Acc 6" },
            { task: "Stored Procs — Spark High Batch 1 (15 SPs)", subtasks: "Full PySpark refactoring, medallion architecture", hours: 317, owners: "Sr Data Engineers (2), Architect", accelerator: "Acc 3 + Acc 6" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["Spark Medium: 25 / 25 \u2713", "Spark High: 15 / 25"]
    },
    {
        id: 9,
        name: "SP High Complete + Logic Apps & ADLS Complete",
        hours: 694,
        tasks: [
            { task: "Stored Procs — Spark High Batch 2 (10 SPs, final)", subtasks: "Full PySpark refactoring", hours: 211, owners: "Sr Data Engineers (2), Architect", accelerator: "Acc 3 + Acc 6" },
            { task: "Logic Apps (147 apps)", subtasks: "Batch scripted repointing, validation", hours: 235, owners: "Data Engineers (2)", accelerator: "Acc 7" },
            { task: "ADLS Accounts (53 accounts)", subtasks: "OneLake shortcuts, scripted migration", hours: 148, owners: "Data Engineer, DBA", accelerator: "Acc 7" },
            { task: "Dev hardening", subtasks: "Integration testing, performance baseline", hours: 60, owners: "QA Lead, Data Engineers", accelerator: "\u2014" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["Spark High: 25 / 25 \u2713", "Logic Apps: 147 / 147 \u2713", "ADLS: 53 / 53 \u2713", "All Dev Complete"]
    },
    {
        id: 10,
        name: "SIT Cycle 1",
        hours: 700,
        tasks: [
            { task: "Automated SIT deployment", subtasks: "CI/CD pipeline-driven full deployment to SIT", hours: 60, owners: "Sr Data Engineer", accelerator: "Acc 4" },
            { task: "Automated schema & data validation", subtasks: "Validation framework: row counts, checksums, schema comparison for 1,538 tables", hours: 200, owners: "QA Lead, Data Engineers", accelerator: "Acc 5" },
            { task: "Pipeline execution testing", subtasks: "Automated pipeline test runs with assertion checks", hours: 180, owners: "Data Engineers, Sr Data Engineers", accelerator: "Acc 4 + Acc 5" },
            { task: "SP functional testing", subtasks: "Execute all SPs, automated output comparison", hours: 120, owners: "Sr Data Engineers", accelerator: "Acc 5" },
            { task: "Defect triage & remediation", subtasks: "Fix critical/high defects", hours: 100, owners: "All Engineers", accelerator: "Acc 6" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["SIT: 700 / 1,785"]
    },
    {
        id: 11,
        name: "SIT Cycle 2",
        hours: 680,
        tasks: [
            { task: "Logic App & ADLS validation", subtasks: "End-to-end flow validation, shortcut integrity", hours: 100, owners: "Data Engineers", accelerator: "Acc 5" },
            { task: "Performance testing", subtasks: "Automated benchmark suite, capacity stress testing", hours: 180, owners: "DBA, Architect", accelerator: "Acc 5" },
            { task: "Regression testing (Cycle 1 fixes)", subtasks: "Automated re-validation of all fixes", hours: 120, owners: "QA Lead, Data Engineers", accelerator: "Acc 5" },
            { task: "Security & access testing", subtasks: "Role-based access, Entra ID, RLS", hours: 80, owners: "DBA", accelerator: "\u2014" },
            { task: "Defect triage & remediation", subtasks: "Fix remaining SIT defects", hours: 100, owners: "All Engineers", accelerator: "Acc 6" },
            { task: "SIT exit preparation", subtasks: "Test summary, defect analysis", hours: 60, owners: "QA Lead, PM", accelerator: "\u2014" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["SIT: 1,380 / 1,785"]
    },
    {
        id: 12,
        name: "SIT Closeout + UAT Prep",
        hours: 700,
        tasks: [
            { task: "SIT final regression & sign-off", subtasks: "Full regression, SIT exit criteria validation", hours: 280, owners: "All Engineers, QA Lead", accelerator: "Acc 5" },
            { task: "SIT remediation (remaining)", subtasks: "Final defect fixes", hours: 125, owners: "All Engineers", accelerator: "Acc 6" },
            { task: "UAT environment deployment", subtasks: "Automated CI/CD promotion to UAT", hours: 60, owners: "Sr Data Engineer", accelerator: "Acc 4" },
            { task: "UAT preparation", subtasks: "Test scripts, business user onboarding, UAT kickoff", hours: 100, owners: "PM, QA Lead", accelerator: "\u2014" },
            { task: "UAT Cycle 1 start", subtasks: "Initial business user testing", hours: 100, owners: "PM, Data Engineers", accelerator: "\u2014" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 35, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["SIT: 1,785 / 1,785 \u2713"]
    },
    {
        id: 13,
        name: "UAT",
        hours: 670,
        tasks: [
            { task: "UAT business scenario testing", subtasks: "Full business process walkthroughs, edge cases", hours: 250, owners: "PM, QA Lead, Data Engineers", accelerator: "\u2014" },
            { task: "UAT defect remediation", subtasks: "Fix UAT defects, re-test", hours: 180, owners: "All Engineers", accelerator: "Acc 6" },
            { task: "Performance acceptance testing", subtasks: "Business-critical query performance", hours: 80, owners: "DBA, Architect", accelerator: "Acc 5" },
            { task: "Production readiness planning", subtasks: "Go/no-go checklist, rollback plan, cutover runbook", hours: 80, owners: "Architect, PM", accelerator: "Acc 4" },
            { task: "UAT progress tracking", subtasks: "Stakeholder updates, defect dashboards", hours: 40, owners: "PM", accelerator: "\u2014" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["UAT: 650 / 952"]
    },
    {
        id: 14,
        name: "UAT Closeout + Pre-Production",
        hours: 590,
        tasks: [
            { task: "UAT final remediation & sign-off", subtasks: "Remaining defects, formal UAT acceptance", hours: 200, owners: "All Engineers, QA Lead", accelerator: "Acc 6" },
            { task: "Production dry-run", subtasks: "Automated deployment rehearsal via CI/CD pipeline", hours: 120, owners: "Sr Data Engineers, DBA", accelerator: "Acc 4" },
            { task: "Cutover runbook finalization", subtasks: "Step-by-step instructions, rollback triggers", hours: 60, owners: "Architect, PM", accelerator: "Acc 4" },
            { task: "Monitoring & alerting setup", subtasks: "Capacity monitoring, pipeline alerting, SLA dashboards", hours: 80, owners: "Sr Data Engineer, DBA", accelerator: "Acc 4" },
            { task: "Prod environment validation", subtasks: "Connection health, data freshness, security", hours: 60, owners: "DBA", accelerator: "Acc 5" },
            { task: "Stakeholder communication", subtasks: "Go-live readiness confirmation", hours: 30, owners: "PM", accelerator: "\u2014" },
            { task: "PM governance", subtasks: "Sprint ceremonies, status reporting", hours: 40, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["UAT: 952 / 952 \u2713"]
    },
    {
        id: 15,
        name: "Production Cutover",
        hours: 303,
        tasks: [
            { task: "Automated production deployment", subtasks: "CI/CD pipeline execution for full Prod deployment", hours: 60, owners: "Sr Data Engineers, DBA", accelerator: "Acc 4" },
            { task: "Connection rerouting", subtasks: "Automated reroute of upstream/downstream connections", hours: 43, owners: "Data Engineers, DBA", accelerator: "Acc 4" },
            { task: "Post-deployment validation", subtasks: "Automated smoke tests, critical path verification", hours: 60, owners: "QA Lead, All Engineers", accelerator: "Acc 5" },
            { task: "Go-live monitoring", subtasks: "Real-time monitoring for first 48 hours", hours: 80, owners: "All Engineers", accelerator: "Acc 4" },
            { task: "PM governance", subtasks: "Go-live communication, escalation management", hours: 60, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["Prod Cutover: 303 \u2713"]
    },
    {
        id: 16,
        name: "Hypercare & Closeout",
        hours: 487,
        tasks: [
            { task: "Hypercare support (2 weeks)", subtasks: "Production issue triage, hotfixes, tuning", hours: 180, owners: "All Engineers", accelerator: "Acc 6" },
            { task: "Knowledge transfer", subtasks: "Operational runbooks, client team training", hours: 100, owners: "Architect, Sr Data Engineers", accelerator: "\u2014" },
            { task: "Synapse decommissioning plan", subtasks: "Shutdown planning, data retention verification", hours: 50, owners: "Architect, DBA", accelerator: "\u2014" },
            { task: "Accelerator retrospective", subtasks: "Document accelerator effectiveness, update pattern library", hours: 60, owners: "Sr Data Engineers, Architect", accelerator: "\u2014" },
            { task: "Project closeout", subtasks: "Lessons learned, final report, accelerator feedback", hours: 60, owners: "PM, Architect", accelerator: "\u2014" },
            { task: "PM governance", subtasks: "Final ceremonies, closeout", hours: 37, owners: "PM", accelerator: "\u2014" }
        ],
        milestones: ["Project Complete"]
    }
];

/** Comparison statistics */
const SPRINT_COMPARISON = {
    phase1: { sprints: 25, weeks: 50, hours: 17329 },
    phase2: { sprints: 16, weeks: 32, hours: 11078 },
    hoursSaved: 6251,
    percentSaved: 36
};

/** Additional work breakdown (hours saved by workstream) */
const ADDITIONAL_WORK = {
    total: 6251,
    additionalSprints: 9,
    additionalWeeks: 18,
    breakdown: [
        { workstream: "Synapse Tables", hoursSaved: 2891, baseHours: 6152, acceleratedHours: 3261 },
        { workstream: "ADF Pipelines/Datasets/Triggers", hoursSaved: 1079, baseHours: 2402, acceleratedHours: 1323 },
        { workstream: "Stored Procedures", hoursSaved: 514, baseHours: 2280, acceleratedHours: 1766 },
        { workstream: "Synapse Views/Functions/Schema/Security", hoursSaved: 279, baseHours: 567, acceleratedHours: 288 },
        { workstream: "SIT/UAT/Prod Environments", hoursSaved: 887, baseHours: 3927, acceleratedHours: 3040 },
        { workstream: "PM / Governance / Architecture", hoursSaved: 501, baseHours: 1600, acceleratedHours: 1099 },
        { workstream: "Logic Apps & ADLS", hoursSaved: 123, baseHours: 506, acceleratedHours: 383 }
    ]
};
