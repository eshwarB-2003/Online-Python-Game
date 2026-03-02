class Room:
    def __init__(self, client1, client2):
        self.questions, self.answers = self.generate_questions()
        self.indexs = {client1: 0, client2: 0}
        self.finished = False
    
    def generate_questions(self):
        return ["1 + 1", "2 + 2", "3 + 3"], [2, 4, 6]
    
    def verify_answer(self, client, attempt):
        if self.finished:
            return False
        if client not in self.indexs:
            return False
        
        index = self.indexs[client]
        if index >= len(self.questions):
            return False
        answer = self.answers[index]
        try:
            attempt = int(attempt)
        except:
            return False
        correct = answer == int(attempt) # reason for adding this int type is if user sends 2 as it store as string it should convert it into 2 and gives 

        if correct:
            self.indexs[client] += 1
        
        return correct
