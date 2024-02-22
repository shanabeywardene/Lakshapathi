import tkinter as tk
from tkinter import messagebox
from tkinter import *
from PIL import Image, ImageTk
import random
import csv
import pygame
import os

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Application")
        
        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set the app window size to fit the screen
        self.root.geometry(f"{screen_width}x{screen_height}")

        # Load the background image
        bg_image = Image.open(os.path.join("images", "question_background_1080.jpg"))
        bg_photo = ImageTk.PhotoImage(bg_image)

        self.bg_label = tk.Label(root, image=bg_photo)
        self.bg_label.image = bg_photo
        self.bg_label.place(relwidth=1, relheight=1)


        self.questions = []
        self.current_question = 0
        self.score = 0
        self.delay = 6000  # 6-second delay in milliseconds before the next question
        self.restart_delay = 4000  # 4-second delay before restarting the game
        self.current_level = 1

        self.load_questions_from_csv("quiz_questions.csv")

        self.level_amounts = {
            1: "Rs. 2,000",
            2: "Rs. 4,000",
            3: "Rs. 8,000",
            4: "Rs. 10,000",
            5: "Rs. 20,000",
            6: "Rs. 30,000",
            7: "Rs. 50,000",
            8: "Rs. 70,000",
            9: "Rs. 100,000",
            10: "Rs. 200,000",
            11: "Rs. 300,000",
            12: "Rs. 500,000",
            13: "Rs. 1,000,000",
            14: "Rs. 2,000,000",
            15: "Rs. 3,000,000"
        }

        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

        self.level_label = tk.Label(root, text="", font=("Helvetica", 12))
        self.level_label.pack(pady=10)


        self.question_label = tk.Label(root, text="", font=("Helvetica", 18, "bold"), wraplength=1350)
        self.question_label.place(x=962, y=720, anchor="center")

        self.choice_buttons = []
        button_coords = [
            (329, 830),  # answer0
            (1107, 830),  # answer1
            (329, 915),  # answer2
            (1107, 915),  # answer3
        ]

        button_width = 600
        button_height = 75

        for i in range(4):
            button = tk.Button(root, text="", font=("Helvetica", 18, "bold"), command=lambda i=i, width=button_width, height=button_height: self.check_answer(i))
            self.choice_buttons.append(button)
            button.place(x=button_coords[i][0], y=button_coords[i][1], anchor="nw")

        # Bring labels and buttons to the front
        self.level_label.lift()
        self.question_label.lift()
        for button in self.choice_buttons:
            button.lift()

        self.next_question()

    def load_questions_from_csv(self, filename):
        with open(filename, mode='r', encoding='utf8') as file:
            reader = csv.reader(file)
            for row in reader:
                question = row[0]
                choices = row[1:5]
                correct_answer = int(row[5])
                level = int(row[6])
                self.questions.append({
                    "question": question,
                    "choices": choices,
                    "correct_answer": correct_answer,
                    "level": level
                })

    def next_question(self):
        next_questions = [question_data for question_data in self.questions if question_data["level"] == self.current_level]
        if next_questions:
            next_question = random.choice(next_questions)
            self.current_correct_answer = next_question["correct_answer"]
            level_text = self.level_amounts.get(self.current_level, f"Level {self.current_level}:")
            self.level_label.config(text=level_text)
            
            # Play the new_question.mp3 sound
            self.play_new_question_sound()
            
            # Introduce a 3-second delay before updating the question text
            self.root.after(3000, lambda: self.question_label.config(text=next_question["question"]))
            
            # Introduce a 3-second delay before displaying the answers text
            for i in range(4):
                self.root.after(3000, lambda i=i: self.choice_buttons[i].config(text=next_question["choices"][i], state="active"))
        else:
            self.show_score()

    def check_answer(self, selected_choice):
        self.stop_question_display_sound()  # Stop the question display sound
        #self.display_selected_answer_image(selected_choice) # Display the selected answer image for 6 seconds

        self.play_answer_press_sound()  # Play the answer press sound for 6 seconds
        
        # Mapping of selected choices to image file names
        choice_to_image = {
            0: "A_selected.jpg",
            1: "B_selected.jpg",
            2: "C_selected.jpg",
            3: "D_selected.jpg",
        }

        # Get the selected image file name based on the choice
        image_file = choice_to_image.get(selected_choice)

        if image_file:
            # Load the selected image from the "images" subfolder
            image_path = os.path.join("images", image_file)
            selected_image = Image.open(image_path)
            selected_image = ImageTk.PhotoImage(selected_image)

            # Create a label to display the selected image behind all labels and buttons
            selected_image_label = tk.Label(self.root, image=selected_image)
            selected_image_label.image = selected_image
            selected_image_label.place(x=0, y=0, relwidth=1, relheight=1)
            selected_image_label.lift(self.bg_label)  # Lift the label above bg_label
            selected_image_label.lower(self.question_label)  # Lower the label below question_label
            selected_image_label.lower(self.level_label)  # Lower the label below level_label

            #Schedule the image to disappear after 6 seconds
            self.root.after(6500, lambda: selected_image_label.destroy())

        self.root.after(6000, self.reveal_answer, selected_choice)  # Introduce a 6-second delay


    def reveal_answer(self, selected_choice):

        if selected_choice == self.current_correct_answer:
            # Display the correct answer image based on the selected choice
            correct_image_file = f"{chr(65 + selected_choice)}_correct.jpg"
            correct_image_path = os.path.join("images", correct_image_file)

            if os.path.exists(correct_image_path):
                correct_image = Image.open(correct_image_path)
                correct_image = ImageTk.PhotoImage(correct_image)

                # Create a label to display the correct answer image behind all labels and buttons
                correct_image_label = tk.Label(self.root, image=correct_image)
                correct_image_label.image = correct_image
                correct_image_label.place(x=0, y=0, relwidth=1, relheight=1)
                correct_image_label.lift(self.bg_label)  # Lift the label above bg_label
                correct_image_label.lower(self.question_label)  # Lower the label below question_label
                correct_image_label.lower(self.level_label)  # Lower the label below level_label

                #Schedule the image label to be destroyed after 6 seconds
                self.root.after(6000, lambda: correct_image_label.destroy())

            self.score += 1
            if self.current_level not in [5, 10, 15]:
                self.play_correct_sound()
  
            else:
                if self.current_level == 5:
                    self.play_correct_sound_level5()
                elif self.current_level == 10:
                    self.play_correct_sound_level10()
                elif self.current_level == 15:
                    self.play_correct_sound_level15()
        else:
            self.play_wrong_sound()
            self.root.after(self.restart_delay, self.restart_game)
            return

        if self.current_level == 5:
            self.root.after(7000, self.next_question) # Longer delay for 5th question
            self.current_level += 1

        elif self.current_level == 10:
            self.root.after(8000, self.next_question) # Longer delay for 10th question
            self.current_level += 1

        elif self.current_level in (13,14):
            self.root.after(9000, self.next_question) # Longer delay for 13th question
            self.current_level += 1

        else:
            self.root.after(6000, self.next_question)  # Introduce a 4-second delay before the next question
            self.current_level += 1

    
    
    def play_correct_sound(self):
        try:
            sound_file = os.path.join("music", "correct1.mp3")
            correct_sound = pygame.mixer.Sound(sound_file)

            # Get the length of the audio in seconds
            correct_sound.play()

        except Exception as e:
            print("Error playing correct sound:", e)

    def play_correct_sound_level5(self):
        try:
            sound_file = os.path.join("music", "correct5.mp3")
            correct_sound = pygame.mixer.Sound(sound_file)
            correct_sound.play()
        except Exception as e:
            print("Error playing correct sound for level 5:", e)

    def play_correct_sound_level10(self):
        try:
            sound_file = os.path.join("music", "correct10.mp3")
            correct_sound = pygame.mixer.Sound(sound_file)
            correct_sound.play()
        except Exception as e:
            print("Error playing correct sound for level 10:", e)

    def play_correct_sound_level15(self):
        try:
            sound_file = os.path.join("music", "correct15.mp3")
            correct_sound = pygame.mixer.Sound(sound_file)
            correct_sound.play()
            # Stop the sound after 23 seconds
            self.root.after(23000, correct_sound.stop)
        except Exception as e:
            print("Error playing correct sound for level 15:", e)

    def play_wrong_sound(self):
        try:
            sound_file = os.path.join("music", "wrong1.mp3")
            wrong_sound = pygame.mixer.Sound(sound_file)
            wrong_sound.play()
        except Exception as e:
            print("Error playing wrong sound:", e)

    def play_new_question_sound(self):
        try:
            intro_sound_file = os.path.join("music", f"question{self.current_level}intro.mp3")
            intro_sound = pygame.mixer.Sound(intro_sound_file)

            # Get the length of the audio in seconds
            intro_audio_length = intro_sound.get_length()

            intro_sound.play()

            if self.current_question > 0:
                pygame.time.delay(int(intro_audio_length * 1000 - 500))  # Delay in milliseconds

            # Play the question display audio
            question_display_sound_file = os.path.join("music", "question_display.mp3")
            question_display_sound = pygame.mixer.Sound(question_display_sound_file)
            question_display_sound.play()
 

        except Exception as e:
            print(f"Error playing new question sound for level {self.current_level}:", e)

    def stop_question_display_sound(self):
        pygame.mixer.stop()

    def play_answer_press_sound(self):
        try:
            sound_file = os.path.join("music", "answer_press.mp3")
            answer_press_sound = pygame.mixer.Sound(sound_file)
            answer_press_sound.play()
            # Stop the sound after 6 seconds
            self.root.after(6000, answer_press_sound.stop)
        except Exception as e:
            print("Error playing answer press sound:", e)

    def restart_game(self):
        self.current_question = 0
        self.score = 0
        self.current_level = 1
        for button in self.choice_buttons:
            button.config(state="active")
        self.next_question()

    def show_score(self):
        messagebox.showinfo("Quiz Over", f"Your score: {self.score}/{len(self.questions)}")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
