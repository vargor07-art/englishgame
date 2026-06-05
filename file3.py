import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1024, 725))
pygame.display.set_caption("Learn English - Airport Scenario")

try:
    icon = pygame.image.load('images/game icon.png')
    pygame.display.set_icon(icon)
except:
    pass

clock = pygame.time.Clock()

class Player:
    """Класс игрока с анимацией и движением"""
    def __init__(self, x, y, images_right, images_left, speed=5):
        self.x = x
        self.y = y
        self.images_right = images_right
        self.images_left = images_left
        self.speed = speed
        self.walk_count = 0
        self.direction = "right"
        self.animation_speed = 0
        self.moving = False
        
    def update(self):
        if self.moving:
            self.animation_speed += 1
            if self.animation_speed >= 6:
                self.animation_speed = 0
                self.walk_count = (self.walk_count + 1) % len(self.images_right)
        else:
            self.walk_count = 0
            
    def move_left(self):
        self.x -= self.speed
        self.direction = "left"
        self.moving = True
        
    def move_right(self):
        self.x += self.speed
        self.direction = "right"
        self.moving = True
        
    def stop(self):
        self.moving = False
        
    def draw(self, screen):
        if self.direction == "right":
            screen.blit(self.images_right[self.walk_count], (self.x, self.y))
        else:
            screen.blit(self.images_left[self.walk_count], (self.x, self.y))
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, 50, 50)

class NPC:
    """Класс NPC"""
    def __init__(self, x, y, image, target_x, target_y, speed=1):
        self.x = x
        self.y = y
        self.image = image
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.moving = False
        self.reached = False
        
    def move_to_target(self):
        if not self.reached:
            if self.x < self.target_x:
                self.x += self.speed
                self.moving = True
            elif self.x > self.target_x:
                self.x -= self.speed
                self.moving = True
                
            if self.y < self.target_y:
                self.y += self.speed
                self.moving = True
            elif self.y > self.target_y:
                self.y -= self.speed
                self.moving = True
                
            if abs(self.x - self.target_x) < 5 and abs(self.y - self.target_y) < 5:
                self.reached = True
                self.moving = False
                
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, 50, 50)

