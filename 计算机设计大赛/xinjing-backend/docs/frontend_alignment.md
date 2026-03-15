# Frontend <> Backend API Alignment

## 1) Auth (LoginPage)

- Register: `POST /api/v1/auth/register`
- Login: `POST /api/v1/auth/login`

Register payload example:

```json
{
  "username": "demo01",
  "password": "12345678",
  "confirm_password": "12345678",
  "nickname": "演示用户",
  "email": "demo01@example.com",
  "phone": "13800000000",
  "gender": "male",
  "age_range": "18-24"
}
```

Login payload example:

```json
{
  "username": "demo01",
  "password": "12345678"
}
```

## 2) User Profile

- Get profile: `GET /api/v1/users/{user_id}/profile`
- Update profile: `PUT /api/v1/users/{user_id}/profile`

## 3) Screening Flow (ScreeningPage)

- Create session: `POST /api/v1/evaluations/sessions`
- Submit answers: `POST /api/v1/evaluations/sessions/{session_id}/submit`
- Query sessions: `GET /api/v1/evaluations/sessions?user_id=...`
- Query one session: `GET /api/v1/evaluations/sessions/{session_id}`

## 4) Report (ReportPage/Analytics)

- List reports: `GET /api/v1/reports` (returns current login user only)
- Get report by session: `GET /api/v1/reports/by-session/{session_id}`
- Get report detail: `GET /api/v1/reports/{report_id}`
- Get frontend-ready report JSON: `GET /api/v1/reports/{report_id}/frontend`
- Get recommendations: `GET /api/v1/reports/session/{session_id}/recommendations`
- Get emergency alerts: `GET /api/v1/reports/alerts` (returns current login user only)

## 5) Mood Calendar (MoodCalendarPage)

- Upsert day record: `PUT /api/v1/mood-calendar/{YYYY-MM-DD}`
- List records: `GET /api/v1/mood-calendar?month=2026-03` (returns current login user only)
- List all records: `GET /api/v1/mood-calendar` (returns current login user only)
- Get one record: `GET /api/v1/mood-calendar/{YYYY-MM-DD}` (current login user)
- Delete one record: `DELETE /api/v1/mood-calendar/{YYYY-MM-DD}` (current login user)

Mood calendar payload example:

```json
{
  "mood_key": "sunny",
  "diary_text": "今天状态不错",
  "weather_key": "sunny"
}
```

## 6) Emotion Checkins and Trend Snapshots

- Create checkin: `POST /api/v1/mood-calendar/checkins`
- List checkins: `GET /api/v1/mood-calendar/checkins?limit=30` (returns current login user only)
- Upsert trend snapshot: `PUT /api/v1/mood-calendar/trends/{YYYY-MM-DD}`
- List trend snapshots: `GET /api/v1/mood-calendar/trends?limit=90` (returns current login user only)

## 7) Companion Chat (CompanionPage)

- Create session: `POST /api/v1/chat/sessions`
- List sessions: `GET /api/v1/chat/sessions?user_id=1`
- Get one session: `GET /api/v1/chat/sessions/{session_id}`
- Close session: `PATCH /api/v1/chat/sessions/{session_id}/close`
- Send message: `POST /api/v1/chat/sessions/{session_id}/messages`
- List messages: `GET /api/v1/chat/sessions/{session_id}/messages`

Chat session payload example:

```json
{
  "user_id": 1,
  "session_topic": "日常陪伴",
  "evaluation_session_id": null
}
```

Chat message payload example:

```json
{
  "sender_type": "user",
  "content": "我最近压力很大",
  "message_type": "text"
}
```

Compatibility note:

- Message API also accepts `role` (`user`/`assistant`) and will map `assistant` to `agent`.

## 8) Vite Proxy

In frontend `vite.config.js`:

```js
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true
    }
  }
}
```
