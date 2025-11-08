# Architecture

## Core Principles

- **Layered Modularity** — Each stage performs a single, bounded responsibility with clearly defined inputs and outputs.
- **Composable Pipelines** — Controllers orchestrate interchangeable stages; new workflows can combine or skip modules as
needed.
- **Traceability by Design** — Every transformation produces a warning, error, or change-log record.
- **Strict Type Boundaries** — Each model defines a typed data contract between stages.
- **Separation of Rules & Flow** — Verification and normalization rules live in dedicated engines, decoupled from orchestration logic.
- **Fail Fast, Fail Loud** — The Verifier enforces strict correctness before data leaves the system or reaches the export layer.

## System Overview

This document describes the internal architecture and data-processing pipeline for **BomCheck**, a modular BOM ingestion, cleaning, verification, and export framework designed for traceability and rule-based automation.

### `main.py`

- Application Entry. Launches the application.
- Invokes the **Menu** to start user interaction.

### Menu

- Presents available workflows (interactive or CLI-based).
- Allows the user to select a **Workflow**.

### Workflow

- Encapsulates a real-world task (e.g., *Check BOM*, *Compare BOMs*, *Create DB Template*).
- Chooses and executes the appropriate **Controller**.

### Controller

- Orchestrates pipeline stages in order.
- Manages coordination, logging, progress, and error handling.
- Entry point for full workflows such as *Review BOM* or *Generate Template*.

### Importer

- Ingests raw input from files or APIs.
- Handles decoding, encoding, and deserialization.
- Converts sources (e.g., Excel workbook) → `pandas.DataFrame`.

### Parsers

- Detects the BOM format and version (e.g., Version 3).
- Extracts header/body regions and constructs structured internal **Models**.
- Bridges **external formats** to **system-native data structures**.

### Models

- Core dataclasses shared across all stages (`raw`, `clean`, `canonical`).
- Define strict type and field contracts.
- Serve as the foundation for validation, transformation, and export.

### Checker

- Performs **non-blocking diagnostics** on parsed data.
- Detects missing headers, invalid text, or inconsistent structures.
- Emits **warnings** for early feedback without stopping execution.
- Internally uses the **`review`** rules engine.

### Review

- **Diagnostic Rules Engine**
- Library of lightweight, pre-cleaning validation rules.
- Focused on completeness, structure, and early quality indicators.
- Emits warnings for anomalies rather than raising exceptions.

### Cleaner

- Performs **type coercion and normalization**.
- Converts strings to typed values, trims whitespace, and standardizes text and units.
- Produces a **change log** documenting all applied transformations.
- Internally uses the **`coerce`** normalization engine.

### Coerce

- **Normalization Engine**
- Manages field-level conversions and text normalization.
- Enforces consistent numeric, date, and categorical representation.
- Provides shared coercion utilities used across cleaning and mapping logic.

### Fixer

- Applies **rule-based automatic corrections** after cleaning.
- Resolves mismatched units, vendor aliasing, or arithmetic inconsistencies.
- Supports manual review for unresolved issues.
- Extends the cumulative **change log**.
- Internally uses the **`correct`** auto-correction engine.

### Correction

- **Auto-Correction Engine**
- Encapsulates fix logic, heuristics, and lookup dictionaries.
- Normalizes vendor names (e.g., “AVX Corporation” → “AVX”) and corrects known data issues.
- Logs each correction with its rule source and reason.

### Verifier

- Executes **blocking verification rules** to ensure all data meets defined requirements.
- Validates schema completeness, data integrity, and inter-field consistency. 
- Raises **errors** for any rule violations. 
- Serves as the **final quality gate** before export. 
- Internally uses the **`approve`** verification engine.

### Approve

- **Verification Engine**
- Implements strict requirement-based verification rules.
- Ensures data meets schema, business, and rule-set compliance.
- Produces structured **error reports** and approval summaries.
- Returns pass/fail results to control downstream execution.

### Mapper

- Converts verified clean data into a **canonical system-wide model**.
- Normalizes schema versions, aligns field names, and merges variants.
- Produces the `CanonicalModel` used for export or database integration.

### Exporter

- Serializes the canonical model into desired formats: Excel, CSV, JSON, DB schema, or REST API payload.
- Handles output version tagging, structure, and formatting consistency.
- Ensures safe file I/O and destination compatibility.

### Runtime

- Centralized repository for **read-only constants** and runtime configuration.
- Loaded at startup or on demand.
- Provides validated keys, UI messages, and global settings.

### Utilities

- Reusable system tools shared across modules:
    - `console` – CLI interaction utilities
    - `excel_io` – format-specific file I/O handlers
    - `file_path` – file path helper
    - `folder_path` – folder path helpers
    - `json_io` – format-specific file I/O handlers
    - `parser` – low-level parsing and type-safety helpers
    - `sanitizer` – text cleaning and normalization
    - `text_io` – format-specific file I/O handlers

---

## 🔄 Sample End-to-End Data Flow

```text
Input File
   ↓
Importer [Excel → DataFrame]
   ↓
Parser [DataFrame → raw]
   ↓
Checker [raw → warnings] ← uses review.*
   ↓
Cleaner [raw → clean + change_log] ← uses coerce.*
   ↓
Fixer [clean → clean + change_log] ← uses correction.*
   ↓
Verifier [clean → errors] ← uses approve.*
   ↓
Mapper [clean → canonical]
   ↓
Exporter [CanonicalModel → Excel]
