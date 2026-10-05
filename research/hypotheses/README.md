# Research Hypotheses Registry

This directory contains formal, tracked hypothesis manifests. Each hypothesis is assigned a unique identifier (`HYP-xxxxxx`) and linked to experiments that test it.

## Schema
Hypotheses are defined in JSON or Markdown with the following properties:
- `hypothesis_id`: Unique identifier
- `title`: Short title
- `statement`: Scientific falsifiable proposition
- `independent_variables`: Variables manipulated
- `dependent_variables`: Measured outcomes
- `acceptance_criteria`: Metric threshold required to validate or refute
- `status`: PROPOSED | ACTIVE | VALIDATED | REFUTED
