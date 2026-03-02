import socket
import threading
import json
from protocols import Protocols


class Client:
    def __init__(self, host="127.0.0.1", port=55555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

        self.closed = False
        self.started = False
        self.questions = []
        self.current_question_index = 0
        self.opponent_question_index = 0
        self.opponent_data = None
        self.winner = None

    def start(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
    def play_game(self):
        while not self.closed and self.current_question_index < len(self.questions):
            question = self.get_current_question()
            print(f"\nQuestion: {question}")
            attempt = input("Your answer: ")
            if self.closed:
                return
            try:
                attempt = int(attempt)
            except:
             print("Invalid input. Enter a number.")
             continue

            self.send(Protocols.Request.ANSWER, attempt)
            return  # wait for server response

    def send(self, request, message):
        data = {"type": request, "data": message}
        self.server.send(json.dumps(data).encode("ascii"))

    def receive(self):
        while not self.closed:
            try:
                data = self.server.recv(1024).decode("ascii")
                message = json.loads(data)
                self.handle_response(message)
            except:
                break
        
        self.close()

    def close(self):
        self.closed = True
        self.server.close()
    # Client should never calculate correctness
    # def client_validate_answer(self, attempt):
    #  question = self.get_current_question()
    # answer = eval(question)
    # if answer == int(attempt):
    # self.current_question_index += 1

    def handle_response(self, response):
        r_type = response.get("type")
        data = response.get("data")
        if r_type == Protocols.Response.NICKNAME:
            user_input = input("Enter your nickname: ")
            self.nickname = user_input
            self.send(Protocols.Request.NICKNAME, user_input)
        elif r_type == Protocols.Response.QUESTIONS:
            self.questions = data
        elif r_type == Protocols.Response.OPPONENT:
            self.opponent_data = data
            print(f"Opponent: {data['name']}")
            print(f"Wins: {data['wins']}, Losses: {data['losses']}")
            print(f"Rating: {data.get('rating', 1000)}")
        elif r_type == Protocols.Response.OPPONENT_ADVANCE:
            self.opponent_question_index += 1
        elif r_type == Protocols.Response.START:
            self.started = True
            threading.Thread(target=self.play_game).start()
        elif r_type == Protocols.Response.ANSWER_VALID:
            print("Correct!")
            self.current_question_index += 1
            threading.Thread(target=self.play_game).start()
        elif r_type == Protocols.Response.ANSWER_INVALID:
            print("Wrong answer. Try again.")
            threading.Thread(target=self.play_game).start()
        elif r_type == Protocols.Response.WINNER:
            self.closed = True
            print("\nGame Over!")
            print(f"Winner: {data['winner']}")
            print("\n=== Leaderboard ===")
            for i, player in enumerate(data["leaderboard"], 1):
                line = f"{i}. {player['username']} | Rating: {player['rating']} | Wins: {player['wins']} | Losses: {player['losses']}"
                if player['username'] == self.nickname:
                    line += "  <-- YOU"
                print(line)
            self.server.close()

    def get_current_question(self):
        if self.current_question_index >= len(self.questions):
            return ""
        return self.questions[self.current_question_index]
if __name__ == "__main__":
    client = Client()
    client.start()