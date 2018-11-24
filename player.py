# -*-coding: utf-8-*-
# System imports:

import time
import string
from threading import Thread

# Third party imports:
import pygame as pg 
from pygame.locals import *

# Local imports:
from client import SocketClient
from managepackage import ManagePackage

pg.init()						   # Inicializa o pygame
pg.font.init()                     # Inicializa o addon de fontes
sock = SocketClient()			   # Instancia um objeto Socket Cliente
PacketManager = ManagePackage()    # Instancia um gerenciador de pacotes json

SCREEN_SIZE = (758, 590)           # Dimensões da tela
BACKGROUND_COLOR = (255, 255, 255)
CAPTION = "Pong Hau K'i!"
font = pg.font.Font("times.ttf", 16)

# Load images
fullBoard    = pg.image.load("fullBoard.png")
boardUpdate  = pg.image.load("boardUpdate.png")
chatUpdate   = pg.image.load("chatUpdate.png")
msgBoxUpdate = pg.image.load("msgBoxUpdate.png") 
opponentTurn = pg.image.load("opponentTurn.png")
yourTurn     = pg.image.load("yourTurn.png")
purple       = pg.image.load("purple.png")
pink         = pg.image.load("pink.png") 
you_win 	 = pg.image.load("you_win.png")
you_loss 	 = pg.image.load("you_loss.png")
ask_restart  = pg.image.load("ask_restart.png")
ask_surrender  = pg.image.load("ask_surrender.png")
your_color_purple  = pg.image.load("your_color_purple.png")
your_color_pink  = pg.image.load("your_color_pink.png")
#################################################

board = [None] * 5

# Retorna as coordenadas de acordo com o índice da lista
def index_to_coord(index):
	if index == 0:
		return 320, 50

	elif index == 1:
		return 659, 50
	
	elif index == 2:
		return 490, 220
	
	elif index == 3:
		return 320, 387
	
	elif index == 4:
		return 659, 387 

# Renderiza o tabuleiro e as peças
def draw_board(screen):
	
	screen.blit(boardUpdate, (0, 0))

	for index, item in enumerate(board):
		if (item is True and im_player == "1") or (item is False and im_player == "2"):
			screen.blit(purple, (index_to_coord(index)))

		elif (item is False and im_player == "1") or (item is True and im_player == "2"):
			screen.blit(pink, (index_to_coord(index)))
		
		if im_player == "1":
			screen.blit(your_color_purple, (0, 0))
		elif im_player == "2":
			screen.blit(your_color_pink, (0, 0))
	
	pg.display.update()   

# Retorna se a peça é do jogador e o índice da peça na lista
def is_player_piece(mouse_x, mouse_y):
	if mouse_x > 320 and mouse_x < 373 and mouse_y > 50 and mouse_y < 103 and board[1] != None and board[4] != None:
		return board[0], 0

	elif mouse_x > 658 and mouse_x < 712 and mouse_y > 50 and mouse_y < 103 and board[0] != None and board[3] != None:
		return board[1], 1
	
	elif mouse_x > 489 and mouse_x < 543 and mouse_y > 219 and mouse_y < 274:
		return board[2], 2
	
	elif mouse_x > 320 and mouse_x < 373 and mouse_y > 387 and mouse_y < 442 and board[1] != None:
		return board[3], 3

	elif mouse_x > 658 and mouse_x < 712 and mouse_y > 387 and mouse_y < 442 and board[0] != None:
		return board[4], 4
	
	return None, None

# Reorganiza a lista após a jogada
def organize(orig_index):
	global board
	for index, item in enumerate(board):
		if board[index] is None:
			board[index] = True
			board[orig_index] = None 

# Espelha o tabuleiro (os jogadores se veem sendo as peças roxas e o oponente rosa)
def invert_board():
	global board

	for index, piece in enumerate(board):
		if piece is True:
			board[index] = False

		elif piece is False:
			board[index] = True

def show_chat_window():
	global chat_queue
	
	if len(chat_queue) == 23: # Se a caixa de mensagens estiver cheia	
		chat_queue.pop(0)	  # Remove a primeira mensagem da lista
	
	pos_y = 48
	screen.blit(chatUpdate, (0, 0))
	for msg in chat_queue:
		if msg[1] == "1":
			color = 143, 0, 255
		
		elif msg[1] == "2":
			color = 255, 0, 204

		screen.blit(font.render(msg, 1, (color)), (32, pos_y))
		pos_y += 17 													

	pg.display.update()

