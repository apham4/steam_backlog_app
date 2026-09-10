
# Backlog Game Rec



A full-stack recommendation engine that analyzes a user's Steam library to surface their unplayed backlog games matching their recent gameplay habits. This app was built with FastAPI, PostgreSQL, React, and Redux Toolkit, and deployed on Render (backend) and Vercel (frontend).

Since the app is hosted using Render and Vercel's free tier, it may take \~ 1 minute for the backend and frontend to spin up (individually).
* **Live Demo:** [https://backlog-game-rec.vercel.app/](https://backlog-game-rec.vercel.app/)
* **Backend API Documentation (Swagger):** [https://backlog-game-rec-api.onrender.com/docs](https://backlog-game-rec-api.onrender.com/docs)





## I - Tech Stack

#### Backend

 - Python 3, FastAPI, SQLAlchemy ORM, Pydantic, HTTPx, PyJWT, Alembic,
   hosted on Render.

#### Frontend

 - TypeScript, Vite, React, Redux Toolkit, Tailwind CSS, Axios, hosted
   on Vercel.

#### Database

 - PostgreSQL, hosted on Neon.tech.

#### External APIs

 - Steam Web API (IPlayerService, ISteamUser), Steam Storefront API,
   Steam OpenID 2.0.

## II - API Overview

|**Method**|**Endpoint**|**Description**|**Auth Required**|
|-|-|-|-|
|`GET`|`/api/auth/login`|Redirects client to Steam OpenID 2.0 login portal.|No|
|`GET`|`/api/auth/callback`|Validates OpenID signature and issues JWT.|No|
|`GET`|`/api/me`|Returns the profile and settings of the currently authenticated user.|Yes (Bearer)|
|`PUT`|`/api/settings`|Updates the user preferences of the currently authenticated user (backlog/recent playetime thresholds).|Yes (Bearer)|
|`GET`|`/api/recommendation/get`|Analyzes the authenticated user's Steam library data and returns a top-scored backlog game based on their set preferences.|Yes (Bearer)|
|`POST`|`/api/exclusions`|Excludes a game from recommendations for a set duration for the authenticated user.|Yes (Bearer)|
|`DELETE`|`/api/exclusions`|Purges all active exclusions for the authenticated user.|Yes (Bearer)|
|`GET`|`/api/steam/library`|Retrieves the authenticated user's owned games categorized into backlog and recently played.|Yes (Bearer)|
|`GET`|`/api/health`|General health check route for the service.|No|





## III - Highlights

#### 1. Stateless OpenID 2.0 Authentication
Backlog Game Rec integrates Steam's OpenID 2.0 assertion flow to authenticate and get the user's game library data. The backend constructs the authentication request, verifies the cryptographic signature with Valve's endpoints via HTTP callbacks, and extracts the verified 64-bit Steam ID. The verified Steam identity is then converted into a JSON Web Token (JWT) containing user claims and expiration timestamps, and sent to the client. The client then uses the Axios request interceptor to inject the bearer token into outgoing requests without manual token passing.

#### 2. Steam API Throttling Mitigation
Steam Storefront API notoriously has strict rate limits (~200 requests/5 minutes). The server stores game metadata (genres, categories, developers, review metrics, etc.) in PostgreSQL with configurable time-to-live (TTL) expiration. Upon recommendation request, the app queries its database for fresh cache hits. Cache misses are sampled up to a count limit before executing concurrent asynchronous httpx fetch from Steam Storefront API.

#### 3. Game Scoring Mechanic
The server analyzes the user's gameplay duration over the prior two weeks, mapping genre playtime distribution into normalized scalar weights. Backlog games are then scored by their genre tags multiplied by these weights. The score is further refined by taking into account its user review score from the Steam Storefront API. The recommendation engine also supports exclusions that temporarily exclude games from being recommended for a user-customizable period. These exclusions are automatically cleaned up based on their expiration time upon recommendation request.

Future improvements to the recommendation engine may take into account playtime on different devices (Windows, MacOS, Steam Deck) and weigh games based on their support status on such platforms.


## IV - Local Development Setup



#### Prerequisites

 - Python 3.13.4 or later
 - Node.js 22.16.0 or later
 - PostgreSQL Database: Local instance or a hosted serverless instance
   with URL.
 - Steam Web API Key (available from the [Steam Community Developer
   Portal](https://steamcommunity.com/dev/apikey)).


#### Backend Setup

1. Navigate to the server directory.
`cd server`
2. Create and activate a virtual environment.
`python -m venv .venv`
`.venv\Scripts\activate`
3. Install dependencies.
`pip install -r requirements.txt`
4. Create a `.env` file in the directory matching the template in `.env.example`.
5. Start the development server instance.
`uvicorn app.main:app --reload --port 8000`
6. The server app will be available at `http://localhost:8000` with interactive Swagger docs at `http://localhost:8000/docs`.


#### Frontend Setup
1. Navigate to the server directory.
`cd server`
2. Install dependencies
`npm install`
3. Create a `.env.local` file in the directory matching the template in `.env.example`.
4. Start the development client instance.
`npm run dev`
5. The React SPA will be available at `http://localhost:5173/` by default.