class DialogBox:
    """Класс диалогового окна"""
    def __init__(self):
        self.active = False
        self.question = ""
        self.correct_answer = ""
        self.user_input = ""
        self.message = ""
        self.message_color = (0, 128, 0)
        self.options = []
        self.selected_option = 0
        self.is_multiple_choice = False
        self.awaiting_response = False
        self.hint = ""  
        
    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
        
    def show_question(self, question, correct_answer, is_multiple_choice=False, options=None, hint=""):
        self.active = True
        self.question = question
        self.correct_answer = correct_answer
        self.user_input = ""
        self.message = ""
        self.is_multiple_choice = is_multiple_choice
        self.awaiting_response = True
        self.hint = hint 
        if options:
            self.options = options
            self.selected_option = 0
            
    def handle_input(self, event):
        if not self.active or not self.awaiting_response:
            return None
            
        if event.type == pygame.KEYDOWN:
            if self.is_multiple_choice:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                    return None  
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                    return None
                elif event.key == pygame.K_RETURN:
                    return self.options[self.selected_option]
                elif event.key == pygame.K_1 and len(self.options) >= 1:
                    return self.options[0]
                elif event.key == pygame.K_2 and len(self.options) >= 2:
                    return self.options[1]
                elif event.key == pygame.K_3 and len(self.options) >= 3:
                    return self.options[2]
                elif event.key == pygame.K_h:
                    self.show_hint_popup()
                    return None
            else:
                if event.key == pygame.K_RETURN:
                    return self.user_input
                elif event.key == pygame.K_BACKSPACE:
                    self.user_input = self.user_input[:-1]
                elif event.key == pygame.K_h: 
                    self.show_hint_popup()
                    return None
                else:
                    if event.unicode.isprintable():
                        self.user_input += event.unicode
        return None
    
    def show_hint_popup(self):
        self.hint_active = True
        
    def close(self):
        self.active = False
        self.awaiting_response = False
        
    def set_waiting(self, waiting):
        self.awaiting_response = waiting
        
    def draw(self, screen, font, small_font):
        if not self.active:
            return
            
        pygame.draw.rect(screen, (255, 255, 255), (50, 150, 670, 450))
        pygame.draw.rect(screen, (0, 0, 0), (50, 150, 670, 450), 3)
        
        y_offset = 180
        max_width = 580  

        question_lines = self.wrap_text(self.question, font, max_width)
        
        for line in question_lines:
            q_text = font.render(line, True, (0, 0, 0))
            screen.blit(q_text, (70, y_offset))
            y_offset += 35  
        
        y_offset += 10 

        if self.hint:
            hint_text = small_font.render(f"Подсказка: {self.hint}", True, (100, 100, 255))
            screen.blit(hint_text, (70, y_offset))
            y_offset += 30

        hint_instruction = small_font.render(" ", True, (150, 150, 150))
        screen.blit(hint_instruction, (70, y_offset))
        y_offset += 30
            
        if self.is_multiple_choice and self.awaiting_response:
            for i, option in enumerate(self.options):
                if i == self.selected_option:
                    color = (255, 0, 0)
                    prefix = " ->"
                else:
                    color = (0, 0, 0)
                    prefix = "   "

                option_text = f"{prefix}{i+1}. {option}"
                if font.size(option_text)[0] > max_width - 20:
                    while font.size(option_text)[0] > max_width - 20 and len(option_text) > 10:
                        option_text = option_text[:-1]
                    option_text += "..."
                
                opt_text = font.render(option_text, True, color)
                screen.blit(opt_text, (70, y_offset + i * 35))
            
            hint1 = small_font.render("Используй стрелки верх/вниз или цифры 1-3 для выбора", True, (100, 100, 100))
            hint2 = small_font.render("ENTER для подтверждения", True, (100, 100, 100))
            screen.blit(hint1, (70, y_offset + len(self.options) * 35 + 10))
            screen.blit(hint2, (70, y_offset + len(self.options) * 35 + 35))
            
        elif not self.is_multiple_choice and self.awaiting_response:
            pygame.draw.rect(screen, (200, 200, 200), (70, y_offset, 500, 40))
            pygame.draw.rect(screen, (0, 0, 0), (70, y_offset, 500, 40), 2)
            answer_text = font.render(self.user_input + "_", True, (0, 0, 0))
            screen.blit(answer_text, (80, y_offset + 8))
            
            hint = small_font.render("Напиши ответ и нажми ENTER", True, (100, 100, 100))
            screen.blit(hint, (70, y_offset + 55))
            
        if self.message:
            msg_lines = self.wrap_text(self.message, small_font, max_width)
            msg_y = y_offset + 100
            for line in msg_lines:
                msg_text = small_font.render(line, True, self.message_color)
                screen.blit(msg_text, (70, msg_y))
                msg_y += 25
            
    def set_message(self, msg, is_error=False):
        self.message = msg
        self.message_color = (255, 0, 0) if is_error else (0, 128, 0)

