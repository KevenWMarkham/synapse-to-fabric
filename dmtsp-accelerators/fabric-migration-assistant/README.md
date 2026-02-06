# Accelerator 01: Fabric Migration Assistant for Data Warehouse

**Target:** Synapse DW Schema/Tables
**Productivity Gain:** 40-55%
**Build Effort:** Low
**Reusability:** Global — built once, deployed at every Synapse-to-Fabric engagement

## What It Is

A reusable accelerator built on the native GA tool in the Fabric portal, providing a guided, four-step migration experience for moving Synapse dedicated SQL pools into Fabric Data Warehouse. Built once by a central team and deployed across all client engagements to reduce hours globally. Microsoft offers personalized migration support through their Migration Factory at no cost.

## How It Works

1. **Metadata Migration via DACPAC** — Extract schema definitions using Visual Studio, VS Code, or SqlPackage CLI
2. **AI-Assisted Problem Resolution** — Copilot analyzes broken scripts and suggests fixes with inline comments
3. **Data Copy via Fabric Data Factory** — Integrated copy jobs for one-time full or continuous incremental copying
4. **Connection Rerouting** — REST API identifies and reroutes connections to new Fabric warehouse

## Impact by Object Type

| Object | Count | Base Hours | Impact |
|--------|-------|------------|--------|
| Tables | 1,538 | 6,152 | Primary target |
| Views | 362 | 543 | Automated find/replace |
| Functions | 4 | 4 | Near-complete automation |
| Schema | 16 | 5 | Fully automated |
| Security | 40 | 10 | Partial automation |

## DMTSP Buildout

Create reusable **DACPAC Extraction and Migration Runbook** deployable at every client engagement:

- Pre-flight validation checklists
- Known T-SQL incompatibility patterns with pre-built fix scripts
- Copilot prompt library optimized for migration fix scenarios