def write_in_chat(event, screen):
	global current_string
	global chat 
	global chat_queue

	if event.key == K_BACKSPACE:
		current_string = current_string[0:-1]	  # A tecla backspace apaga uma letra.

	elif event.key == K_RETURN:		         	  # Tecla para enviar mensagem no chat (Enter)
		if im_player == "1":
			chat = "P1: " + chat

		elif im_player == "2":
			chat = "P2: " + chat

		sock.send(chat)					 	 	  # Envia a mensagem para o outro jogador
		chat_queue.append(chat)				 	  # Insere nova mensagem na lista do chat
		current_string = []					 	  # Esvazia o buffer da mensagem digitada
		show_chat_window()						  # Atualiza o chat

	elif event.key <= 255:						  # Aceita letras no padrão ASCII
		if len(current_string) < 32:		 	  # Limita a caixa de digitação em 28 caracteres 		
			current_string.append(chr(event.key)) # Armazena cada tecla digitada para formar a mensagem. Ex: (["o"], ["l"], "[a]")

	chat = string.join(current_string, "")		  # Junta as letras digitadas em uma string só. Ex: ("ola")
	screen.blit(msgBoxUpdate, (0, 0))			  # Desenha a caixa de entrada de texto
	screen.blit(font.render(chat, 1, (255, 255, 255)), (51, 447))  # Desenha a palavra digitada
	pg.display.update()											   # Renderiza a tela

def end_game():
	global victory
	# [False, x, True, False, True] or
	# [x, False, True, True, False]
	if ((board[0] == False and board[2] == True and board[3] == False and board[4] == True) or
	    (board[1] == False and board[2] == True and board[3] == True and board[4] == False)):
		victory = True 
		animate_win_loss()

	# [True, x, False, True, False] or
	# [x, True, False, False, True]
	elif ((board[0] == True and board[2] == False and board[3] == True and board[4] == False) or 
	      (board[1] == True and board[2] == False and board[3] == False and board[4] == True)):
		victory = False 
		animate_win_loss()

def animate_win_loss():
	draw_board(screen)
	if victory is True:
		screen.blit(you_win, (0, 0))

	elif victory is False:
		screen.blit(you_loss, (0, 0))
	pg.display.update()

#****************************************************************************************
# Codifica o tabuleiro em um json e envia pro servidor
def pack_and_send():
	packet = PacketManager.pack_json(board)
	sock.send(packet)

# Recebe pacotes json e decodifica 
def receive_pack():
	packet = sock.receive()
	dictionary = PacketManager.unpack_json(packet)
	return dictionary

def ask_for_surrender_or_restart(x, y):
	if x > 24 and x < 277 and y > 480 and y < 525: 		   
		sock.send("<]r")	   # Envia o pedido de reinício para o servidor

	elif x > 24 and x < 277 and y > 535 and y < 580:	  
		sock.send("<]d") 	   # Envia o pedido de desistência para o servidor

def will_accept_ask():
	global opponent_ask_surrender
	global opponent_ask_restart
	global victory
	global board

	decide = False
	accepted_resquest = False

	if opponent_ask_restart:
		answer = "<]ar"
		notify = ask_restart
	
	elif opponent_ask_surrender:
		answer = "<]ad"
		notify = ask_surrender

	screen.blit(notify, (0, 0))
	pg.display.update()

	while not decide:
		for event in pg.event.get():
			if event.type == pg.MOUSEBUTTONDOWN:
				x, y = pg.mouse.get_pos()
				
				if x > 552 and x < 749 and y > 530 and y < 582:
					sock.send(answer)
					accepted_resquest = True

				decide = True
			
			elif event.type == QUIT: # Fechar o jogo
				sock.send("<]f")     # Notifica o servidor que o jogador saiu
				return

	opponent_ask_restart   = False 
	opponent_ask_surrender = False

	# Se aceitar o pedido de desistência
	if accepted_resquest and answer == "<]ad":
		victory = True
		animate_win_loss()

	# Se aceitar o pedido de reinício
	elif accepted_resquest and answer == "<]ar":
		if im_player == "1":
			board = [True, True, None, False, False]
		elif im_player == "2":
			board = [False, False, None, True, True]
		draw_board(screen)

		if vez:
			screen.blit(yourTurn, (0, 0))
		elif not vez:
			screen.blit(opponentTurn, (0, 0))
		pg.display.update()

	else:
		draw_board(screen)  # Renderiza o tabuleiro
		if vez:
			screen.blit(yourTurn, (0, 0))
		elif not vez: 
			screen.blit(opponentTurn, (0, 0))
		pg.display.update()

