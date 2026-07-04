# Common Spring Boot Starter & Dependency Pitfalls

## Wrong Artifact IDs

| Wrong | Correct | Notes |
|-------|---------|-------|
| `spring-boot-starter-webmvc` | `spring-boot-starter-web` | webmvc artifact doesn't exist |
| `spring-boot-starter-data-jpa-test` | `spring-boot-starter-test` | Only one test starter exists |
| `spring-boot-starter-validation-test` | `spring-boot-starter-test` | Same — single test starter |
| `spring-boot-starter-webmvc-test` | `spring-boot-starter-test` | Same |

Only **one** test dependency needed:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

## Redundant Compiler Plugin Config

Spring Boot 4.x parent POM (`spring-boot-starter-parent`) already configures annotation processor discovery via `spring-boot-maven-plugin` + `maven-compiler-plugin`. You do **not** need a manual `<annotationProcessorPaths>` block in the compiler plugin. Having one can:

- Override the parent's processor discovery
- Break if other processors (MapStruct, etc.) are added later
- Be unnecessary boilerplate (Lombok on classpath is auto-detected)

Remove it unless you have a specific reason to pin processor order.

## BCryptPasswordEncoder Setup

Dependency (no version needed — BOM-managed):
```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-crypto</artifactId>
</dependency>
```

Two patterns:

**Pattern A — Bean (clean, testable)**
```java
@Configuration
public class SecurityConfig {
    @Bean
    public BCryptPasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```
Then inject into service:
```java
@Service
public class UserServiceImpl {
    private final BCryptPasswordEncoder encoder;
    // constructor injection
}
```

**Pattern B — New instance (simple, one-off)**
```java
String hash = new BCryptPasswordEncoder().encode(plainPassword);
```

Always hash before saving. Never store plaintext.

## Circular Self-Injection Anti-Pattern

```java
// WRONG — injecting own interface in its own Impl
public class UserServiceImpl implements UserService {
    private UserService userService;  // circular!
}

// RIGHT — inject the repository
public class UserServiceImpl implements UserService {
    private UserRepository userRepository;
}
```

## Entity: `unique=true` on Passwords

```java
// BAD — two users can have the same BCrypt hash
@Column(name = "hashed_password", nullable = false, unique = true)

// CORRECT
@Column(name = "hashed_password", nullable = false)
```

BCrypt is designed for hash collisions across users (that's fine — two users choosing "password123" produce the same hash). Unique constraint will break on insert.
