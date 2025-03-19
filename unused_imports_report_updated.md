# Unused Imports Report

**Total unused imports found: 40**

## Files by Unused Import Count

| File | Unused Imports |
|------|---------------|
| src/code_conductor/ai_work_effort_creator.py | 5 |
| src/code_conductor/utils/thought_process.py | 3 |
| src/code_conductor/work_efforts/counter.py | 3 |
| src/code_conductor/work_efforts/create_work_node.py | 3 |
| src/code_conductor/work_efforts/scripts/work_effort_manager.py | 3 |
| src/code_conductor/scripts/index_work_efforts.py | 2 |
| src/code_conductor/utils/directory_scanner.py | 2 |
| src/code_conductor/utils/migrate_ai_setup.py | 2 |
| src/code_conductor/work_efforts/consolidate_work_efforts.py | 2 |
| src/code_conductor/work_efforts/scripts/ai_work_effort_creator.py | 2 |
| src/code_conductor/core/new_feature.py | 1 |
| src/code_conductor/creators/project.py | 1 |
| src/code_conductor/creators/work_efforts.py | 1 |
| src/code_conductor/event_system.py | 1 |
| src/code_conductor/providers/ollama.py | 1 |
| src/code_conductor/providers/openai.py | 1 |
| src/code_conductor/scripts/cc_new.py | 1 |
| src/code_conductor/utils/convert_to_folders.py | 1 |
| src/code_conductor/utils/helpers.py | 1 |
| src/code_conductor/work_effort.py | 1 |
| src/code_conductor/work_effort_manager.py | 1 |
| src/code_conductor/work_efforts/update_status.py | 1 |
| src/code_conductor/workflow/run_workflow.py | 1 |

## Detailed Report

### src/code_conductor/ai_work_effort_creator.py

| Import | Line | Column |
|--------|------|--------|
| `src.code_conductor.work_efforts.scripts.ai_work_effort_creator.setup_work_efforts_structure` | 12 | 0 |
| `src.code_conductor.work_efforts.scripts.ai_work_effort_creator.create_work_effort` | 12 | 0 |
| `src.code_conductor.work_efforts.scripts.ai_work_effort_creator.create_content` | 12 | 0 |
| `src.code_conductor.work_efforts.scripts.ai_work_effort_creator.main` | 12 | 0 |
| `src.code_conductor.work_efforts.scripts.ai_work_effort_creator.main_async` | 12 | 0 |

### src/code_conductor/utils/thought_process.py

| Import | Line | Column |
|--------|------|--------|
| `os` | 1 | 0 |
| `time` | 7 | 0 |
| `datetime.datetime` | 8 | 0 |

### src/code_conductor/work_efforts/counter.py

| Import | Line | Column |
|--------|------|--------|
| `typing.Tuple` | 19 | 0 |
| `typing.List` | 19 | 0 |
| `typing.Union` | 19 | 0 |

### src/code_conductor/work_efforts/create_work_node.py

| Import | Line | Column |
|--------|------|--------|
| `fnmatch` | 62 | 0 |
| `pathlib.Path` | 63 | 0 |
| `shutil` | 64 | 0 |

### src/code_conductor/work_efforts/scripts/work_effort_manager.py

| Import | Line | Column |
|--------|------|--------|
| `typing.Tuple` | 21 | 0 |
| `work_efforts.counter.WorkEffortCounter` | 31 | 8 |
| `work_efforts.counter.format_work_effort_filename` | 31 | 8 |

### src/code_conductor/scripts/index_work_efforts.py

| Import | Line | Column |
|--------|------|--------|
| `datetime.datetime` | 14 | 0 |
| `typing.Optional` | 16 | 0 |

### src/code_conductor/utils/directory_scanner.py

| Import | Line | Column |
|--------|------|--------|
| `typing.Set` | 4 | 0 |
| `typing.Tuple` | 4 | 0 |

### src/code_conductor/utils/migrate_ai_setup.py

| Import | Line | Column |
|--------|------|--------|
| `re` | 26 | 0 |
| `pathlib.Path` | 30 | 0 |

### src/code_conductor/work_efforts/consolidate_work_efforts.py

| Import | Line | Column |
|--------|------|--------|
| `yaml` | 68 | 0 |
| `pathlib.Path` | 70 | 0 |

### src/code_conductor/work_efforts/scripts/ai_work_effort_creator.py

| Import | Line | Column |
|--------|------|--------|
| `time` | 8 | 0 |
| `shutil` | 10 | 0 |

### src/code_conductor/core/new_feature.py

| Import | Line | Column |
|--------|------|--------|
| `os` | 15 | 0 |

### src/code_conductor/creators/project.py

| Import | Line | Column |
|--------|------|--------|
| `sys` | 2 | 0 |

### src/code_conductor/creators/work_efforts.py

| Import | Line | Column |
|--------|------|--------|
| `datetime.datetime` | 2 | 0 |

### src/code_conductor/event_system.py

| Import | Line | Column |
|--------|------|--------|
| `typing.Optional` | 168 | 4 |

### src/code_conductor/providers/ollama.py

| Import | Line | Column |
|--------|------|--------|
| `sys` | 4 | 0 |

### src/code_conductor/providers/openai.py

| Import | Line | Column |
|--------|------|--------|
| `json` | 2 | 0 |

### src/code_conductor/scripts/cc_new.py

| Import | Line | Column |
|--------|------|--------|
| `src.code_conductor.cli.cli.find_nearest_config` | 38 | 12 |

### src/code_conductor/utils/convert_to_folders.py

| Import | Line | Column |
|--------|------|--------|
| `datetime.datetime` | 12 | 0 |

### src/code_conductor/utils/helpers.py

| Import | Line | Column |
|--------|------|--------|
| `platform` | 4 | 0 |

### src/code_conductor/work_effort.py

| Import | Line | Column |
|--------|------|--------|
| `os` | 11 | 0 |

### src/code_conductor/work_effort_manager.py

| Import | Line | Column |
|--------|------|--------|
| `src.code_conductor.work_efforts.scripts.work_effort_manager.WorkEffortManager` | 10 | 0 |

### src/code_conductor/work_efforts/update_status.py

| Import | Line | Column |
|--------|------|--------|
| `src.code_conductor.workflow.workflow_runner.COMPLETED_DIR` | 10 | 0 |

### src/code_conductor/workflow/run_workflow.py

| Import | Line | Column |
|--------|------|--------|
| `datetime` | 13 | 0 |

