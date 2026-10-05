# Architecture

Three pages that sit above the per-artifact docs.

| Page | What it holds |
|---|---|
| [[projects.md]] | The project manifest from `tastrade.pjx`: members by type with descriptions, exclusions, build settings, what is on disk but outside the project, and which of the 83 bitmaps anything uses |
| [[startup.md]] | Start-up and shutdown sequence, as a diagram and step by step, with what `DEBUGMODE` changes |
| [[framework.md]] | Framework overview: entry and environment, application object, base classes and the toolbar contract, forms, data, reports and menus, and the conventions a rebuild must reproduce |

The per-artifact docs these draw on: [[../03-data-model/README.md]], [[../04-forms/README.md]], [[../05-classes/README.md]], [[../06-reports/README.md]], [[../07-menus/README.md]], [[../08-programs/README.md]]; the generated census is in [[../00-inventory/README.md]].
