import pygame
import sys
import os
import socket
import errno
import threading


# Socket Stuff
HEADERSIZE = 10


# Setup Window ------------------------------------------------ #
pygame.init()
SIZE = WIDTH, HEIGHT = 800, 450
LEFT_SPACE = int(WIDTH*0.05)

FPS = 60
main_clock = pygame.time.Clock()

WINDOW = pygame.display.set_mode((SIZE))
CHAT_WINDOW = pygame.Surface((int(WIDTH*0.7), int(HEIGHT*0.65)))
USER_WINDOW = pygame.Surface((int(WIDTH*0.175), int(HEIGHT*0.65)))
pygame.display.set_caption('Chat')

#IMG = pygame.image.load(os.path.join('assets', 'IMG.png'))
MENU_FONT = pygame.font.SysFont('Matura MT Script Capitals',
                                min(60, int((HEIGHT/450)*60)), 1)
CHAT_FONT = pygame.font.SysFont('Matura MT Script Capitals',
                                min(25, int((HEIGHT/450)*25)), 1)


class Button():
    def __init__(self, window, msg, font, x, y, w, h, ac, ic):
        self.window = window
        self.msg = msg
        self.default_msg = msg
        self.font = font
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.ac = ac
        self.ic = ic


    def check(self):
        mouse = pygame.mouse.get_pos()
        
        return self.x <= mouse[0] <= self.x + self.w\
               and self.y <= mouse[1] <= self.y + self.h

    
    def render_font(self, align):
        self.label = self.font.render(self.msg, 1, (25,25,25))
        self.label_rect = self.label.get_rect()
        if not align:
            self.label_rect.center = ((self.x+(self.w//2)),
                                      (self.y+(self.h//2)))
        if align == 'left':
            self.label_rect.midleft = (self.x+int(self.w*0.01),
                                      (self.y+(self.h//2)))

        self.window.blit(self.label, self.label_rect)


    def draw(self, align=None):
        if self.check():
            pygame.draw.rect(self.window, self.ac, self.rect)
        else:
            pygame.draw.rect(self.window, self.ic, self.rect)

        self.render_font(align)
        

    def draw_clicked(self, align=None):
        pygame.draw.rect(self.window, self.ac,
                         (self.x, self.y, self.w, self.h))
        
        self.render_font(align)
    

    def is_clicked(self, action=None, args=None):
        if self.check():
            if args:
                action(*args)
            else:
                action()
            return True


def draw_chat_window(chat_history):
    CHAT_WINDOW.fill((240,240,240))
    for i, line in enumerate(chat_history):
        chat_line = CHAT_FONT.render(line, True, (25,25,25))
        chat_line_rect = chat_line.get_rect()
        CHAT_WINDOW.blit(chat_line,
                         ( int(CHAT_WINDOW.get_width()*0.01),
                           int(HEIGHT*0.65-(chat_line_rect[3]+HEIGHT*0.01)*(len(chat_history)-i))
                           )
                         )


def draw_user_window(usernames):
    USER_WINDOW.fill((240,240,240))
    usernames = usernames.split(',')
    for i, user in enumerate(usernames):
        user_line = CHAT_FONT.render(user, True, (25,25,25))
        user_line_rect = user_line.get_rect()
        USER_WINDOW.blit(user_line,
                         ( int(USER_WINDOW.get_width()*0.01),
                           int(HEIGHT*0.01+(user_line_rect[3]+HEIGHT*0.01)*i)
                           )
                         )
    

def draw_main_window(message_button, username):
    WINDOW.fill((25,25,25))
    WINDOW.blit(CHAT_WINDOW, (LEFT_SPACE, int(HEIGHT*0.1)))
    WINDOW.blit(USER_WINDOW, (LEFT_SPACE+CHAT_WINDOW.get_width()+int(LEFT_SPACE/2),
                              int(HEIGHT*0.1)))
    
    message_button.draw('left')
    username_label = CHAT_FONT.render(f'You are connected as: {username}', 1, (255, 180, 80))
    WINDOW.blit(username_label, (LEFT_SPACE, int(HEIGHT*.9)))

    pygame.display.update()
    

def typing(button, message='', align=None, limit=280):
    typing = True
    
    while typing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        typing = False
                        break
                    elif event.key == pygame.K_RETURN:
                        typing = False
                        if message:
                            button.msg = message
                        else:
                            button.msg = button.default_msg
                        break
                    elif event.key == pygame.K_BACKSPACE:
                        message = message[:-1]
                    elif len(message) < limit:
                        message += event.unicode

            button.msg = message + '_'
            button.draw_clicked(align)
            pygame.display.update(button.rect)
            

def connect_to_chat(username, ip, port): #button.msg x 3
    print('Connecting...')
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((ip, int(port)))
        client_socket.setblocking(False) # .recv won't be blocking
        
        username_header = f'{len(username):<{HEADERSIZE}}'.encode('utf-8')
        client_socket.send(username_header + username.encode('utf-8'))
        
        print('Successfully Connected...')
        
    except Exception as e:
        print('Connection failed!')
        print(e)
        return None

    chat(client_socket, username)


def menu():
    username_button = Button(WINDOW,
                             'Enter Name',
                             MENU_FONT,
                             LEFT_SPACE, int(HEIGHT*.1),
                             WIDTH-LEFT_SPACE*2, int(HEIGHT*.15),
                             (180,180,180),(240,240,240),
                             )

    ip_button = Button(WINDOW,
                       socket.gethostname(),
                       MENU_FONT,
                       LEFT_SPACE,int(HEIGHT*.46),
                       WIDTH-LEFT_SPACE*2,int(HEIGHT*.1),
                       (180,180,180),(240,240,240),
                       )

    port_button = Button(WINDOW,
                         '1234',
                         MENU_FONT,
                         LEFT_SPACE,int(HEIGHT*.6),
                         WIDTH-LEFT_SPACE*2,int(HEIGHT*.1),
                         (180,180,180),(240,240,240),
                         )

    connect_button = Button(WINDOW,
                            'connect',
                            MENU_FONT,
                            LEFT_SPACE*2,int(HEIGHT*.8),
                            WIDTH-LEFT_SPACE*4,int(HEIGHT*.1),
                            (180,180,180),(240,240,240),
                            )

    # Loop -------------------------------------------------------- #
    while True:

        # Background ---------------------------------------------- #
        WINDOW.fill((25,25,25))
        connection_label = MENU_FONT.render('Connect to Server', 1, (255, 180, 80))
        connection_label_rect = connection_label.get_rect()
        connection_label_rect.center = (int(WIDTH*.5), int(HEIGHT*.35))
        WINDOW.blit(connection_label, connection_label_rect)
        
        
        # Buttons n stuff ----------------------------------------- #
        username_button.draw()
        ip_button.draw()
        port_button.draw()
        connect_button.draw()

        # Events n stuff ------------------------------------------ #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN: # event has no key attribute
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    username_button.is_clicked(action=typing, args=(username_button,
                                                                    '', None, 14))
                    
                    ip_button.is_clicked(action=typing, args=(ip_button,
                                                              '', None, 12))
                    
                    port_button.is_clicked(action=typing, args=(port_button,
                                                                '', None, 6))
                    
                    connect_button.is_clicked(action=connect_to_chat, args=(username_button.msg,
                                                                            ip_button.msg,
                                                                            port_button.msg))
        
        # Update window ------------------------------------------- #
        pygame.display.update()
        main_clock.tick(FPS)


def chat(client_socket, username):
    chat_history = []
    usernames = ''    
    message_button = Button(WINDOW,
                            '>',
                            CHAT_FONT,
                            LEFT_SPACE,int(HEIGHT*.8),WIDTH-LEFT_SPACE*2,20,
                            (240,240,240),(240,240,240),
                            )
    
    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN: # event has no key attribute
                if event.key == pygame.K_ESCAPE:
                    run = False
                    client_socket.close()

                # Type and send message
                if event.key ==  pygame.K_BACKSPACE:
                    if len(message_button.msg) > 1:
                        message_button.msg = message_button.msg[:-1]
            
                elif event.key ==  pygame.K_RETURN:
                    ''' send things to yourself to be available on server side'''
                    if message_button.msg != '>':
                        message_button.msg = message_button.msg[1:]
                        message = message_button.msg.encode('utf-8')
                        message_header = f'{len(message):<{HEADERSIZE}}'.encode('utf-8')
                        client_socket.send(message_header + message)
                        # also locally append to chat history
                        print(f'{username} > {message_button.msg}')
                        chat_history.append(f'{username} > {message_button.msg}')
                        message_button.msg = message_button.default_msg

                else:
                    if len(message_button.msg) < 35:
                        message_button.msg += event.unicode
                    

        if run:            
            try:
                ''' receive things from server (weitergeleitet von anderen clients) '''
                # other clients (on server) or server send to user
                message_header = client_socket.recv(HEADERSIZE)
                if not message_header:
                    print('Connection closed by the server')
                    run = False
                    break

                message_length = int(message_header.decode('utf-8').strip())
                sender = client_socket.recv(message_length).decode('utf-8')
                
                message_header = client_socket.recv(HEADERSIZE)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                if message.startswith('USERDISCONNECTED'):
                    chat_history.append(f'{sender} disconnected')
                    usernames = message[16:]
                elif message.startswith('USERCONNECTED'):
                    if sender == username:
                        pass
                    else:
                        chat_history.append(f'{sender} connected')
                    usernames = message[13:]
                else:
                    print(f'{sender} > {message}')
                    chat_history.append(f'{sender} > {message}')
                    

                    
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    # above errors: when there are no more messages to receive
                    # if not one of these:
                    print('Reading Error', str(e))
                    sys.exit()

                    
            except Exception as e:
                print('General Error', str(e))
                sys.exit()

        # Draw Stuff        
        # draw user window
        draw_chat_window(chat_history)
        draw_user_window(usernames)
        draw_main_window(message_button, username)
        
        main_clock.tick(FPS)

    
menu()
    
# Close Pygame ------------------------------------------------ #
pygame.quit()
sys.exit()
