# Spring Boot 4.1.0 + Java 25 Migration Pitfalls

This document captures concrete gotchas encountered while building with Spring Boot 4.1.0 on Java 25, specifically with Jackson 3.x, YAML configuration, and the ad-hoc verification approach used for end-to-end testing.

## Jackson 3.x (tools.jackson.databind)

Spring Boot 4.1.0 ships with Jackson 3.x, which moved from the `com.fasterxml.jackson` package to `tools.jackson.databind`. This has several implications:

### Renamed/Removed SerializationFeature Enums

The enum `WRITE_DATES_AS_TIMESTAMPS` does **not** exist in Jackson 3.x. Trying to set it in `application.yml` will fail at startup:

```
Failed to bind properties under 'spring.jackson.serialization' to java.util.Map<tools.jackson.databind.SerializationFeature, java.lang.Boolean>
No enum constant tools.jackson.databind.SerializationFeature.write-dates-as-timestamps
```

**Valid enum values in Jackson 3.x** (as of SB 4.1.0):
- `INDENT_OUTPUT`
- `FAIL_ON_EMPTY_BEANS`
- `WRAP_ROOT_VALUE`
- `WRITE_SELF_REFERENCES_AS_NULL`
- `ORDER_MAP_ENTRIES_BY_KEYS`
- `USE_EQUALITY_FOR_OBJECT_ID`
- `WRITE_CHAR_ARRAYS_AS_JSON_ARRAYS`
- `WRITE_SINGLE_ELEM_ARRAYS_UNWRAPPED`
- `WRITE_EMPTY_JSON_ARRAYS`
- `FAIL_ON_SELF_REFERENCES`
- `FAIL_ON_UNWRAPPED_TYPE_IDENTIFIER`
- `FLUSH_AFTER_WRITE_VALUE`
- `CLOSE_CLOSEABLE`
- `EAGER_SERIALIZER_FETCH`
- `FAIL_ON_ORDER_MAP_BY_INCOMPARABLE_KEY`
- `APPLY_JSON_INCLUDE_FOR_CONTAINERS`
- `WRAP_EXCEPTIONS`

**Removed**: `WRITE_DATES_AS_TIMESTAMPS`, `FAIL_ON_NUMBERS_FOR_ENUMS`, `FAIL_ON_UNKNOWN_PROPERTIES` (some have been consolidated into DeserializationFeature under different names or removed entirely).

**Fix**: Simply remove or rename the property. For date serialization, use `spring.jackson.date-format` or configure a `Jackson2ObjectMapperBuilderCustomizer` bean instead.

### Import Changes

If you directly use Jackson annotations in code:
- `com.fasterxml.jackson.annotation.*` → now `tools.jackson.annotation.*`
- `com.fasterxml.jackson.databind.*` → now `tools.jackson.databind.*`

Spring Boot's auto-configuration handles the switch transparently for `spring.jackson.*` YAML properties (except enum names that changed).

## YAML Placeholder Syntax Gotchas

In Spring Boot's YAML `application.yml`, the placeholder syntax `${VAR:default}` is very sensitive to spaces.

### WRONG (space after colon becomes part of default):
```yaml
spring:
  datasource:
    url: "${DB_URL: jdbc:postgresql://localhost:5432/mydb}"
    # defaults to " jdbc:postgresql://..." (leading space!) — connection fails
```

### RIGHT (no space after colon):
```yaml
spring:
  datasource:
    url: "${DB_URL:jdbc:postgresql://localhost:5432/mydb}"
```

This matters most for DB URLs, passwords, and any config that uses placeholders with defaults.

## Ad-Hoc End-to-End Verification Pattern

When building a Spring Boot backend, a bash-based verification script is more practical than formal unit tests for early-stage validation:

### Pattern
1. Clean DB state (DELETE from tables)
2. Start server in background (java -jar ...)
3. Poll for readiness (curl health/auth endpoint until 200/403)
4. Execute sequential API calls, capturing HTTP status + response body
5. Assert with grep-based checks
6. Print PASS/FAIL summary
7. Kill server, cleanup test data

### Key Techniques
```bash
# Capture only HTTP status code
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/api/endpoint)

# Capture full JSON body
RESPONSE=$(curl -s -X POST http://localhost:8080/api/endpoint \
  -H 'Content-Type: application/json' \
  -d '{"key":"value"}')

# Extract field with python3
TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Assert helper
check() {
  local label="$1" expected="$2" actual="$3"
  if echo "$actual" | grep -q "$expected"; then
    echo "  PASS: $label"
  else
    echo "  FAIL: $label (expected '$expected' in response)"
    echo "        got: $actual"
  fi
}
```

### When to Use
- During initial backend development (before formal test suite)
- To validate integration between layers (Controller — Service — Repository — DB)
- As a quick regression check after changes
- Replace with proper JUnit/Mockito tests once API surface stabilizes

## JwtFilterClass Thread Safety

When extending `OncePerRequestFilter`, the filter bean is a singleton — all requests share the same instance. **Never** store request-specific data (like `userId`) in class-level fields:

### WRONG (race condition):
```java
@Component
public class JwtFilterClass extends OncePerRequestFilter {
  private UUID userId;  // shared across ALL concurrent requests!

  protected void doFilterInternal(...) {
    this.userId = jwtService.extractUserId(token);
    // another request overwrites userId before this one reads it
  }
}
```

### RIGHT (local variables only):
```java
@Component
public class JwtFilterClass extends OncePerRequestFilter {
  private final JwtService jwtService;  // immutable dependency — safe

  protected void doFilterInternal(...) {
    final UUID userId = jwtService.extractUserId(token);  // local — thread-safe
    // use userId within this method only
  }
}
```

## Key Dependencies for SB 4.1.0 Chat App

```xml
<!-- pom.xml key entries -->
<parent>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-parent</artifactId>
  <version>4.1.0</version>
</parent>
<java.version>25</java.version>

<!-- Required starters -->
spring-boot-starter-web
spring-boot-starter-data-jpa
spring-boot-starter-validation
spring-boot-starter-websocket
spring-boot-starter-security
spring-boot-starter-lombok

<!-- Database -->
postgresql (runtime scope)

<!-- JWT (jjwt 0.12.6+) -->
io.jsonwebtoken:jjwt-api:0.12.6
io.jsonwebtoken:jjwt-impl:0.12.6 (runtime)
io.jsonwebtoken:jjwt-jackson:0.12.6 (runtime)
```
