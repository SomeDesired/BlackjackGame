import copy
import pygame
import random
pygame.init()

cards = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
one_deck = 4 * cards
decks = 4
game_deck = copy.deepcopy(decks * one_deck)

WIDTH = 600
HEIGHT = 900

screen = pygame.display.set_mode([WIDTH,HEIGHT])
pygame.display.set_caption("Python Blackjack Game!")
fps = 90
timer = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf',45)
smaller_font = pygame.font.Font('freesansbold.ttf',35)
active = False
hand_active = False

# win, loss, draw/push
records = [0, 0, 0]
player_score = 0
dealer_score = 0
initial_deal = False
my_hand = []
dealer_hand = []
outcome = 0
reveal_dealer = False
add_score = False
results = ['', 'PLAYER BUSTED', 'PLAYER WINS', 'DEALER WINS', 'TIE GAME']

def randomSuit(suit_list):
    a = random.randint(0, len(suit_list) - 1)
    return a

#deal cards by selecting randomly from deck, and make function for once card at a time
def deal_cards(current_hand, current_deck):
    card = random.randint(0, len(current_deck))
    current_hand.append(current_deck[card - 1])
    current_deck.pop(card - 1)
    return current_hand, current_deck

#draw scores for player and dealer on screen
def draw_scores(player, dealer):
    screen.blit(font.render(f'Score: {player}', True, 'black'), (350, 400))
    if reveal_dealer:
        screen.blit(font.render(f'Score: {dealer}', True, 'black'), (350, 100))

#draw cards visually on screen
def draw_cards(player, dealer, reveal):

    for i in range(len(player)):
        pygame.draw.rect(screen, 'white', [70 + (70 *i), 460 + (5*i), 120, 220], 0 ,5)
        screen.blit(font.render(player[i], True, 'black'), (75+70*i, 465 + 5*i))
        screen.blit(font.render(player[i], True, 'black'), (75 + 70 * i, 635 + 5 * i))
        pygame.draw.rect(screen, 'black', [70 + (70 * i), 460 + (5 * i), 120, 220], 5, 5)

    for i in range(len(dealer)):

        pygame.draw.rect(screen, 'white', [70 + (70 * i), 160 + (5 * i), 120, 220], 0, 5)
        if i != 0 or reveal:
            screen.blit(font.render(dealer[i], True, 'black'), (75 + 70 * i, 165 + 5 * i))
            screen.blit(font.render(dealer[i], True, 'black'), (75 + 70 * i, 335 + 5 * i))
        else:
            screen.blit(font.render('???', True, 'black'), (75 + 70 * i, 165 + 5 * i))
            screen.blit(font.render('???', True, 'black'), (75 + 70 * i, 335 + 5 * i))
        pygame.draw.rect(screen, 'black', [70 + (70 * i), 160 + (5 * i), 120, 220], 5, 5)

#pass in player or dealer hand and get best score possible
def calculate_score(hand):
    #calculate hand score fresh everytime, check how many aces we have
    hand_score = 0
    aces_count = hand.count('A')
    for i in range(len(hand)):
        # for 2, 3, 4, 5, 6, 7, 8, 9 - just add the number to total
        for j in range (8):
            if hand[i] == cards[j]:
                hand_score += int(hand[i])
        if hand[i] in ['10','J','Q', 'K']:
            hand_score += 10
        #for aces start adding 11, we'll check if we need to reduce afterward
        elif hand[i] == 'A':
            hand_score += 11
    if hand_score > 21 and aces_count > 0:
        for i in range(aces_count):
            if hand_score > 21:
                hand_score -= 10
    return hand_score

