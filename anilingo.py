import pygame
import yaml
import random

with open('lyrics.yaml', 'r', encoding="utf-8") as file:
    lyrics_data = yaml.safe_load(file)

pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ani-Lingo")
font = pygame.font.Font("./assets/japanese.font", 28)
kfont = pygame.font.Font("./assets/korean.font", 28)
box_width, box_height, box_margin = 120, 60, 20
box_color = {"default": (200, 200, 200), "selected": (230, 230, 230)}
selected_tokens = []

def create_button(text, x, y, width, height):
    button_rect = pygame.Rect(x, y, width, height)
    button_text = font.render(text, True, (0, 0, 0))
    button_text_rect = button_text.get_rect(center=button_rect.center)
    return button_rect, button_text, button_text_rect

def draw_button(button_rect, button_text, button_text_rect):
    pygame.draw.rect(screen, (200, 200, 200), button_rect, 0)
    screen.blit(button_text, button_text_rect)

def draw_correct_answer():
    correct_answer_text = " ".join(ordered_tokens)
    correct_answer_surface = font.render(correct_answer_text, True, (0, 0, 0))
    correct_answer_rect = correct_answer_surface.get_rect(center=(screen_width // 2, 180))
    screen.blit(correct_answer_surface, correct_answer_rect)

def reset_game():
    global random_lyric, original_lyric, english_translation, korean_translation, combined_tokens, tokens, selected_tokens, ordered_tokens, hiragana_tokens
    random_lyric = random.choice(lyrics_data)
    original_lyric = random_lyric['original']
    english_translation, korean_translation = random_lyric['english'], random_lyric['korean']
    ordered_tokens, hiragana_ordered_tokens = random_lyric['tokens'].split(','), random_lyric['hiragana'].split(',')
    tokens, hiragana_tokens = ordered_tokens.copy(), hiragana_ordered_tokens.copy()
    combined_tokens = list(zip(ordered_tokens, hiragana_ordered_tokens))
    random.shuffle(combined_tokens)
    tokens, hiragana_tokens = zip(*combined_tokens)
    selected_tokens = []

def draw_token_boxes(tokens, hiragana_tokens, hovered_box_index):
    global start_x, y
    num_tokens = len(tokens)
    max_line_width = screen_width - 2 * box_margin
    num_tokens_per_line = max_line_width // (box_width + box_margin)
    line_width = num_tokens_per_line * box_width + (num_tokens_per_line - 1) * box_margin
    num_lines = (num_tokens + num_tokens_per_line - 1) // num_tokens_per_line
    start_y = (screen_height - (num_lines * (box_height + box_margin) - box_margin)) // 2
    token_index = 0
    token_boxes = []
    global_index = 0
    for line in range(num_lines):
        line_tokens = tokens[token_index:token_index + num_tokens_per_line]
        num_tokens_in_line = len(line_tokens)
        line_width = num_tokens_in_line * box_width + (num_tokens_in_line - 1) * box_margin
        start_x = (screen_width - line_width) // 2
        y = start_y + (box_height + box_margin) * line

        for idx, token in enumerate(line_tokens):
            global_index = idx + line * num_tokens_per_line
            box_x = start_x
            box_rect = pygame.Rect(box_x, y, box_width, box_height)

            if global_index in selected_tokens:
                box_color_key = "selected"
            else:
                box_color_key = "default"

            pygame.draw.rect(screen, box_color[box_color_key], box_rect, 0)
            if global_index == hovered_box_index and token != hiragana_tokens[global_index]:
                token_to_render = hiragana_tokens[global_index]
            else:
                token_to_render = token
            text = font.render(token_to_render, True, (0, 0, 0))
            text_rect = text.get_rect(center=(box_rect.centerx, box_rect.centery))
            screen.blit(text, text_rect)
            start_x += box_width + box_margin
            global_index += 1
            token_boxes.append(box_rect)
        token_index += num_tokens_per_line
    pygame.display.flip()
    return token_boxes

def draw_token_box(token, box_rect, color_key):
    pygame.draw.rect(screen, box_color[color_key], box_rect, 0)
    text = font.render(token, True, (0, 0, 0))
    text_rect = text.get_rect(center=(box_rect.centerx, box_rect.centery))
    screen.blit(text, text_rect)
    pygame.display.update(box_rect)

running = True
needs_redraw = True
next_question_button, next_question_text, next_question_text_rect = create_button("Next question", 200, 500, 200, 50)
try_again_button, try_again_text, try_again_text_rect = create_button("Try again", 450, 500, 200, 50)
show_answer_button, show_answer_text, show_answer_text_rect = create_button("Show answer", 200, 500, 200, 50)
show_correct_answer = False
hovered_box_index = None
previous_hovered_box_index = None
token_boxes = []

reset_game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            for i, box_rect in enumerate(token_boxes):
                if box_rect.collidepoint(pygame.mouse.get_pos()):
                    hovered_box_index = i
                    break
                else:
                    hovered_box_index = None
            if hovered_box_index != previous_hovered_box_index:
                if previous_hovered_box_index is not None:
                    box_rect = token_boxes[previous_hovered_box_index]
                    color_key = "selected" if previous_hovered_box_index in selected_tokens else "default"
                    token_to_render = tokens[previous_hovered_box_index]
                    draw_token_box(token_to_render, box_rect, color_key)
                if hovered_box_index is not None:
                    box_rect = token_boxes[hovered_box_index]
                    color_key = "selected" if hovered_box_index in selected_tokens else "default"
                    if tokens[hovered_box_index] != hiragana_tokens[hovered_box_index]:
                        token_to_render = hiragana_tokens[hovered_box_index]
                    else:
                        token_to_render = tokens[hovered_box_index]
                    draw_token_box(token_to_render, box_rect, color_key)
                previous_hovered_box_index = hovered_box_index
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, box_rect in enumerate(token_boxes):
                if box_rect.collidepoint(event.pos):
                    if i in selected_tokens:
                        selected_tokens.remove(i)
                    else:
                        selected_tokens.append(i)
                    needs_redraw = True
                    break
    if needs_redraw:
        screen.fill((255, 255, 255))
        english_text = font.render(english_translation, True, (0, 0, 0))
        english_text_rect = english_text.get_rect(center=(screen_width // 2, 30))
        screen.blit(english_text, english_text_rect)
        korean_text = kfont.render(korean_translation, True, (0, 0, 0))
        korean_text_rect = korean_text.get_rect(center=(screen_width // 2, 65))
        screen.blit(korean_text, korean_text_rect)
        token_boxes = draw_token_boxes(tokens, hiragana_tokens, hovered_box_index)
        selected_text = " ".join(tokens[i] for i in selected_tokens)
        selected_text_surface = font.render(selected_text, True, (0, 0, 0))
        selected_text_rect = selected_text_surface.get_rect(center=(screen_width // 2, 140))
        screen.blit(selected_text_surface, selected_text_rect)

        if len(selected_tokens) == len(tokens):
            selected_token_values = [tokens[i] for i in selected_tokens]
            if selected_token_values == ordered_tokens:
                result_text = "Correct!"
                draw_button(next_question_button, next_question_text, next_question_text_rect)
            else:
                result_text = "Incorrect..."
                draw_button(try_again_button, try_again_text, try_again_text_rect)
                draw_button(show_answer_button, show_answer_text, show_answer_text_rect)
            result_text_surface = font.render(result_text, True, (0, 0, 0))
            result_text_rect = result_text_surface.get_rect(center=(screen_width // 2, 110))
            screen.blit(result_text_surface, result_text_rect)
            if show_correct_answer:
                draw_correct_answer()
                show_correct_answer = False
        pygame.display.flip()
        needs_redraw = False

    if event.type == pygame.MOUSEBUTTONDOWN:
        if next_question_button.collidepoint(event.pos) and len(selected_tokens) == len(tokens) and selected_token_values == ordered_tokens:
            reset_game()
            needs_redraw = True
        elif try_again_button.collidepoint(event.pos) and len(selected_tokens) == len(tokens) and selected_tokens != tokens:
            selected_tokens = []
            random.shuffle(combined_tokens)
            tokens, hiragana_tokens = zip(*combined_tokens)
            needs_redraw = True
        if show_answer_button.collidepoint(event.pos) and len(selected_tokens) == len(tokens) and selected_token_values != ordered_tokens:
            show_correct_answer = True
            needs_redraw = True
pygame.quit()
