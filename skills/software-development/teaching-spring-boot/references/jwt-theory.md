# JWT Teaching Notes — For This Student

## Learning Style Discovered
- **Never used JWT before** — needs full theory before any code
- **Prefers: theory → one method at a time → code themselves**
- **Wants: plain language, analogies, no jargon dumps**
- **Got confused by:** email vs UUID as subject, what `.claim()` does, verification flow

## Theory That Worked (Condensed)

### Analogy: Movie Ticket
- Buy ticket (login) → get paper with: your name, movie, time, theater stamp (signature)
- Show ticket at door (every request) → usher checks stamp matches theater's secret ink
- No central list of ticket holders — the ticket *is* the proof

### Key Distinctions That Clicked
| Confusion | Resolution |
|-----------|------------|
| "Use email as subject" | Subject = immutable ID (UUID). Email can change. |
| "Client sends signature only" | Client sends full token (header.payload.signature). Server parses all 3 parts. |
| "We recompute HMAC manually" | `Jwts.parser().verifyWith(key).parseSignedClaims(token)` does it all in one call. |
| "What does .claim() do?" | Custom key-value in payload. Like `Map.put("userName", "fugleman")`. |

### Verification Flow (What Actually Happens)
```java
// One call does everything:
Jwts.parser()
  .verifyWith(secretKey)
  .build()
  .parseSignedClaims(token);
// If returns → valid (signature OK + not expired)
// If throws JwtException → invalid
```

## Teaching Sequence That Worked
1. **Concept probe:** "What do you think JWT does?" → revealed "HMAC with email + secret"
2. **Analogy first:** Movie ticket / passport stamp
3. **Decoded JWT visual:** Showed header.payload.signature structure
4. **Claims table:** Standard vs custom, why UUID not email
5. **Crypto intuition:** Signature binds header+payload, only secret holder can forge
6. **Verification = one library call:** Not manual split/recompute
7. **Code one method at a time:** init → generateToken → extractUserId → extractUserName → isTokenValid

## Method Signatures (For Reference)
```java
// init() — runs once at startup
@PostConstruct
public void init() {
  byte[] keyBytes = Decoders.BASE64.decode(secretString);
  this.secretKey = Keys.hmacShaKeyFor(keyBytes);
}

// generateToken — called at login
public String generateToken(UUID userId, String userName)

// extractUserId — called by filter on every request
public UUID extractUserId(String token)

// extractUserName — optional, for UI display
public String extractUserName(String token)

// isTokenValid — called by filter on every request
public boolean isTokenValid(String token)
```

## Common Student Pitfalls to Watch
- Using email as `sub` → explain immutability
- Forgetting `.claim("userName", userName)` → client can't display name without extra call
- Trying to manually verify HMAC → point to `parseSignedClaims()`
- Not catching `JwtException` in `isTokenValid` → crashes on bad token instead of returning false
- **Student gets confused when you spec all JWT files at once** — they said "I'm getting confused with JWT, let's leave it for now". Lesson: teach JWT one file at a time, defer if overwhelmed.

## JWT Implementation Flow (After Theory)
Student chose to defer JWT implementation and do services/controllers first. When resuming, the order is:
1. **UserDetailsServiceImpl** — loadUserByUsername(email) + loadUserById(UUID). Uses UserRepository. Maps to Spring Security `UserDetails` builder.
2. **JwtAuthenticationFilter** — extends `OncePerRequestFilter`. Extracts `Authorization: Bearer *** calls `jwtService.getUserId(token)`, loads `UserDetails` via `loadUserById`, builds `UsernamePasswordAuthenticationToken`, sets `SecurityContextHolder`. Silent failure on bad token.
3. **SecurityConfig** — `@Configuration`. CSRF disabled, stateless session, permit `/auth/**` + `/ws/**`, add `JwtAuthenticationFilter` before `UsernamePasswordAuthenticationFilter`. Expose `AuthenticationManager` and `PasswordEncoder` beans.
4. **UserServiceImpl** — register (check duplicate email, hash password, save, generate JWT), login (authenticate via AuthenticationManager, set online, generate JWT).
5. **UserController** — POST `/auth/register`, POST `/auth/login`. Both return `AuthResponse`.

**Key rule**: Provide code as copyable blocks in chat, NEVER as `write_file` operations. The student copies to their editor.