# Existing Codebase

## Path Traversal Attack

```
User requests: filename = "../../../etc/passwd"
Code: File(baseDir, filename)
Result: Accesses /etc/passwd instead of /reports/../../../etc/passwd
```

## Vulnerable Pattern

```kotlin
// VULNERABLE: User input directly used in path
@GetMapping("/download")
fun downloadFile(@RequestParam filename: String): Resource {
    val file = File("/app/reports/$filename")  // Path traversal!
    return FileSystemResource(file)
}
```

## Safe Pattern

```kotlin
// SAFE: Validate and normalize path
@GetMapping("/download")
fun downloadFile(@RequestParam filename: String): Resource {
    val basePath = Paths.get("/app/reports").toAbsolutePath().normalize()
    val filePath = basePath.resolve(filename).normalize()

    // Ensure file is within allowed directory
    if (!filePath.startsWith(basePath)) {
        throw SecurityException("Access denied")
    }

    return FileSystemResource(filePath.toFile())
}
```

## Usage Guidelines

- Never trust user input for file paths
- Use Path.normalize() to resolve .. and .
- Verify final path is within allowed directory
- Use whitelist of allowed characters for filenames
- Consider using UUIDs instead of user-provided names
