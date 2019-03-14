import json
import xmltodict
import subprocess
import random
import string
import os
import os.path
import sys

class BlastPlasmid:
	def __init__(self, plasmidSeq):
		self.plasmidSeq = plasmidSeq
		randomFileName = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(10))+".tmp"
		self.fileName = randomFileName
		self.result = None
		self.filePath = os.path.join("/tmp",randomFileName)
		with open(self.filePath, "w") as f:
			f.write(plasmidSeq)
			f.write("\n")

	def blast(self, abiSeq):
		process = subprocess.Popen(('blastn -subject %s -outfmt 5'%self.filePath).split(' '), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
		out = process.communicate(input=abiSeq)[0]
		#debug save xml
		#with open("lastxml.txt","w") as f:
			#f.write(out)
			
		self.result = xmltodict.parse(out)

		#sys.stderr.write(json.dumps(self.result))
		#subprocess.call(['rm',self.filePath])
		return self.result

	def hasHits(self,dct):
		return dct['BlastOutput']['BlastOutput_iterations']['Iteration']['Iteration_hits']!=None

	def getHsp(self, dct):
		hsp = dct['BlastOutput']['BlastOutput_iterations']['Iteration']['Iteration_hits']['Hit']['Hit_hsps']['Hsp']
		return hsp

	def getMatch(self, dct):
		hits = dct['BlastOutput']['BlastOutput_iterations']['Iteration']['Iteration_hits']['Hit']
		#length = hits['Hit_len']
		hsp = hits['Hit_hsps']['Hsp']
		if type(hsp) == list:
			hsp = hsp[0]
		qseq = hsp['Hsp_qseq']
		midline = hsp['Hsp_midline']
		hseq = hsp['Hsp_hseq']
		return {"qseq":qseq,"midline":midline,"hseq":hseq}


	def getOutput(self,dct):
		if self.hasHits(dct):
			hsp = self.getHsp(dct)
			if type(hsp)==list:
				hsp = hsp[0]
				queryFrom = int(hsp['Hsp_query-from'])
				queryTo = int(hsp['Hsp_query-to'])
				hitFrom = int(hsp['Hsp_hit-from'])
				hitTo = int(hsp['Hsp_hit-to'])
			else:
				queryFrom = int(hsp['Hsp_query-from'])
				queryTo = int(hsp['Hsp_query-to'])
				hitFrom = int(hsp['Hsp_hit-from'])
				hitTo = int(hsp['Hsp_hit-to'])


			return {"queryFrom":queryFrom,"queryTo":queryTo,"hitFrom":hitFrom,"hitTo":hitTo,"match":self.getMatch(dct),"message":"OK"}
		else:
			return {"message":"no hits"}

def reverseComplement(src):
	dst = ""
	d = {"A":"T","T":"A","C":"G","G":"C","c":'g','g':'c','a':'t','t':'a'}
	for i in range(len(src)-1,-1,-1):
		if src[i] in d:
			dst+=d[src[i]]
		else:
			dst+=" "
	return dst



def fullAlignment(original,abiSeq,plasmidSeq):
	abiSeq = abiSeq.replace("\n","")
	plasmidSeq = plasmidSeq.replace("\n","")
	if 'queryFrom' in original and 'queryTo' in original:
		if original['queryFrom'] ==1 and original['queryTo']==len(plasmidSeq):
			return original
		else:
			oriQFrom = original['queryFrom']-1
			oriQTo = original['queryTo']
			oriHFrom = original['hitFrom']-1
			oriHTo = original['hitTo']
			add5 = plasmidSeq[:oriQFrom]
			add3 = plasmidSeq[oriQTo:]
			hitFrom = 0
			hitTo = len(plasmidSeq)
			qseq = add5+original['match']['qseq']+add3
			if oriQFrom < oriQTo:
				queryFrom = oriQFrom - len(add5)
				queryTo = oriQTo + len(add3)
				hseq = abiSeq[queryFrom:oriQFrom] + original['match']['hseq'] +abiSeq[oriQTo:queryTo]
			else:
				queryFrom = oriQFrom+ len(add5)
				queryTo = oriQto - len(add3)
				rcAbiSeq = reverseComplement(abiSeq)
				rclen = len(rcAbiSeq)
				hseq = rcAbiSeq[rcLen-queryFrom:rcLen-original['queryFrom']] + original['match']['hseq'] +AbiSeq[rcLen-original['queryTo']:rcLen-queryTo]

			match = ""
			#print oriQFrom
			#print oriQTo
			#print oriHFrom
			#print oriHTo
			#print add5,len(add5)
			#print add3,len(add3)
			#print queryFrom
			#print queryTo
			#print original['queryFrom']
			#print original['queryTo']
			#
			for i in range(len(qseq)):
				if qseq[i] == hseq[i]:
					match+="|"
				else:
					match+=" "

			return {"queryFrom":oriQFrom+1,"queryTo":oriQTo,"hitFrom":oriHFrom+1,"hitTo":oriHTo,"match":{"qseq":qseq,"midline":match,"hseq":hseq},"message":"OK"}
	else:
		return original


if __name__ == "__main__":
	fullAlignmentFlag = False
	if len(sys.argv)>1:
		if sys.argv[1] == '-a':
			fullAlignmentFlag = True
	seq = sys.stdin.readline() #abi
	seq2 = sys.stdin.readline() #original
	b = BlastPlasmid(seq)
	dct = b.blast(seq2)
	output = b.getOutput(dct)
	if fullAlignmentFlag:
		output = fullAlignment(output,seq,seq2)

	sys.stdout.write(json.dumps(output))
else:
	print __name__
