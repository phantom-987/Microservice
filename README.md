~~~  User Service ~~~
A production-style FastAPI microservice for user management built to practice ""core backend patterns: REST APIs, async DB access, caching, and stateless auth, all containerized""

Features
- User CRUD (create, read, update, delete)
- JWT-based authentication (stateless, bearer tokens)
- PostgreSQL for persistent storage (async SQLAlchemy + Alembic migrations)
- Redis caching (cache-aside pattern on user lookups, with invalidation on update/delete)
- Fully Dockerized (app + Postgres + Redis via Docker Compose)
- Input validation via Pydantic, password hashing via bcrypt


///Running Locally///
```bash
docker compose -f docker/docker-compose.yml up -d --build
docker compose -f docker/docker-compose.yml exec app alembic upgrade head
```
API available at `http://localhost:8000`, interactive docs at `/docs`.

API Overview:

Register a user — POST /api/v1/users/ — open to anyone, no login needed. "For Creating New Account"
Log in — POST /api/v1/auth/login — send email + password, get back a JWT token. This token verifies who you are on later requests.
List all users — GET /api/v1/users/ — requires a valid token. Only logged-in users can see the full list.
Get one user by ID — GET /api/v1/users/{id} — open, no login needed. Also the one route backed by Redis caching, so repeated lookups are fast.
Update a user — PUT /api/v1/users/{id} — requires a valid token. Changes a user's details.
Delete a user — DELETE /api/v1/users/{id} — requires a valid token. Removes a user.
Health check — GET /health — open, no login.

check it out : http://127.0.0.1:8000/docs# 
