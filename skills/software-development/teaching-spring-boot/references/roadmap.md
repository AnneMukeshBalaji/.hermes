# Chat Application — Teaching Roadmap

## Phase 1: Core Concepts (Theory)
- [x] What is Spring Boot? (Convention over Configuration)
- [x] IoC Container & Dependency Injection
- [x] Layered Architecture (Controller → Service → Repository → DB)
- [x] Entity vs DTO — separation of DB and client contracts
- [x] Hibernate / ORM / JPA — how Java objects map to SQL rows
- [x] WebSocket — full-duplex, handshake (Upgrade → 101 → persistent)
- [x] JWT — stateless auth, movie-ticket analogy, short-expiry defense
- [x] Token Storage — localStorage vs sessionStorage vs HTTP-only cookie

## Phase 2: Building the Backend (Complete)
- [x] Project scaffold (Spring Boot 4.1.0, Java 25)
- [x] Dependencies: webmvc, data-jpa, postgresql, websocket, security, lombok, jjwt
- [x] entity/User.java -- UUID PK, userName, hashedPassword, online, email, timestamps
- [x] entity/MessageStatus.java -- PENDING, DELIVERED, READ
- [x] entity/Message.java -- content (TEXT), sender/recipient (ManyToOne), status
- [x] Repositories -- UserRepository (findByEmail, findByUserName), MessageRepository (@Query findConversation)
- [x] DTOs -- RegisterRequest, LoginRequest, AuthResponse, UserResponse, SendMessageRequest, MessageResponse, ChangePasswordRequest
- [x] JwtService -- init(), generateToken(UUID), extractUserId(token), validateToken(token)
- [x] JwtFilterClass -- OncePerRequestFilter, Bearer extraction, SecurityContextHolder (thread-safe, local vars)
- [x] SecurityConfig -- CORS localhost:5173, CSRF disabled, stateless, permit /api/auth/** + /ws/**, BCrypt
- [x] AuthService -- register (duplicate check, hash, save, token), login (verify, token), logout (offline)
- [x] UserService -- getAllUsers, getUserById, updateProfile, changePassword
- [x] MessageService -- sendMessage, getConversation, updateStatus
- [x] AuthController -- POST /api/auth/register, POST /api/auth/login, POST /api/auth/logout
- [x] UserController -- GET /api/users, GET /api/users/{id}, PUT /api/users/profile, PUT /api/users/password
- [x] MessageController -- POST /api/messages/send, GET /api/messages/{userId}, PUT /api/messages/{id}/status
- [x] WebSocketConfig -- STOMP over SockJS on /ws, /topic + /queue broker, /app prefix, /user dest
- [x] WebSocketController -- @MessageMapping /chat.send and /chat.typing via SimpMessagingTemplate

## Phase 3: Connect and Test (Verified)
- [x] Run the app, verify DB tables created (users, messages)
- [x] Test REST endpoints with curl -- 13/13 end-to-end tests passing
- [x] Test: register, duplicate rejection, login, users list, auth guard, send message, conversation, profile update, password change, logout
- [x] WebSocket STOMP endpoint registered at /ws with SockJS fallback

## Dev Environment Notes
- Neovim + jdtls (Mason) — Lombok agent required: `--jvm-arg=-javaagent:~/.local/share/nvim/mason/share/jdtls/lombok.jar` in jdtls cmd config
