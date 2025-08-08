# Tonight In-Town

Tonight In-Town is a micro-SaaS application that surfaces public events starting within 12 hours of a user's location. It's built with a FastAPI backend and a Next.js frontend.

## Features

- **Find Local Events:** Automatically detects your location and finds events happening near you.
- **Real-time Countdown:** Shows how soon an event is starting.
- **Distance & Pricing:** Displays the distance to the event and the minimum ticket price.
- **Direct Ticket Links:** Provides a direct link to the event's ticket purchasing page.

## Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, PostgreSQL (SQLite for development)
- **Frontend:** Next.js, React, Tailwind CSS, Axios
- **Containerization:** Docker

## API Services

This project is designed to ingest data from various event APIs. Currently, it is integrated with:

- **Ticketmaster Discovery API**

> **Note:** The integration with the **Eventbrite API** is currently a placeholder. During development, I was unable to access their API documentation due to a persistent issue with the development environment's internet access. The service and task placeholders are in the code and can be implemented once the documentation is available.

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js and npm (or yarn)
- Docker (for containerized deployment)
- An API key from [Ticketmaster for Developers](https://developer.ticketmaster.com/)

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

3.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```

4.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up environment variables:**
    Create a `.env` file in the `backend` directory by copying the example:
    ```bash
    cp .env.example .env
    ```
    Add your Ticketmaster API key to the `.env` file:
    ```
    TICKETMASTER_API_KEY="your_ticketmaster_api_key"
    ```
    *Optional: To use PostgreSQL, set the `DATABASE_URL` in the `.env` file.*

6.  **Run the initial data fetching task:**
    This will populate the database with some initial event data.
    ```bash
    python -m tasks
    ```
    *You can set up a cron job to run this script periodically to keep the event data fresh.*

7.  **Run the FastAPI server:**
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install the dependencies:**
    ```bash
    npm install
    # or: yarn install
    ```

3.  **Run the Next.js development server:**
    ```bash
    npm run dev
    # or: yarn dev
    ```
    The frontend application will be available at `http://localhost:3000`.

---

## API Endpoint

### `GET /events/`

Returns a list of events near a specified location.

-   **Query Parameters:**
    -   `lat` (float, required): Latitude of the location.
    -   `lng` (float, required): Longitude of the location.
    -   `radius_km` (int, optional): Search radius in kilometers. Defaults to `10`.

-   **Example Request:**
    ```
    GET http://localhost:8000/events/?lat=34.0522&lng=-118.2437&radius_km=25
    ```

-   **Example Response:**
    ```json
    [
      {
        "name": "Awesome Concert",
        "start_datetime": "2023-10-28T20:00:00Z",
        "end_datetime": "2023-10-28T23:00:00Z",
        "venue_name": "The Grand Venue",
        "lat": "34.052235",
        "lng": "-118.243683",
        "price_min": "25.00",
        "url": "http://ticketmaster.com/event/...",
        "source": "ticketmaster",
        "id": 1,
        "created_at": "2023-10-28T10:00:00Z"
      }
    ]
    ```

---

## Deployment

### Backend (Docker)

The backend is containerized using Docker.

1.  **Build the Docker image:**
    ```bash
    docker build -t tonight-in-town-api .
    ```

2.  **Run the Docker container:**
    Make sure to pass the `.env` file for the environment variables.
    ```bash
    docker run -d -p 8000:8000 --env-file backend/.env --name tonight-in-town-api tonight-in-town-api
    ```
    The API will be accessible on port 8000 of the host machine. This image is ready for deployment on services like Fly.io or Render.

### Frontend

The frontend can be deployed to any platform that supports Next.js, such as Vercel or Netlify. Connect your Git repository to one of these services for continuous deployment.
