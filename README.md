# BetterDays Mobile MVP

A mobile-first BetterDays starter for **Android + iOS** built with Expo / React Native / TypeScript and a FastAPI + PostgreSQL backend. The existing Next.js project is not modified.

## Included
- Expo Router tabs: Home, Recipes, Community, Progress, Profile
- Recipe list/detail/create form and share action
- Habit check-ins and water tracker
- Community feed with cheers
- Challenges join/leave
- Profile/settings basics
- FastAPI endpoints for health, auth, recipes, habits, water, community, challenges, profile
- PostgreSQL via SQLAlchemy; JWT access tokens; password hashing
- Docker Compose for local PostgreSQL + API
- API client with bearer token support

## Quick start

### 1. Backend
Install Docker Desktop, then from this folder:
```bash
docker compose up --build
```
API docs: http://localhost:8000/docs

The API container runs migrations-on-start by creating tables via SQLAlchemy. For production, replace this with Alembic migrations and managed secrets.

### 2. Mobile app
Install Node.js LTS and Expo Go on your phone. In a second terminal:
```bash
cd mobile
cp .env.example .env
npm install
npx expo start
```
Set `EXPO_PUBLIC_API_URL` in `mobile/.env` to a URL reachable from the device:
- iOS simulator: `http://localhost:8000`
- Android emulator: `http://10.0.2.2:8000`
- Physical phone: `http://YOUR_COMPUTER_LAN_IP:8000`

Scan the QR code with Expo Go. For a physical phone, phone and computer must be on the same Wi-Fi and your firewall must allow port 8000.

### 3. Create account
Use the mobile app's Profile tab to register / sign in. Alternatively use `/docs`.

## Important MVP limitations
- This is a starter scaffold and has not been run through iOS/Android native builds in this environment.
- No store signing, push notifications, payments, food database, image upload service, email verification, password reset, rate limiting, or production moderation yet.
- Recipe image URLs are optional demo placeholders.
- JWTs are stored in AsyncStorage for prototype simplicity. Before production, use `expo-secure-store`, short-lived access tokens, refresh-token rotation, and secure logout.
- Community posts and challenges are seeded demo content; real user-generated posts need reporting, blocking, moderation, pagination, and abuse prevention.
- Wellness data is user data: add a privacy policy, export/delete workflows, consent and retention rules before launch.
