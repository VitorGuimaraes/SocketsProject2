# -*-coding: utf-8-*-

from socket import *
from threading import Thread
import time
from server import SocketServer
from managepackage import ManagePackage

BUFFER = 2048 # Tamanho máximo do pacote
PacketManager = ManagePackage()    # Instancia um gerenciador de pacotes json

def packer(data):
	packet = PacketManager.pack_json(data)
	return packet

def main():
	sock = SocketServer()	# Instancia um objeto socket
	sock.listen(2)			# Servidor está escutando e aceita até duas conexões

	player1_container = " " # Inicia o pacote como vazio	
	player2_container = " "	# Inicia o pacote como vazio

	for i in range(0, 2):	# Aguarda os dois jogadores se conectarem
		print "Aguardando jogador " + str(i+1) + " se conectar..."
		sock.conn[i], sock.addr[i] = sock.sock.accept()
		print "Cliente " + str(sock.addr[i]) + " conectado com sucesso!\n"

	sock.conn[0].send(packer([True, True, None, False, False]))
	sock.conn[1].send(packer([False, False, None, True, True]))

	def run_player1():		
		global player1_container  
		global player2_container 

		player1_container = ""
		player2_container = ""

		while True:
			packet = sock.conn[0].recv(BUFFER)
			print("player1: " + str(packet))
			
			if len(packet) == 32:	# É o tabuleiro!
				sock.conn[1].send("<]v") 
				player1_container = packet
				
			elif packet[:2] == "<]": # Protocolo de confirmação de recebimento
				if len(player2_container) == 32:
					sock.conn[0].send(player2_container)
					player2_container = " "

				elif packet == "<]r":
					sock.conn[1].send("<]r") 		# Pedido de reinício

				elif packet == "<]d":
					sock.conn[1].send("<]d") 		# Pedido de desistência

				elif packet == "<]ar":
					sock.conn[1].send("<]ar")  		# Resposta ao pedido de reinício

				elif packet == "<]ad":
					sock.conn[1].send("<]ad") 		# Resposta ao pedido de desistência

				elif packet == "<]f":
					sock.conn[1].send("<]f") 	    # O jogo foi fechado

			elif packet[:2] != "<]":				# Mensagem do chat
				sock.conn[1].send(packet)

			# "Esvazia" o pacote, senão quando voltar pro início do while vai considerar que uma mensagem chegou
			packet = "<]"	

	def run_player2():
		global player1_container
		global player2_container
		
		player1_container = ""
		player2_container = ""

		while True:
			packet = sock.conn[1].recv(BUFFER)
			print("player2: " + str(packet))

			if len(packet) == 32:	# É o tabuleiro!
				sock.conn[0].send("<]v") # Notifica o oponente que é a vez dele
				player2_container = packet

			elif packet[:2] == "<]": # Protocolo de confirmação de recebimento
				if len(player1_container) == 32:
					sock.conn[1].send(player1_container) #Envia o tabuleiro pro oponente
					player1_container = " "

				elif packet == "<]r":
					sock.conn[0].send("<]r") 		# É pedido de restart

				elif packet == "<]d":
					sock.conn[0].send("<]d") 		# É pedido de surrender

				elif packet == "<]ar":
					sock.conn[0].send("<]ar") 		# É resposta de restart

				elif packet == "<]ad":
					sock.conn[0].send("<]ad") 		# É resposta de surrender

				elif packet == "<]f":
					sock.conn[0].send("<]f") 	    # O jogador fechou o jogo

			elif packet[:2] != "<]":				# É mensagem do chat
				sock.conn[0].send(packet)

			# Reseta o pacote, senão quando voltar pro início do while vai considerar que uma mensagem chegou
			packet = "<]"	 

	player1 = Thread(target = run_player1)
	player2 = Thread(target = run_player2)

	player1.start()
	player2.start()

if __name__ == "__main__":
	main()