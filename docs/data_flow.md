# Work Effort Management System: Data Flow & Sources of Truth

## System Architecture and Data Flow

```
                  ┌─────────────────────────┐
                  │                         │
                  │    Command Line Tools   │
                  │    (cc-work, etc.)      │
                  │                         │
                  └───────────┬─────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    WorkEffortManager                        │
│                                                             │
└─┬─────────────────────┬─────────────────────┬───────────────┘
  │                     │                     │
  ▼                     ▼                     ▼
┌──────────────┐   ┌──────────────┐    ┌─────────────────┐
│              │   │              │    │                 │
│ Create       │   │ Query        │    │ Update Status   │
│ Work Effort  │   │ Work Efforts │    │ & Metadata      │
│              │   │              │    │                 │
└───────┬──────┘   └────┬─────────┘    └────────┬────────┘
        │               │                       │
        ▼               │                       ▼
┌────────────────┐      │             ┌──────────────────────┐
│                │      │             │                      │
│ File System    │      │             │ Modify Files &       │
│ (Write Files)  │◄─────┘             │ Update Index         │
│                │                    │                      │
└────────┬───────┘                    └──────────┬───────────┘
         │                                       │
         │                                       │
         ▼                                       ▼
┌────────────────────────────────────────────────────────────┐
│                                                            │
│            SINGLE SOURCE OF TRUTH                          │
│                                                            │
│            .code_conductor/work_index.json                 │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Sources of Truth in the System

| Component | Role | Source Priority |
|-----------|------|-----------------|
| **Central Index** (.code_conductor/work_index.json) | PRIMARY source of truth | 1 (Highest) |
| **File System** (work_efforts/) | Canonical data storage, verification reference | 2 |
| **In-Memory Cache** (WorkEffortManager) | Runtime state for active processes | 3 |
| **Counter System** (work_efforts/counter.json) | Sequential numbering state | Independent |

## Data Flow During Key Operations

### 1. Work Effort Creation

```
User → cc-work command → WorkEffortManager →
  → Creates folder/file in file system
  → Updates in-memory cache
  → Updates central index
  → Emits event
```

### 2. Work Effort Retrieval

```
Query → WorkEffortManager →
  → First tries central index
  → Falls back to file system scan if needed
  → Returns results from in-memory cache
```

### 3. Work Effort Status Update

```
Update command → WorkEffortManager →
  → Moves files in file system
  → Updates file content
  → Updates in-memory cache
  → Updates central index
  → Emits event
```

### 4. System Recovery

```
System start → WorkEffortManager →
  → Tries to load from central index
  → If index corrupted/missing, rebuilds from file system
  → Recreates index
  → System operational
```

## Integrity Maintenance

The system maintains integrity through:

1. **Atomic Operations**: Write-to-temp and rename pattern for index updates
2. **Directory Verification**: Checks for required directories before operations
3. **File Locking**: Prevents concurrent access to the same files
4. **Fallback Mechanisms**: Can rebuild from file system if index is corrupted
5. **Event System**: Propagates changes throughout the system