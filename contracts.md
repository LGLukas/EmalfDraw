# EmalfDraw API Contracts

## Backend Implementation Plan

### 1. API Endpoints

**Base URL**: `/api/ideas`

#### GET /api/ideas
- **Purpose**: Retrieve all drawing ideas
- **Response**: Array of idea objects
- **Response Format**:
```json
[
  {
    "id": "uuid",
    "text": "Draw a cat wearing a wizard hat",
    "created_at": "2025-01-09T10:30:00Z",
    "user_submitted": false
  }
]
```

#### POST /api/ideas
- **Purpose**: Add new drawing idea
- **Request Body**:
```json
{
  "text": "Draw a robot that makes pancakes"
}
```
- **Response**: Created idea object

#### GET /api/ideas/random
- **Purpose**: Get a random drawing idea
- **Response**: Single idea object

### 2. MongoDB Schema

**Collection**: `drawing_ideas`

```javascript
{
  _id: ObjectId,
  text: String (required, unique),
  created_at: Date (default: now),
  user_submitted: Boolean (default: true)
}
```

### 3. Frontend Integration Changes

#### Remove from mock.js:
- Replace localStorage usage with API calls
- Remove `mockData.defaultIdeas` dependency

#### Update EmalfDraw.jsx:
- Replace `useEffect` localStorage logic with API call to GET /api/ideas
- Replace `getRandomIdea()` with API call to GET /api/ideas/random  
- Replace `addNewIdea()` with API call to POST /api/ideas
- Add loading states for API calls
- Handle API errors with toast notifications

#### API Integration Points:
1. **Initial Load**: Fetch all ideas from GET /api/ideas
2. **Random Challenge**: Use GET /api/ideas/random for refresh button
3. **Add Idea**: POST to /api/ideas when user submits new idea
4. **Error Handling**: Show toast notifications for API failures

### 4. Default Data Seeding
- Seed database with default 20 drawing ideas on startup
- Mark default ideas as `user_submitted: false`
- New user ideas marked as `user_submitted: true`

### 5. Backend Implementation
- FastAPI endpoints with proper error handling
- MongoDB integration using Motor async driver
- Input validation with Pydantic models
- CORS configuration for frontend access