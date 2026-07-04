# Jackson Annotations — Student Reference

## `@JsonAlias`

- **Deserialization only** — tells Jackson to accept alternative field names when reading JSON into Java
- Does NOT affect serialization (Java -> JSON always uses the Java field name or `@JsonProperty`)
- Example: `@JsonAlias("user_name")` on field `userName` means both `{"userName":...}` and `{"user_name":...}` are accepted on input, but output always uses `userName`
- **Useless on Response DTOs** — response DTOs are only serialized (Java -> JSON), never deserialized, so `@JsonAlias` is dead code there

## `@JsonProperty`

- Controls the JSON field name for **both** serialization and deserialization
- Use when you want the API contract to differ from the Java field name (e.g., Java field `userName` but JSON field `user_name`)

## Decision Table

| Annotation | Affects Input? | Affects Output? | Use Case |
|---|---|---|---|
| `@JsonAlias` | Yes | No | Accept legacy snake_case but respond in camelCase |
| `@JsonProperty` | Yes | Yes | Full rename — both input and output |
| Neither | Uses field name | Uses field name | Standard case — prefer this unless you need compatibility |

## When to Use Which

- **Request DTOs** — `@JsonAlias` if you want backward compatibility for clients sending snake_case
- **Response DTOs** — neither, unless you want snake_case in responses (then use `@JsonProperty`)
- **When designing from scratch** with consistent camelCase — use neither, keep it clean
