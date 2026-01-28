# Plan: Rename springboot to springboot-java

## Objective

Rename the Spring Boot Java framework identifier from `springboot` to `springboot-java` for consistency with `springboot-kotlin`.

## Rationale

- **Consistency**: `springboot` vs `springboot-kotlin` is asymmetric
- **Clarity**: `springboot-java` explicitly indicates the language
- **Extensibility**: Easier to add other JVM languages in the future

## Changes Required

### Phase 1: Rename Directory and Files

| Current | New |
|---------|-----|
| `cases/springboot/` | `cases/springboot-java/` |
| `patterns_springboot.yaml` | `patterns_springboot_java.yaml` |

### Phase 2: Update Python Scripts

#### scripts/runner.py

1. **Line 34** - Type definition:
   ```python
   # Before
   FrameworkName = Literal["rails", "django", "laravel", "springboot", "springboot-kotlin"]
   # After
   FrameworkName = Literal["rails", "django", "laravel", "springboot-java", "springboot-kotlin"]
   ```

2. **Lines 55-59** - FRAMEWORK_CONFIG key:
   ```python
   # Before
   "springboot": { ... }
   # After
   "springboot-java": { ... }
   ```

3. **Line 565** - build_prompt() framework check:
   ```python
   # Before
   elif framework == "springboot":
   # After
   elif framework == "springboot-java":
   ```

4. **Line 958** - CLI argument choices:
   ```python
   # Before
   choices=["rails", "django", "laravel", "springboot", "springboot-kotlin"]
   # After
   choices=["rails", "django", "laravel", "springboot-java", "springboot-kotlin"]
   ```

#### scripts/generator.py

1. **Lines 53-59** - FRAMEWORK_CONFIG key and patterns_file:
   ```python
   # Before
   "springboot": {
       ...
       "patterns_file": "patterns_springboot.yaml",
   }
   # After
   "springboot-java": {
       ...
       "patterns_file": "patterns_springboot_java.yaml",
   }
   ```

2. **Line 198** - Framework-specific prompt condition:
   ```python
   # Before
   elif framework == "springboot":
   # After
   elif framework == "springboot-java":
   ```

3. **Line 267** - framework_names mapping:
   ```python
   # Before
   framework_names = {"django": "Django", "springboot": "Spring Boot", ...}
   # After
   framework_names = {"django": "Django", "springboot-java": "Spring Boot (Java)", ...}
   ```

4. **Line 396** - Implementation generation prompt condition:
   ```python
   # Before
   elif framework == "springboot":
   # After
   elif framework == "springboot-java":
   ```

5. **Lines 605-606** - meta.json framework field:
   ```python
   # Before
   elif framework == "springboot":
       meta["framework"] = "springboot"
   # After
   elif framework == "springboot-java":
       meta["framework"] = "springboot-java"
   ```

6. **Line 746** - CLI argument choices:
   ```python
   # Before
   choices=["rails", "django", "springboot"]
   # After
   choices=["rails", "django", "springboot-java"]
   ```

#### scripts/evaluator.py

1. **Line 1115** - CLI argument choices:
   ```python
   # Before
   choices=["rails", "django", "laravel", "springboot", "springboot-kotlin"]
   # After
   choices=["rails", "django", "laravel", "springboot-java", "springboot-kotlin"]
   ```

### Phase 3: Update meta.json Files

Update all 33 meta.json files in `cases/springboot-java/`:

```json
// Before
"framework": "springboot"
// After
"framework": "springboot-java"
```

**Files to update:**
- CALC_001 through CALC_006 (6 files)
- AUTH_001 through AUTH_004 (4 files)
- STATE_001 through STATE_004 (4 files)
- TIME_001 through TIME_003 (3 files)
- STOCK_001, STOCK_002 (2 files)
- NOTIFY_001 (1 file)
- SPRING_001 through SPRING_008 (8 files)
- FP_001 through FP_005 (5 files)

### Phase 4: Update Documentation

#### CLAUDE.md

1. Update command examples:
   ```bash
   # Before
   python scripts/generator.py --framework springboot --pattern CALC_001
   python scripts/runner.py --model claude-sonnet --framework springboot

   # After
   python scripts/generator.py --framework springboot-java --pattern CALC_001
   python scripts/runner.py --model claude-sonnet --framework springboot-java
   ```

2. Update Supported Frameworks table:
   ```markdown
   | Spring Boot (Java) | patterns_springboot_java.yaml | cases/springboot-java/ | impl.java |
   ```

#### docs/plans/add-springboot-support.md

Update all references from `springboot` to `springboot-java` for historical accuracy.

### Phase 5: Result Files (Optional)

Existing result files in `results/` directories contain `"framework": "springboot"`. These can be left as-is since they represent historical data, or updated for consistency.

**Recommendation**: Leave historical results unchanged.

## Execution Order

1. Rename `patterns_springboot.yaml` to `patterns_springboot_java.yaml`
2. Rename `cases/springboot/` directory to `cases/springboot-java/`
3. Update all Python scripts (runner.py, generator.py, evaluator.py)
4. Update all 33 meta.json files
5. Update CLAUDE.md documentation
6. Update planning document (optional)
7. Run syntax check on Python files
8. Test with a sample command

## Verification

After changes, verify:

```bash
# Syntax check
python3 -m py_compile scripts/runner.py
python3 -m py_compile scripts/generator.py
python3 -m py_compile scripts/evaluator.py

# Functional test
python scripts/runner.py --help  # Should show springboot-java in choices
python scripts/generator.py --help  # Should show springboot-java in choices
```

## Rollback Plan

If issues arise:
1. `git checkout .` to revert all changes
2. `git mv cases/springboot-java cases/springboot` if directory was renamed
3. `git mv patterns_springboot_java.yaml patterns_springboot.yaml` if file was renamed