def receive_packet():
	global vez
	global opponent_ask_surrender
	global opponent_ask_restart
	global board
	global chat_queue
	global victory
	
	while True:

		msg = sock.receive()    # Aguarda receber mensagens do servidor
		
		if msg == "<]v":
			sock.send("<]ok")		   # Responde ao servidor que recebeu a vez
			board = receive_pack()
			sock.send("<]ok")	               # Responde ao servidor que recebeu o tabuleiro
			invert_board()                     # Atualiza a lista do tabuleiro		
			vez = True

		elif msg[:2] != "<]":                  # Mensagem do chat
			chat_queue.append(msg)			   # Armazena a mensagem no array de mensagens
			show_chat_window()

		elif msg == "<]r":				       
			opponent_ask_restart = True		   # Recebe pedido de reinício

		elif msg == "<]d":				   
			opponent_ask_surrender = True	   # Recebe pedido de desistência

		elif msg == "<]ar":	                   # Recebe resposta a pedido de reinício    			   
			if im_player == "1":
				board = [True, True, None, False, False]
			elif im_player == "2":
				board = [False, False, None, True, True]
			draw_board(screen)

			if vez:
				screen.blit(yourTurn, (0, 0))
			elif not vez:
				screen.blit(opponentTurn, (0, 0))
			pg.display.update()
			
		elif msg == "<]ad":			   		   # Recebe resposta a pedido de desistência 
			victory = False
			animate_win_loss()
		
		elif msg == "<]f":					   # Servidor avisa que o oponente desconectou
			victory = True # Vitória
			animate_win_loss()
			
def main():
	
	global screen
	global vez	
	global opponent_ask_restart
	global opponent_ask_surrender
	global pack
	global chat
	global chat_queue
	global current_string
	global board
	global victory 
	global im_player

	screen = pg.display.set_mode(SCREEN_SIZE)		# Window instance
	screen.fill(BACKGROUND_COLOR)				    # Background color
	pg.display.set_caption(CAPTION)					# Window title

	vez                    = False   # Vez do jogador                     
	end                    = False   # Fim do jogo
	opponent_ask_surrender = False	 # Oponente pediu para desistir
	opponent_ask_restart   = False   # Oponente pediu para reiniciar
	pack                   = " "     # Armazena o pacote do tabuleiro enviado pelo oponente
	victory 			   = None	 # Condição de vitória
	im_player			   = None  	 # O jogador é o player1 ou player2

	current_string = []  		     # Armazena as letras em uma lista para formar a mensagem 
	chat           = ""	             # Concatena a mensagem que será enviada no chat utilizando a lista acima
	chat_queue     = []  		     # Armazena as mensagens da janela do chat

	##############################################################################
	board = receive_pack()           # Aguarda o servidor enviar o tabuleiro

	if board[0] == True:
		im_player = "1"
	
	elif board[0] == False:
		im_player = "2"

	screen.blit(fullBoard, (0, 0))   # Desenha o background completo
	draw_board(screen)               # Renderiza o tabuleiro
	
	if board[0] is True:
		vez = True
	elif board[0] is False:
		screen.blit(opponentTurn, (0, 0))

	pg.display.update()
	##############################################################################

	receive = Thread(target = receive_packet)	   # Thread que gerencia os pacotes recebidos
	receive.daemon = True					  	   # A flag daemon faz a thread encerrar quando o fluxo principal encerra
	receive.start()								   # Inicia a thread

	while not end:      # Enquanto o jogo não acabar
		while vez is False:  # Enquanto não for a vez do jogador
			
			if opponent_ask_restart or opponent_ask_surrender:
				will_accept_ask()

			for event in pg.event.get():		      # Checa eventos do pygame
				if event.type == KEYDOWN:		      # Se o evento for uma tecla pressionada
					write_in_chat(event, screen)      # Chama a função para escrever no chat

				elif event.type == pg.MOUSEBUTTONDOWN:
					x, y = pg.mouse.get_pos() 
					ask_for_surrender_or_restart(x, y)     # Jogador pode pedir para desistir ou reiniciar

				elif event.type == QUIT:  # Clicar no x da janela fecha o jogo
					sock.send("<]f")      # Notifica o servidor de que o jogo foi fechado
					return

		if vez:	   # Se for a vez do jogador
			# Colocar a condição de derrota aqui
			draw_board(screen)  # Renderiza o tabuleiro
			screen.blit(yourTurn, (0, 0))
			pg.display.update()

		while vez:
			end_game()

			if opponent_ask_restart or opponent_ask_surrender:
				will_accept_ask()

			for event in pg.event.get():
				if event.type == KEYDOWN:		    # Se o evento for uma tecla pressionada
					write_in_chat(event, screen)    # Chama a função para escrever no chat

				elif event.type == pg.MOUSEBUTTONDOWN:
					x, y = pg.mouse.get_pos() 
					ask_for_surrender_or_restart(x, y)     # Jogador pode pedir para desistir ou reiniciar
					
					piece, index = is_player_piece(x, y)

					if piece is True:  # Se onde clicou é uma peça
						organize(index)
						draw_board(screen)  # Renderiza o tabuleiro
						screen.blit(opponentTurn, (0, 0))
						pg.display.update()
						
						end_game()
						# Colocar a condição de vitória aqui
						pack_and_send()	# Envia o tabuleiro atualizado pro servidor
						vez = False     # Finaliza a jogada
						
				elif event.type == QUIT: # Fechar o jogo
					sock.send("<]f")     # Notifica o servidor que o jogador saiu
					return

if __name__ == "__main__":
	main()