# Backlog Game Rec



A full-stack recommendation engine that analyzes a user's Steam library to surface their unplayed backlog games matching their recent gameplay habits. This app was built with FastAPI, PostgreSQL, React, and Redux Toolkit, and deployed on Render (backend) and Vercel (frontend).



Since the app is hosted using Render and Vercel's free tier, it may take \~ 1 minute for the backend and frontend to spin up (individually).



* **Live Demo:** [https://backlog-game-rec.vercel.app/](https://backlog-game-rec.vercel.app/)
* **Backend API Documentation (Swagger):** [https://backlog-game-rec-api.onrender.com/docs](https://backlog-game-rec-api.onrender.com/docs)





### I - Tech Stack



##### Backend

Python 3, FastAPI, SQLAlchemy ORM, Pydantic, HTTPx, PyJWT, Alembic, hosted on Render.

##### 

##### Frontend

TypeScript, Vite, React, Redux Toolkit, Tailwind CSS, Axios, hosted on Vercel.



##### Database

PostgreSQL, hosted on Neon.tech.



##### External APIs

Steam Web API (IPlayerService, ISteamUser), Steam Storefront API, Steam OpenID 2.0.





### II - API Overview



|**Method**|**Endpoint**|**Description**|**Auth Required**|
|-|-|-|-|
|GET|/api/auth/login|Redirects client to Steam OpenID 2.0 login portal.|No|
|GET|/api/auth/callback|Validates OpenID signature and issues JWT.|No|
|GET|/api/me|Returns the profile and settings of the currently authenticated user.|Yes (Bearer)|
|PUT|/api/settings|Updates the user preferences of the currently authenticated user (backlog/recent playetime thresholds).|Yes (Bearer)|
|GET|/api/recommendation/get|Analyzes the authenticated user's Steam library data and returns a top-scored backlog game based on their set preferences.|Yes (Bearer)|
|POST|/api/exclusions|Excludes a game from recommendations for a set duration for the authenticated user.|Yes (Bearer)|
|DELETE|/api/exclusions|Purges all active exclusions for the authenticated user.|Yes (Bearer)|
|GET|/api/steam/library|Retrieves the authenticated user's owned games categorized into backlog and recently played.|Yes (Bearer)|
|GET|/api/health|General health check route for the service.|No|





### III - Highlights



asdf





### IV - Local Development Setup



Prerequisites

Python 3.13.4 or later

Node.js 22.16.0 or later

PostgreSQL Database: Local instance or a hosted serverless instance with URL.



Backend Setup



Frontend Setup

