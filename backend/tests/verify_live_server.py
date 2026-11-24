"""Live Server & End-to-End SSE Verification Script."""
import time
import json
import threading
import uvicorn
import httpx
from backend.app.main import app

PORT = 8088

def run_server(server: uvicorn.Server):
    server.run()

def verify_live():
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=run_server, args=(server,), daemon=True)
    server_thread.start()

    # Wait for server to become ready
    base_url = f"http://127.0.0.1:{PORT}"
    ready = False
    for _ in range(20):
        try:
            with httpx.Client(base_url=base_url, timeout=1.0) as probe:
                if probe.get("/").status_code == 200:
                    ready = True
                    break
        except Exception:
            time.sleep(0.2)

    if not ready:
        print("ERROR: Server failed to start within 4 seconds.")
        return

    with httpx.Client(base_url=base_url, timeout=15.0) as client:
        # 1. Health Endpoint
        res_health = client.get("/api/v1/health")
        print(f"HEALTH_STATUS: {res_health.status_code}")
        print(f"HEALTH_BODY: {res_health.json()}")

        # 2. Docs Endpoint
        res_docs = client.get("/docs")
        print(f"DOCS_STATUS: {res_docs.status_code}")

        # 3. Places API
        res_places = client.get("/api/v1/places?limit=3")
        print(f"PLACES_STATUS: {res_places.status_code}")
        print(f"PLACES_COUNT: {len(res_places.json())}")

        # 4. Multi-turn Chat SSE Stream: Turn 1
        session_id = f"live_verify_{int(time.time())}"
        turn1_payload = {
            "session_id": session_id,
            "message": "Hi Hana! I am traveling with my partner. Neither of us have mobility issues."
        }
        print("\n--- INITIATING TURN 1 SSE ---")
        tokens_turn1 = []
        with client.stream("POST", "/api/v1/chat/stream", json=turn1_payload) as response:
            print(f"TURN1_STREAM_STATUS: {response.status_code}")
            print(f"CONTENT_TYPE: {response.headers.get('content-type')}")
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                        if "token" in data:
                            tokens_turn1.append(data["token"])
                        elif "session_id" in data:
                            print(f"TURN1_DONE_PROFILE: {data.get('profile')}")
                    except Exception:
                        pass
        print(f"TURN1_STREAMED_TEXT_LENGTH: {len(''.join(tokens_turn1))}")

        # 5. Multi-turn Chat SSE Stream: Turn 2 (Testing place recommendations)
        print("\n--- INITIATING TURN 2 SSE (Recommendations) ---")
        turn2_payload = {
            "session_id": session_id,
            "message": "Where should we go? We love quiet nature and scenic lake viewpoints."
        }
        tokens_turn2 = []
        places_turn2 = []
        with client.stream("POST", "/api/v1/chat/stream", json=turn2_payload) as response:
            print(f"TURN2_STREAM_STATUS: {response.status_code}")
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                        if "token" in data:
                            tokens_turn2.append(data["token"])
                        elif isinstance(data, list):
                            places_turn2 = data
                    except Exception:
                        pass

        print(f"TURN2_STREAMED_TEXT_LENGTH: {len(''.join(tokens_turn2))}")
        print(f"TURN2_GROUNDED_PLACES_COUNT: {len(places_turn2)}")
        if places_turn2:
            print(f"FIRST_RECOMMENDED_PLACE: {places_turn2[0].get('name_ja')} ({places_turn2[0].get('name_en')})")

        # 6. Verify Session State
        res_session = client.get(f"/api/v1/chat/sessions/{session_id}")
        session_data = res_session.json()
        print(f"\nFINAL_SESSION_MESSAGE_COUNT: {session_data['message_count']}")
        print(f"FINAL_SESSION_ASKED_QUESTIONS: {session_data['asked_questions']}")

    # Clean shutdown
    server.should_exit = True

if __name__ == '__main__':
    verify_live()
