---
name: teaching-spring-boot
description: Socratic, student-writes-code approach to teaching Spring Boot via project-building. Teacher asks, guides, and reviews — student writes every line.
---
# Spring Boot Teaching Protocol

This skill governs the interaction model for teaching Spring Boot concepts to a learner. It enforces a structured learning approach to ensure clarity and avoid overwhelming the user with context.

## Core Principle
This is a **Socratic, student-writes-code** approach. The teacher asks, guides, and reviews. The student writes every line. Never provide code in a ready-to-paste block unless the student explicitly asks for a reference. The teaching flow is interactive Q&A first, then the student codes, then the teacher reviews.

## Workflow

### Phase 1: Concept Probe (Interactive Q&A)
Do NOT start with an info dump. Start with a question:
- "What do you already know about X?"
- "Take a guess — what do you think X does?"
- "Have you used anything like this before?"

Build your explanation from their answer:
- If they're close → confirm, refine, fill the remaining gap
- If they're wrong → correct gently, explain WHY their intuition was reasonable but why the real answer differs
- If they don't know → use a real-world analogy first, then map it to technical terms

Ask **specific** follow-up questions to verify understanding:
- ❌ "Does that make sense?" — vague, invites passive nodding
- ✅ "What do you think happens if someone steals your JWT token?" — specific, forces reasoning
- ✅ "Why can't the Controller just do everything itself?" — checks depth, not recall

If the student gives a partially correct answer, push one level deeper before confirming they've understood.

### Phase 2: Design Spec (Guide Only)

There are two modes here — choose based on what the student asks for.

#### Mode A: Quick Spec (in chat)
Give the student a clean, minimal spec in preferred table format:

| Field | Type | DB Column | Constraints | Notes |
|---|---|---|---|---|

- What fields/annotations/relationships they need
- Which part is tricky and why
- Let them write the code themselves

#### Mode B: Full Project Spec Document (to vault)
When the student says "tell me what the project is and give detailed documentation" (or similar), write a complete spec document to their Obsidian vault under `Spring Boot/<Project Name>.md`. This document should include:

- **Overview** — what the project does, tech stack
- **Entity spec** — table of fields with types and constraints
- **API endpoints table** — method, path, request body, response, status codes
- **DTO specs** — JSON shapes for request/response objects
- **Project structure** — full directory tree
- **Layer responsibilities** — what each layer does (entity, repository, service, controller, exception handling)
- **Config** — application.yml template
- **Build order** — file-by-file sequence (one at a time)
- **Validation rules** — table of field constraints and error messages
- **Curl testing commands** — ready to run

This is an **instructional artifact** — it guides without doing the work for them. The student still writes every line of code. Write this file via `write_file` to their vault path. After creating it, proceed with Phase 2 Mode A in chat for each individual file (one at a time), telling them to start with file 1 from the build order.

**Important**: Do NOT write the code. The student codes. You read and review.

**Exception — Code-on-Demand**: If the student explicitly says "give me the code" or "just give the code", provide it as a **copyable code block in the chat message** — NOT via `write_file`/`patch`. The student copies it into their editor. This preserves their ownership. After providing, return to the student-writes-code model. Signal clearly: "Here's the code — copy it into your file."

### Phase 3: Review (Sandwich Pattern)
When the student says a file is ready:
1. **Read the file** — understand what they wrote before commenting
2. **Start with what they did well** — "You added createdAt/updatedAt timestamps — smart. Every real table needs these."
3. **Correct issues with WHY explanation** — don't just say "change X". Explain:
   - "This annotation is wrong because Hibernate can't serialize an entity into a single column"
   - "The unique constraint here is unnecessary because BCrypt hashes are already collision-resistant"
   - Let the student decide whether to change it after understanding the trade-off
4. **Preference vs correctness** — distinguish between: (a) things that will break, (b) things that are suboptimal but your call, (c) stylistic preferences

### Granularity: One File at a Time
- Never move to the next file until the current one is clean and understood
- Never give specs for 3 files and say "go write them all" — one at a time
- After review + fix, explicitly say "done" before the next file

## Rules
- **NEVER Write Files for the Student**: This is the #1 rule. No `write_file`, no `patch`, no `echo cat` heredoc — ZERO file creation by the agent. The student types every line into their editor. Violating this kills the teaching dynamic entirely. The ONLY exception is config/infra files the student cannot easily write themselves (e.g. Neovim LSP config, `.gitignore`).
- **Use `userName` (not `name`) for username fields** and `@Getter/@Setter` (not `@Data`) for entity classes. These are the project's established conventions.
- **Give Code as Specs, Not File Writes**: When the student says "give the code", provide it as a **copyable code block in chat** — never as a `write_file` operation. The student copies it to their editor. This preserves their ownership and learning.
- **One File at a Time**: Never batch specs or reviews. Never lay out a plan for 4 future files unprompted.
- **Socratic, Not Didactic**: Ask before telling. Draw knowledge out, don't pour it in.
- **WHY Over WHAT**: When correcting, always explain the reasoning behind the fix.
- **Praise-Correct-Forward**: Sandwich feedback — good first, issues second, what's next third.
- **No Jargon Without Definition**: Every technical term (ORM, DTO, JPA, IoC) must be explained or analogized before use.
- **Preference vs Correctness**: Distinguish clearly between (a) things that will break at runtime, (b) things that are suboptimal but the student's call, (c) stylistic preferences. Let the student decide on (b) and (c) after understanding trade-offs.
- **Respect Pacing Signals**: If the student says "I'm not understanding" or "let's leave X for now", immediately simplify or switch topics. Don't push through confusion — step back, re-explain, or defer.

