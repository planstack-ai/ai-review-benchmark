# Existing Codebase

## Path Traversal Attack

```
User requests: filename = "../../../etc/passwd"
Code: new File(baseDir + "/" + filename)
Result: Accesses /etc/passwd instead of /reports/../../../etc/passwd
```

## Vulnerable Pattern

```java
// VULNERABLE: User input directly used in path
@GetMapping("/download")
public Resource downloadFile(@RequestParam String filename) {
    File file = new File("/app/reports/" + filename);  // Path traversal!
    return new FileSystemResource(file);
}
```

## Safe Pattern

```java
// SAFE: Validate and normalize path
@GetMapping("/download")
public Resource downloadFile(@RequestParam String filename) {
    Path basePath = Paths.get("/app/reports").toAbsolutePath().normalize();
    Path filePath = basePath.resolve(filename).normalize();

    // Ensure file is within allowed directory
    if (!filePath.startsWith(basePath)) {
        throw new SecurityException("Access denied");
    }

    return new FileSystemResource(filePath.toFile());
}
```

## Usage Guidelines

- Never trust user input for file paths
- Use Path.normalize() to resolve .. and .
- Verify final path is within allowed directory
- Use whitelist of allowed characters for filenames
- Consider using UUIDs instead of user-provided names
