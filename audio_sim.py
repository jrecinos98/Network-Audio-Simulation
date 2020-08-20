import sunau
import random

#Prob =probability of packet getting lost
#returns true if the random number is > prob. False otherwise
def is_packet_lost(prob):
	if(prob > random.uniform(0,1)):
		return True
	return False


def open_audio(name, mode):
	try:
		file= sunau.open(name, mode)
		return file
	except sunau.Error:
		print("Error opening file")
		return None

def init_writer(name):
	writer= sunau.open(name, 'w')
	return writer

def write(writer, reader, frames):
	#Each frame is 2 byte
	packet = reader.readframes(frames)
	writer.writeframesraw(packet)
	return packet

#Works correclty
def silence(frame, reader, writer, packet= None):
	new_packet= ('\x00\x00'*frame*reader.getnchannels()).encode()
	write_data(writer, reader, frame, new_packet)

#Appears to work correctly
def previous_packet(frame, reader, writer, packet):
	write_data(writer,reader,frame, packet)
	
#Works correctly
def previous_sample(frame, reader,writer, packet):
	#I want only the last sample from last packet 
	samples= int(len(packet)/(2*reader.getnchannels()))
	start= (samples-1)*(2*reader.getnchannels())
	newPacket= packet[start:]
	write_data(writer, reader, frame, newPacket*frame)
	
def write_data(writer, reader, packetSize, packet):
	framesize=packetSize
	#When reader has not sent any packets
	if(reader.tell()-framesize < 0):
		#Check that we dont exceed available space
		if (reader.tell()+framesize > reader.getnframes()):
			framesize= reader.getnframes()-reader.tell()
		#Writes and ajusts reader to new position
		new_packet= ('\x00\x00'*framesize*reader.getnchannels()).encode()
		writer.writeframesraw(new_packet)
	#If data has been sent
	else:
		#Check that we dont exceed available space
		if (reader.tell()+framesize > reader.getnframes()):
			framesize= reader.getnframes()-reader.tell()
		#reduce packet size (if needed). 
		#We want the most recent bytes (bytes num starting from the right)
		newPacket= packet[packetSize-framesize:]
		writer.writeframesraw(newPacket)
	reader.setpos(reader.tell()+framesize)
	
	#return newPacket
def EmptyStart(writer, reader, size):
	framesize=size
	if(reader.tell()-framesize < 0):
		#Check that we dont exceed available space
		if (reader.tell()+framesize > reader.getnframes()):
			framesize= reader.getnframes()-reader.tell()
		#Writes and ajusts reader to new position
		new_packet= ('\x00\x00'*framesize*reader.getnchannels()).encode()
		writer.writeframesraw(new_packet)
		reader.setpos(reader.tell()+framesize)


def main():
	writers = {}
	readers = []  
	packet_sizes= [ 50, 150, 500, 3000] #bytes
	loss_rates= [.05, .25, .50, .70]

	policies= {}
	policies["silence"]= silence
	policies["repeat_packet"]= previous_packet
	policies["repeat_sample"]= previous_sample
	readers ={}
	readers["got"] = open_audio("got.au", 'r')
	readers["father"]  = open_audio("father.au",'r')
	
	#Loop through the parameters to make audio files with all parameters
	for reader in readers.keys():
		for i in packet_sizes:
			for j in loss_rates:
				for policy in policies.keys():
					fname= reader+ "_"+str(i)+"_"+str(int(j*100))+"%_"+policy+".au"
					#print("Name: ", fname)
					writer = init_writer(fname)
					#init header of new file
					writer.setparams(readers[reader].getparams())
					size= readers[reader].getnframes()
					written= 0
					missed=0
					sent=0
					lastPacket= None
					while written < size:
						#Determine if packet is lost
						if(is_packet_lost(j)):
							if(lastPacket == None):
								EmptyStart(writer,readers[reader], i)
							else:
								policies[policy](i, readers[reader], writer, lastPacket)
						else:
							lastPacket= write(writer, readers[reader], i)
						sent+=1
						written+=i
					writer.close()
					readers[reader].rewind()
					if(missed != 0):
						print("		Percentage lost: ", str((missed/sent)*100)+"%")
		#print("Finished with File.")
	#Create one with 0% loss 
	for reader in readers.keys():
		fname= reader+"_0%"+".au"		
		writer = init_writer(fname)
		writer.setparams(readers[reader].getparams())
		size= readers[reader].getnframes()
		write(writer, readers[reader], size)
		writer.close()
		readers[reader].rewind()
	
	for i in readers.keys():
		readers[i].close()
	

if __name__=="__main__":
	main()