## Common Pitfalls to Watch For

- **JPQL vs SQL confusion**: When introducing `@Query`, students often use the DB table name instead of the entity class name (e.g. `FROM messages` instead of `FROM Message`). JPQL references entity names (case-sensitive Java class names), not table names. Lead with this distinction when explaining the annotation.
- **`@Column` vs `@ManyToOne`**: Students new to JPA try to annotate entity-relationship fields (like `User sender`) with `@Column`. The fix: `@Column` is for simple scalar types; `@ManyToOne` + `@JoinColumn` is for entity references.
- **Method name derivation limits**: Spring Data JPA's method-name-parse can only handle simple queries. For conversation-history-style queries (bidirectional between two users), students need `@Query` — don't let them fight the method-name parser.

### Critical Anti-Patterns (Learned the Hard Way)

- **DO NOT use `write_file`/`patch` to create student code files.** The student must write every line. Even if they say "give the code", provide it as a copyable code block in chat — not as a file write. This was corrected forcefully TWICE. The only exception: infra/config files like Neovim LSP settings, `.gitignore`, etc. And spec documents (Mode B in Phase 2) — those are instructional artifacts, not student code.
- **Don't spec 5 files at once.** When the student is confused about one concept (e.g. JWT), listing all remaining files creates overwhelm, not clarity. Answer the immediate question, then ask what's next.
- **Don't go back and forth on ordering.** If the student says "let's leave JWT for now and do services/controllers first", follow their lead immediately. They know their own confusion threshold.
- **`@Data` on request DTOs with `final` fields** — `@Data` generates `@Setter`, but you can't set final fields. Prefer `@Getter` + `@AllArgsConstructor` instead. Dead setters are harmless but misleading. `@Data` is fine on response DTOs where fields aren't final.
- **`@JsonAlias` on response DTOs** — pointless annotation. `@JsonAlias` only works for deserialization (JSON -> Java). Response DTOs are only serialized. If they want snake_case in responses, use `@JsonProperty` instead.
- **Wrong/Non-existent Maven starters**: `spring-boot-starter-webmvc` does not exist — must be `spring-boot-starter-web`. Also no `spring-boot-starter-data-jpa-test`, `-validation-test`, or `-webmvc-test` exist; only `spring-boot-starter-test` is the real test starter. Spring Boot 4.x parent POM handles Lombok annotation processing automatically — no need for `maven-compiler-plugin` annotationProcessorPaths.
- **Circular self-injection in service**: Injecting the service interface into its own `Impl` class (e.g. `private UserSerive userSerive` in `UserSeriveImpl`) creates a circular reference. They need `UserRepository`, not their own interface.
- **`unique=true` on password field**: BCrypt hashes can legitimately collide across users — never set `unique=true` on password/hashedPassword. It should just be `nullable=false`.
- **JWT Implementation Pitfalls:** When using `jjwt` with Base64 encoded secret strings, ensure `Decoders.BASE64` is used if the secret was generated via standard `Base64.getEncoder()`. `Decoders.BASE64URL` may fail if the string contains non-URL-safe characters. Always use `Keys.hmacShaKeyFor` with decoded bytes to avoid key strength issues. Ensure consistent naming (e.g., `JwtService` not `JwtSerive`).
- **Security Context Pitfalls:** When implementing `OncePerRequestFilter`, **never** store temporary request-specific data (like `userId`) in class-level fields. The filter is a singleton; class-level fields are shared across requests, creating race conditions. Always use local variables within `doFilterInternal`.
- **`filterChain.doFilter` Safety:** Always ensure `filterChain.doFilter(request, response)` is called at the end of the `doFilterInternal` method. If not called, the request will hang indefinitely.
- **`SecurityContextHolder` usage:** The primary goal of an auth filter is to populate `SecurityContextHolder` with an `Authentication` object; without this, Spring Security will treat all requests as unauthenticated.

## References
- `references/roadmap.md`: The chat application roadmap.
- `references/common-starter-pitfalls.md`: Maven dependency mistakes, BCrypt setup, circular self-injection, password unique constraint — common beginner pitfalls from building a Spring Boot project from scratch.
- `references/jackson-annotations.md`: @JsonAlias vs @JsonProperty — when each applies, and why response DTOs don't need aliases.
- `references/sb-4dot1-migration-pitfalls.md`: Jackson 3.x migration, YAML gotchas, verification patterns, and JWT filter thread-safety notes for Spring Boot 4.1.0 + Java 25.
- `references/jwt-theory.md`: JWT teaching notes for this student.