class Game:
    """Основной класс игры"""
    def __init__(self):
        self.score = 0
        self.politeness_score = 100
        self.scenario = None  
        self.stage = 0
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.dialog = DialogBox()
        self.running = True
        self.game_over = False
        self.waiting_for_next = False
        self.wait_timer = 0
        self.message_timer = 0
        self.showing_error_popup = False
        self.error_popup_timer = 0
        self.error_message = ""
        
        try:
            player_right = [
                pygame.image.load('images/player111.png'),
            ]
            player_left = [
                pygame.image.load('images/player2222.png'),
            ]
        except:
            player_right = [pygame.Surface((40, 50)), pygame.Surface((40, 50))]
            player_left = [pygame.Surface((40, 50)), pygame.Surface((40, 50))]
            for surf in player_right:
                surf.fill((0, 255, 0))
            for surf in player_left:
                surf.fill((0, 255, 0))
        
        self.player = Player(70, 300, player_right, player_left, speed=5)
        
        try:
            npc_img = pygame.image.load('images/player2222.png')
        except:
            npc_img = pygame.Surface((40, 50))
            npc_img.fill((255, 0, 0))
        
        # ИСПРАВЛЕНИЕ: target_y совпадает с начальным y=300, чтобы NPC не двигался вниз
        self.npc = NPC(640, 300, npc_img, 500, 300, speed=0.5)
        
        try:
            self.home_bg = pygame.image.load('images/home.jpg')
        except:
            self.home_bg = pygame.Surface((1024, 725))
            self.home_bg.fill((50, 50, 150))
        
        try:
            self.airport_bg = pygame.image.load('images/airport6.png')
        except:
            self.airport_bg = pygame.Surface((1024, 725))
            self.airport_bg.fill((100, 150, 200))
        
        try:
            self.supermarket_bg = pygame.image.load('images/supermarket.png')
        except:
            self.supermarket_bg = pygame.Surface((1024, 725))
            self.supermarket_bg.fill((150, 200, 100))
        
        self.current_bg = self.home_bg
        
        self.current_scenario_index = 0
        self.question_attempts = 0  
        self.waiting_after_error = False  
        
        self.airport_scenarios = [
            self.scenario_passport_check,
            self.scenario_announcement,
            self.scenario_lost_luggage
        ]
        
        self.supermarket_scenarios = [
            self.scenario_supermarket_1,
            self.scenario_supermarket_2,
            self.scenario_supermarket_3
        ]
        
        self.dialog_triggered = False
        self.selected_scenario = None  
        
    def start_scenario(self, scenario_name):
        """Запуск выбранного сценария"""
        self.scenario = scenario_name
        self.current_scenario_index = 0
        self.question_attempts = 0
        self.waiting_after_error = False
        self.dialog_triggered = False
        self.game_over = False
        self.score = 0
        self.politeness_score = 100
        
        if scenario_name == "airport":
            self.current_bg = self.airport_bg
        else: 
            self.current_bg = self.supermarket_bg

        # ИСПРАВЛЕНИЕ: target_y = 300, совпадает с y игрока, NPC идёт только по X
        self.npc.target_x = 500
        self.npc.target_y = 300
        
        self.npc.x = 640  
        self.npc.y = 300   # было 325 — исправлено на 300
        self.npc.reached = False
        self.npc.moving = False
        self.player.x = 70   
        self.player.y = 300  
        
        if hasattr(self, 'luggage_step'):
            delattr(self, 'luggage_step')
        
    def show_error_popup(self, error_text):
        self.showing_error_popup = True
        self.error_popup_timer = pygame.time.get_ticks()
        self.error_message = error_text
        
    def reset_current_question(self):
        self.waiting_for_next = False
        self.wait_timer = 0
        self.dialog.active = False
        self.dialog.awaiting_response = False
        
    def scenario_passport_check(self):
        """Скрипт 1.1: Проверка паспорта"""
        if not self.dialog.active and not self.waiting_for_next and not self.waiting_after_error:
            self.question_attempts += 1
            self.dialog.show_question(
                "Good morning. Can I see your passport and ticket, please?",
                "Here you are",
                is_multiple_choice=True,
                options=["Here you are.", "Take it.", "My passport."],
                hint="вы должны быть вежливыми"
            )
            
    def check_passport_answer(self, answer):
        if answer == "Here you are.":
            self.dialog.set_message("Правильно! +10 очков вежливости")
            self.score += 10
            self.politeness_score = min(100, self.politeness_score + 10)
            self.waiting_for_next = True
            self.wait_timer = pygame.time.get_ticks()
            self.current_scenario_index = 1
            self.question_attempts = 0  
            self.dialog.close()
        else:
            if answer == "Take it.":
                error_msg = f"Грубый ответ! -10 очков вежливости\nПодсказка: нужно быть вежливым\nПопытка {self.question_attempts + 1}"
                self.dialog.set_message(error_msg, is_error=True)
                self.show_error_popup(error_msg)
                self.politeness_score = max(0, self.politeness_score - 10)
            elif answer == "My passport.":
                error_msg = f"Слишком сухо! -5 очков вежливости\nПодсказка: нужно быть вежливым\nПопытка {self.question_attempts + 1}"
                self.dialog.set_message(error_msg, is_error=True)
                self.show_error_popup(error_msg)
                self.politeness_score = max(0, self.politeness_score - 5)

            self.waiting_after_error = True
            self.wait_timer = pygame.time.get_ticks()
            self.dialog.close()
            
    def scenario_announcement(self):
        """Скрипт 1.2: Объявление"""
        if not self.dialog.active and not self.waiting_for_next and not self.waiting_after_error:
            self.question_attempts += 1
            announcement = "Attention, passengers of flight BA 249 to London. "
            announcement += "Boarding will begin at gate 15 in five minutes."
            announcement += "Your flight: BA 249, Gate 15, Time: 10:45."
            announcement += "What should you do?"
            
            self.dialog.show_question(
                announcement,
                "B",
                is_multiple_choice=True,
                options=["A. Finish coffee calmly, there's time",
                        "B. Run to gate 15 right now",
                        "C. Ask the waiter what was said"],
                hint="спрашивается, что вам надо сделать после объявления"
            )
            
    def check_announcement_answer(self, answer):
        if answer.startswith("B"):
            self.dialog.set_message("Правильно! Boarding starts in 5 minutes, you need to go!")
            self.score += 15
            self.waiting_for_next = True
            self.wait_timer = pygame.time.get_ticks()
            self.current_scenario_index = 2
            self.question_attempts = 0
            self.dialog.close()
        else:
            if answer.startswith("A"):
                error_msg = f"Ошибка! You missed your flight.\nПодсказка: после объявления нужно сразу идти к выходу\nПопытка {self.question_attempts + 1}"
                self.dialog.set_message(error_msg, is_error=True)
                self.show_error_popup(error_msg)
                self.score = max(0, self.score - 20)
            elif answer.startswith("C"):
                error_msg = f"You wasted time! Boarding has already started!\nПодсказка: нужно сразу реагировать на объявление\nПопытка {self.question_attempts + 1}"
                self.dialog.set_message(error_msg, is_error=True)
                self.show_error_popup(error_msg)
                self.score = max(0, self.score - 10)

            self.waiting_after_error = True
            self.wait_timer = pygame.time.get_ticks()
            self.dialog.close()
            
    def scenario_lost_luggage_step0(self):
        """Скрипт 1.3: Потеря багажа - шаг 0"""
        if not self.dialog.active and not self.waiting_for_next and not self.waiting_after_error:
            self.dialog.show_question(
                "How can I help you? Put the dialog in the correct order:",
                "1,2,3",
                is_multiple_choice=True,
                options=["1. My suitcase hasn't arrived.",
                        "2. It's a big, black Samsonite.",
                        "3. My name is John Smith, flight from Paris."],
                hint="вы должны отвечать на вопрос, который вам задает работник"
            )
            
    def scenario_lost_luggage_step1(self):
        """Скрипт 1.3: Потеря багажа - шаг 1"""
        if not self.dialog.active and not self.waiting_for_next and not self.waiting_after_error:
            self.dialog.show_question(
                "Great! What's your name and flight? Then describe your suitcase.",
                "3,2",
                is_multiple_choice=True,
                options=["2. It's a big, black Samsonite.",
                        "3. My name is John Smith, flight from Paris."],
                hint="вы должны отвечать на вопрос, который вам задает работник"
            )
            
    def scenario_lost_luggage(self):
        if not hasattr(self, 'luggage_step'):
            self.luggage_step = 0
            
        if self.luggage_step == 0:
            self.scenario_lost_luggage_step0()
        elif self.luggage_step == 1:
            self.scenario_lost_luggage_step1()
                
    def check_luggage_answer(self, answer):
        if self.luggage_step == 0:
            if answer.startswith("1"):
                self.dialog.set_message("Good! Now tell me your flight and describe the suitcase.")
                self.luggage_step = 1
                self.dialog.close()
                self.waiting_for_next = True
                self.wait_timer = pygame.time.get_ticks()
            else:
                error_msg = f"Wrong order! Start with the problem.\nПодсказка: сначала сообщите о проблеме\nПопытка {self.question_attempts + 1}"
                self.dialog.set_message(error_msg, is_error=True)
                self.show_error_popup(error_msg)
                self.score = max(0, self.score - 5)
                self.waiting_after_error = True
                self.wait_timer = pygame.time.get_ticks()
                self.dialog.close()
        elif self.luggage_step == 1:
            if answer.startswith("3"):
                self.dialog.set_message("Excellent! The staff will find your suitcase. Airport scenario completed!")
                self.score += 20
                self.game_over = True
                self.dialog.close()
            else:
                error_msg = f"First tell your name and flight, then describe the suitcase!\nПодсказка: отвечайте на вопрос работника\nПопытка {self.question_attempts + 1}"
                self.dialog.set_message(error_msg, is_error=True)
                self.show_error_popup(error_msg)
                self.score = max(0, self.score - 5)
                self.waiting_after_error = True
                self.wait_timer = pygame.time.get_ticks()
                self.dialog.close()

    def scenario_supermarket_1(self):
        """Скрипт 2: Поиск хлеба и молока"""
        if not self.dialog.active and not self.waiting_for_next and not self.waiting_after_error:
            self.question_attempts += 1
            self.dialog.show_question(
                "I need bread and milk. Where do I go?",
                "Dairy and Bakery",
                is_multiple_choice=True,
                options=["Dairy and Bakery", "Frozen food and Fruit & veg", "Bakery and frozen food"],
                hint="Надо выбрать отделы где есть хлеб и молоко"
            )
            
    def check_supermarket_1_answer(self, answer):
        if answer == "Dairy and Bakery":
            self.dialog.set_message("Правильно! Хлеб в пекарне (Bakery), а молоко в молочном отделе (Dairy)!")
            self.score += 15
            self.politeness_score = min(100, self.politeness_score + 5)
            self.waiting_for_next = True
            self.wait_timer = pygame.time.get_ticks()
            self.current_scenario_index = 1
            self.question_attempts = 0
            self.dialog.close()
        else:
            if answer == "Frozen food and Fruit & veg":
                error_msg = f"Неправильно! В замороженных продуктах нет хлеба и молока.\nПодсказка: {self.dialog.hint}\nПопытка {self.question_attempts + 1}"
                self.dialog.set_message(error_msg, is_error=True)
                self.show_error_popup(error_msg)
                self.score = max(0, self.score - 5)
            elif answer == "Bakery and frozen food":
                error_msg = f"Неправильно! В замороженных продуктах нет молока.\nПодсказка: {self.dialog.hint}\nПопытка {self.question_attempts + 1}"
                self.dialog.set_message(error_msg, is_error=True)
                self.show_error_popup(error_msg)
                self.score = max(0, self.score - 5)

            self.waiting_after_error = True
            self.wait_timer = pygame.time.get_ticks()
            self.dialog.close()
            
    def scenario_supermarket_2(self):
        """Скрипт 2.2: Ответ на вопрос работника"""
        if not self.dialog.active and not self.waiting_for_next and not self.waiting_after_error:
            self.question_attempts += 1
            self.dialog.show_question(
                "Excuse me, could I help you?",
                "Yes, I am looking for the spice's aisle.",
                is_multiple_choice=True,
                options=["Yes, I am looking for the spice's aisle.", 
                        "Of course, I'll be happy to lend you a hand",
                        "Sorry to bother you."],
                hint="Каким может быть ответ на вопрос работника"
            )
            
    def check_supermarket_2_answer(self, answer):
        if answer == "Yes, I am looking for the spice's aisle.":
            self.dialog.set_message("Правильно! Это вежливый ответ, указывающий на то, что вам нужна помощь!")
            self.score += 15
            self.politeness_score = min(100, self.politeness_score + 10)
            self.waiting_for_next = True
            self.wait_timer = pygame.time.get_ticks()
            self.current_scenario_index = 2
            self.question_attempts = 0
            self.dialog.close()
        else:
            if answer == "Of course, I'll be happy to lend you a hand":
                error_msg = f"Неправильно! Это ответ работника, а не покупателя.\nПодсказка: {self.dialog.hint}\nПопытка {self.question_attempts + 1}"
                self.dialog.set_message(error_msg, is_error=True)
                self.show_error_popup(error_msg)
                self.politeness_score = max(0, self.politeness_score - 5)
            elif answer == "Sorry to bother you.":
                error_msg = f"Неправильно! Это ответ покупателя, который НЕ нуждается в помощи.\nПодсказка: {self.dialog.hint}\nПопытка {self.question_attempts + 1}"
                self.dialog.set_message(error_msg, is_error=True)
                self.show_error_popup(error_msg)
                self.politeness_score = max(0, self.politeness_score - 5)

            self.waiting_after_error = True
            self.wait_timer = pygame.time.get_ticks()
            self.dialog.close()
            
    def scenario_supermarket_3(self):
        """Скрипт 2.3: Расчет итоговой суммы"""
        if not self.dialog.active and not self.waiting_for_next and not self.waiting_after_error:
            self.question_attempts += 1
            self.dialog.show_question(
                "Your total comes to 89.9 pounds with the 15% discount it'll be 76.42 pounds. Oh, sorry I forgot to delete the flour, then it'll be 71.3 pounds. What is the total?",
                "71.3 pounds",
                is_multiple_choice=True,
                options=["89.9 pounds", "71.3 pounds", "76.42 pounds"],
                hint="Какая итоговая сумма после всех вычислений"
            )
            
    def check_supermarket_3_answer(self, answer):
        if answer == "71.3 pounds":
            self.dialog.set_message("Правильно! Итоговая сумма 71.3 фунта после всех вычетов!")
            self.score += 20
            self.waiting_for_next = True
            self.wait_timer = pygame.time.get_ticks()
            self.game_over = True
            self.dialog.close()
        else:
            if answer == "89.9 pounds":
                error_msg = f"Неправильно! Это начальная сумма без учета скидки.\nПодсказка: {self.dialog.hint}\nПопытка {self.question_attempts + 1}"
                self.dialog.set_message(error_msg, is_error=True)
                self.show_error_popup(error_msg)
                self.score = max(0, self.score - 5)
            elif answer == "76.42 pounds":
                error_msg = f"Неправильно! Это сумма со скидкой, но без вычета муки.\nПодсказка: {self.dialog.hint}\nПопытка {self.question_attempts + 1}"
                self.dialog.set_message(error_msg, is_error=True)
                self.show_error_popup(error_msg)
                self.score = max(0, self.score - 5)

            self.waiting_after_error = True
            self.wait_timer = pygame.time.get_ticks()
            self.dialog.close()
    
    def draw_home_screen(self):
        screen.blit(self.home_bg, (0, 0))

        title_font = pygame.font.Font(None, 72)
        title = title_font.render("Learn English", True, (255, 215, 0))
        screen.blit(title, (370, 100))
        
        subtitle = self.font.render("Choose a scenario:", True, (255, 255, 255))
        screen.blit(subtitle, (420, 200))

        button_width = 300
        button_height = 80
        button_y = 300
        spacing = 40

        airport_button_rect = pygame.Rect((1024 - button_width) // 2, button_y, button_width, button_height)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if airport_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (100, 150, 200), airport_button_rect)
            pygame.draw.rect(screen, (255, 215, 0), airport_button_rect, 3)
            if mouse_click[0]:
                self.start_scenario("airport")
        else:
            pygame.draw.rect(screen, (70, 100, 150), airport_button_rect)
            pygame.draw.rect(screen, (200, 200, 200), airport_button_rect, 2)
        
        airport_text = self.font.render("AIRPORT SCENARIO", True, (255, 255, 255))
        airport_text_rect = airport_text.get_rect(center=airport_button_rect.center)
        screen.blit(airport_text, airport_text_rect)

        supermarket_button_rect = pygame.Rect((1024 - button_width) // 2, button_y + button_height + spacing, button_width, button_height)
        
        if supermarket_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (100, 150, 100), supermarket_button_rect)
            pygame.draw.rect(screen, (255, 215, 0), supermarket_button_rect, 3)
            if mouse_click[0]:
                self.start_scenario("supermarket")
        else:
            pygame.draw.rect(screen, (70, 100, 70), supermarket_button_rect)
            pygame.draw.rect(screen, (200, 200, 200), supermarket_button_rect, 2)
        
        supermarket_text = self.font.render("SUPERMARKET SCENARIO", True, (255, 255, 255))
        supermarket_text_rect = supermarket_text.get_rect(center=supermarket_button_rect.center)
        screen.blit(supermarket_text, supermarket_text_rect)
        
        instruction = self.small_font.render("Click on a scenario to start", True, (200, 200, 200))
        screen.blit(instruction, (420, 550))
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            if self.scenario is None:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pass
                return
            
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.__init__()
                    elif event.key == pygame.K_ESCAPE:
                        self.scenario = None 
                        self.game_over = False
                    return
                
                if self.showing_error_popup:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.showing_error_popup = False
                    return
                
                if not self.dialog.active:
                    if event.key == pygame.K_LEFT:
                        self.player.move_left()
                    elif event.key == pygame.K_RIGHT:
                        self.player.move_right()
                    elif event.key == pygame.K_ESCAPE:
                        self.scenario = None  
                        self.game_over = False
                        return
                
                if self.dialog.active:
                    answer = self.dialog.handle_input(event)
                    if answer is not None:
                        if self.scenario == "airport":
                            if self.current_scenario_index == 0:
                                self.check_passport_answer(answer)
                            elif self.current_scenario_index == 1:
                                self.check_announcement_answer(answer)
                            elif self.current_scenario_index == 2:
                                self.check_luggage_answer(answer)
                        else:  
                            if self.current_scenario_index == 0:
                                self.check_supermarket_1_answer(answer)
                            elif self.current_scenario_index == 1:
                                self.check_supermarket_2_answer(answer)
                            elif self.current_scenario_index == 2:
                                self.check_supermarket_3_answer(answer)
                            
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    self.player.stop()
                    
    def update(self):
        if self.scenario is None or self.game_over:
            return

        if self.showing_error_popup and pygame.time.get_ticks() - self.error_popup_timer > 10000:
            self.showing_error_popup = False
            if self.waiting_after_error:
                self.waiting_after_error = False
                if self.scenario == "airport":
                    if self.current_scenario_index == 2 and hasattr(self, 'luggage_step'):
                        if self.luggage_step == 0:
                            self.scenario_lost_luggage_step0()
                        else:
                            self.scenario_lost_luggage_step1()
                    else:
                        self.airport_scenarios[self.current_scenario_index]()
                else:  
                    self.supermarket_scenarios[self.current_scenario_index]()

        if self.waiting_for_next and pygame.time.get_ticks() - self.wait_timer > 2000:
            self.waiting_for_next = False

        if self.waiting_after_error and not self.showing_error_popup and pygame.time.get_ticks() - self.wait_timer > 2000:
            self.waiting_after_error = False
            if self.scenario == "airport":
                if self.current_scenario_index == 2 and hasattr(self, 'luggage_step'):
                    if self.luggage_step == 0:
                        self.scenario_lost_luggage_step0()
                    else:
                        self.scenario_lost_luggage_step1()
                else:
                    self.airport_scenarios[self.current_scenario_index]()
            else:  
                self.supermarket_scenarios[self.current_scenario_index]()
            
        self.npc.move_to_target()

        if self.npc.reached and not self.dialog.active and not self.waiting_for_next and not self.waiting_after_error and not self.game_over and not self.showing_error_popup:
            if self.scenario == "airport":
                if self.current_scenario_index < len(self.airport_scenarios):
                    self.airport_scenarios[self.current_scenario_index]()
            else:  
                if self.current_scenario_index < len(self.supermarket_scenarios):
                    self.supermarket_scenarios[self.current_scenario_index]()
            
        self.player.update()
        
    def draw_error_popup(self):
        if not self.showing_error_popup:
            return

        overlay = pygame.Surface((1024, 725))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        popup_width = 550
        popup_height = 220
        popup_x = (1024 - popup_width) // 2
        popup_y = (725 - popup_height) // 2
        
        pygame.draw.rect(screen, (255, 255, 255), (popup_x, popup_y, popup_width, popup_height))
        pygame.draw.rect(screen, (255, 0, 0), (popup_x, popup_y, popup_width, popup_height), 3)
        
        title = self.font.render("НЕПРАВИЛЬНО!", True, (255, 0, 0))
        screen.blit(title, (popup_x + 180, popup_y + 20))

        y_offset = popup_y + 70
        for line in self.error_message.split('\n'):
            error_text = self.small_font.render(line, True, (0, 0, 0))
            screen.blit(error_text, (popup_x + 50, y_offset))
            y_offset += 30

        close_text = self.small_font.render("Нажми ПРОБЕЛ, ENTER или ESC для продолжения", True, (100, 100, 100))
        screen.blit(close_text, (popup_x + 130, popup_y + 180))

        retry_text = self.small_font.render("Попробуй еще раз!", True, (255, 100, 0))
        screen.blit(retry_text, (popup_x + 200, popup_y + 155))
        
    def draw(self):
        if self.scenario is None:
            self.draw_home_screen()
            pygame.display.update()
            return
        
        screen.blit(self.current_bg, (0, 0))
        
        self.player.draw(screen)
        self.npc.draw(screen)
        
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        polite_text = self.small_font.render(f"Politeness: {self.politeness_score}", True, (255, 255, 0))
        screen.blit(polite_text, (10, 50))
        
        if not self.npc.reached and not self.dialog.active and not self.game_over:
            hint = self.small_font.render("Walk towards the officer (<- -> arrows)", True, (255, 255, 255))
            screen.blit(hint, (10, 90))
            
            hint_h = self.small_font.render("Press H for hint during dialog", True, (200, 200, 100))
            screen.blit(hint_h, (10, 110))
            
            back_hint = self.small_font.render("Press ESC to return to menu", True, (200, 200, 100))
            screen.blit(back_hint, (10, 130))

        if self.dialog.active and self.question_attempts > 0:
            attempt_text = self.small_font.render(f"Attempt: {self.question_attempts}", True, (255, 200, 0))
            screen.blit(attempt_text, (900, 110))
        
        self.dialog.draw(screen, self.font, self.small_font)

        self.draw_error_popup()
        
        if self.game_over:
            overlay = pygame.Surface((1024, 725))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            win_text = self.font.render(f"{self.scenario.upper()} SCENARIO COMPLETED!", True, (255, 215, 0))
            win_text_rect = win_text.get_rect(center=(512, 280))
            screen.blit(win_text, win_text_rect)
            
            score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            score_text_rect = score_text.get_rect(center=(512, 340))
            screen.blit(score_text, score_text_rect)
            
            restart_text = self.small_font.render("Press R to restart", True, (255, 255, 255))
            restart_text_rect = restart_text.get_rect(center=(512, 400))
            screen.blit(restart_text, restart_text_rect)
            
            menu_text = self.small_font.render("Press ESC to return to menu", True, (255, 255, 255))
            menu_text_rect = menu_text.get_rect(center=(512, 430))
            screen.blit(menu_text, menu_text_rect)
            
        pygame.display.update()
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(30)

if __name__ == "__main__":
    game = Game()
    game.run()