#Drawing game conditions and buttons
def draw_game(act, record, result):
    button_list = []
    if not act:
        deal = pygame.draw.rect(screen, 'white', [150, 20, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [150, 20, 300, 100], 3, 5)
        deal_text = font.render('DEAL HAND', True, 'black')
        screen.blit(deal_text, (165, 50))
        button_list.append(deal)
        # once game started, shot hit and stand buttons and win/loss records
    else:
        #Hit button display
        hit = pygame.draw.rect(screen, 'black', [0, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [0, 700, 300, 100], 3, 5)
        hit_text = font.render('HIT ME', True, 'white')
        screen.blit(hit_text, (55, 735))
        button_list.append(hit)

        #Stand button display
        stand = pygame.draw.rect(screen, 'black', [300, 700, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [300, 700, 300, 100], 3, 5)
        stand_text = font.render('STAND', True, 'white')
        screen.blit(stand_text, (355, 735))
        button_list.append(stand)

        #Bottom text that displays score
        score_text = smaller_font.render(f'Wins: {record[0]}   Losses: {record[1]}   Draws: {record[2]}', True, 'white')
        screen.blit(score_text, (15, 840))
    #if there is an outcome for the hand that was played, display a restart button and tell user what happened
    if result != 0:
        screen.blit(font.render(results[result], True, 'black'), (15, 25))
        deal = pygame.draw.rect(screen, 'white', [150, 220, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'green', [150, 220, 300, 100], 3, 5)
        pygame.draw.rect(screen, 'black', [150, 223, 294, 94], 3, 5)
        deal_text = font.render('NEW HAND', True, 'black')
        screen.blit(deal_text, (165, 250))
        button_list.append(deal)
    return button_list

#check endgame conditions function
def check_endgame(hand_act, deal_score, play_score, result, totals, add):
    #check end game scenarios is player has stood, busted, or blackjacked
    #result would 1 - bust, 2 - win, 3 - loss, 4 - push
    if not hand_act and deal_score >= 17:
        if play_score > 21:
            result = 1
        elif deal_score < player_score <= 21 or deal_score > 21:
            result = 2
        elif play_score < deal_score <= 21:
            result = 3
        else:
            result = 4
        if add:
            if result == 1 or result == 3:
                totals[1] += 1
            elif result == 2:
                totals[0] += 1
            else:
                totals[2] += 1
            add = False
    return result, totals, add

run = True
while run:
    timer.tick(fps)
    screen.fill('grey')
    #initiate deal to player and dealer
    if initial_deal:
        for i in range(2):
            my_hand, game_deck = deal_cards(my_hand, game_deck)
            dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        initial_deal = False

    if active:
        player_score = calculate_score(my_hand)
        draw_cards(my_hand, dealer_hand, reveal_dealer)
        if reveal_dealer:
            dealer_score = calculate_score(dealer_hand)
            if dealer_score < 17:
                dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        draw_scores(player_score, dealer_score)
    #once game is activate and dealt, it will calculate scores and display cards
    buttons = draw_game(active, records, outcome)

    #event handling when the user wants to quit the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONUP:
            if not active:
                if buttons[0].collidepoint(event.pos):
                    active = True
                    initial_deal = True
                    game_deck = copy.deepcopy(decks * one_deck)
                    my_hand = []
                    dealer_hand = []
                    outcome = 0
                    hand_active = True
                    reveal_dealer = False
                    add_score = True
            else:
                #draws cards when clicked on hit
                if buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
                    my_hand, game_deck = deal_cards(my_hand, game_deck)
                #ends turn and reveals dealer's cards
                elif buttons[1].collidepoint(event.pos) and not reveal_dealer:
                    reveal_dealer = True
                    hand_active = False
                elif len(buttons) == 3:
                    if buttons[2].collidepoint(event.pos):
                        active = True
                        initial_deal = True
                        game_deck = copy.deepcopy(decks * one_deck)
                        my_hand = []
                        dealer_hand = []
                        outcome = 0
                        hand_active = True
                        reveal_dealer = False
                        add_score = True

                        dealer_score = 0
                        player_score = 0

    if hand_active and player_score >= 21:
        hand_active = False
        reveal_dealer = True

    outcome, records, add_score = check_endgame(hand_active, dealer_score, player_score, outcome, records, add_score)

    pygame.display.flip()
pygame.quit()