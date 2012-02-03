# respond to a key without the need to press enter
 
from tkinter import *
from tkinter.messagebox import *
 
class LabelTweets(Frame):

	def d_tweet(self, inTweet):
		""" Displays the tweet
		"""
		
		self.tweetText.config(state = "normal")
		self.tweetText.delete(1.0, END)
		self.tweetText.insert(END, inTweet)
		self.tweetText.config(state = "disable")
		self.tweetText.pack()
		
		
	def get_tweet(self):
		""" Retrieve the tweet from the database
		"""
		
		inTweet="fdfdfdff"
		self.d_tweet(inTweet)
		
		
	def deposit_tweet(self, c):
		""" Deposit the tweet to the new table
		"""
		
		if c == 1:
			print ('1')
		elif c == 2:
			print ('2')
		elif c == 3:
			print ('3')
		elif c == 4:
			print ('4')
			
		inTweet="111"
		self.d_tweet(inTweet)

		
	def keypress(self,event):
		""" Execute the corresponding event
		"""
		
		if event.keysym == 'Escape':
			root.destroy()
		x = event.char
		if x == "1":
			self.deposit_tweet(1)
		elif x == "2":
			self.deposit_tweet(2)
		elif x == "3":
			self.deposit_tweet(3)
		elif x == "4":
			self.deposit_tweet(4)
			
			
	def drawGUI(self):
		""" Draw the GUI
		"""
		
		# create the label where we display the tweet
		self.tweetText = Text(self, bd = "2", width = 80, height = 2)
		
		self.get_tweet()
		
		return root;
		
		
	def __init__(self, master = None):
	
		Frame.__init__(self, master)
		self.master.title("LABEL THE TWEETS")
        
        #Create the Intro Text
		introText = StringVar()
		introLabel = Label( root, textvariable = introText, font=("Helvetica", 10, "bold"))
		introText.set("Choices  :  1 - Traffic  ||  2 - Not Traffic  ||  3 - Unclear  ||  4 - Robot   ( ESC to Exit ) \n")
		introLabel.pack()
		
		self.pack()
		self.drawGUI()
		
		self.bind_all('<Key>', self.keypress)
 
 
root = Tk()

app = LabelTweets(root)

app.mainloop()