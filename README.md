
# Online Multiplayer Math Game

## Overview

This project is a real-time multiplayer math game built using:

- Python (Sockets)
- PostgreSQL (Database)
- Pygame (GUI)
- Threading (Concurrency)

Players connect to a central server, get paired automatically, and compete to solve math questions faster than their opponent.

---

## Original Project Functionality

Originally, the project included:

- Basic socket-based client-server communication
- Two-player matchmaking
- Simple math question generation
- Win/Loss tracking
- Terminal-based client interface
- Basic database storage for wins and losses

Limitations of the original version:

- No ELO rating system
- No leaderboard
- Client performed answer validation (security issue)
- No atomic rating updates
- No structured protocol separation
- No graphical interface
- Race conditions when players disconnected

---

## Improvements & Enhancements Made

The following major improvements were implemented:

### 1. Secure Server-Side Validation
- Removed client-side answer validation
- Moved all correctness verification to the server
- Prevented arbitrary code execution risks

---

### 2. ELO Rating System
- Implemented dynamic ELO rating calculation
- Added atomic database updates using transactions
- Used row-level locking (`FOR UPDATE`) to prevent race conditions

---

### 3. Leaderboard System
- Added `get_top_players()` database method
- Automatically displays leaderboard at end of game
- Includes rating, wins, and losses

---

### 4. Improved Database Schema
- Added rating column (default 1000)
- Implemented UPSERT logic for wins/losses
- Added safe connection handling
- Integrated environment variable configuration via `.env`

---

### 5. Protocol Layer Refactoring
- Created separate `protocols.py`
- Centralized request/response message types
- Improved maintainability and reduced string duplication

---



### 6. Threading & Concurrency Improvements
- Dedicated thread for each client
- Background receiving thread on client
- Prevented leaderboard interruption after game end
- Fixed disconnect race conditions

---

## Architecture


Server (Game Logic + DB + ELO)
↑
Socket Communication
↓
Client (Networking Layer)
↓
Pygame UI (Presentation Layer)


### Responsibilities

**Server**
- Matchmaking
- Question validation
- Win/Loss updates
- ELO calculation
- Leaderboard generation

**Client**
- Handles socket communication
- Sends answers
- Receives updates

**Pygame UI**
- Renders game interface
- Handles user input
- Displays opponent data and leaderboard

---

## Technologies Used

- Python 3.13
- Socket Programming
- Threading
- PostgreSQL
- psycopg2
- python-dotenv
- Pygame

---

## How To Run

### 1. Install dependencies


pip install psycopg2-binary python-dotenv pygame


### 2. Configure `.env` inside `/server`


DATABASE=your_database_name
USER=your_db_user
PASSWORD=your_password
HOST=localhost
PORT=5432


### 3. Run Server


python server/main.py


### 4. Run Clients


python client/client.py


Run two clients in separate terminals.

---

## Security Improvements

- Removed unsafe `eval()` usage
- Moved validation fully server-side
- Prevented client-side cheating
- Implemented atomic ELO updates

---

## Future Improvements

- AI bot opponent
- Timer-based scoring
- Global leaderboard view screen
- Match history tracking
- Deployment to cloud server

---

## Credits

Original base project concept by:  
Tim Ruscica (Tech with Tim)


Enhancements, refactoring, ELO system, leaderboard, GUI implementation, and architectural improvements by:  
Vaitheeshwar Badrinarayanan

---

## License

This project is for educational purposes.

If redistributing, please retain original author credit.
