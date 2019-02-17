from scene import *
from sound import load_effect, play_effect
import time
import shelve

# menu buttons on starting modes

class Main(Scene):
	def setup(self):
		self.loaded = False
		
		with shelve.open('100TapsSave') as save:
			if 'Highscores' not in save:
				save['Highscores'] = {'Classic': None, 'Timed': 0, 'Speed': 0}
				
			self.highscores = save['Highscores']
		
		self.startTime = 0
		self.taps = 0
		self.state = 'Menu'
		self.click_sound = ''
		load_effect(self.click_sound)
		self.loaded = True
		
		self.ipad = self.size.w > 400
		
		self.f = 'Arial'
		self.s = 40
		
		self.titleF = 'Futura'
		self.titleS = 50
		
		self.smallS = 30
		
		if self.ipad:
			self.s *= 1.5
			self.titleS *= 1.5
			self.smallS *= 1.5
		
	def draw(self):
		w = self.size.w
		h = self.size.h
		if not self.loaded:
			return
			
		background(0, 0, 0)
		
		if self.state == 'Menu':
			text('100 Taps', self.titleF, self.titleS, w * 0.5, h * 0.9)
			text('Classic', self.titleF, self.s, w * 0.5, h * 0.63)
			text('Timed', self.titleF, self.s, w * 0.5, h * 0.5)
			text('Highscores', self.titleF, self.s, w * 0.5, h * 0.37)
			
		if self.state.startswith('Starting'):
			text('Tap to begin!', self.titleF, self.s, w * 0.5, h * 0.5)
			text(self.state[9:] + ' Mode', self.titleF, self.titleS, w * 0.5, h - 10, alignment=2)
			text('Menu', self.f, self.smallS, w - 5, 5, alignment=7)
			
		if self.state in ['Classic', 'Timed']:
			e = time.time() - self.startTime
			self.speed = self.taps / e
			text(str(self.taps), self.titleF, 200, w * 0.5, h * 0.5)
			text('Speed: ' + str('%0.2f' % self.speed) + ' tp/s', self.f, self.s, w * 0.5, 5, alignment=8)
			text('Time: ' + self.formatTime(e if self.state == 'Classic' else 15 - e), self.f, self.s, w * 0.5, h - 5, alignment=2)
			
			if self.state == 'Timed' and e >= 15:
				self.state = 'Timed Win'
				self.speed = self.taps / 15
				
		if self.state.endswith('Win'):
			background(0, 0, 0)
			if self.state == 'Classic Win':
				newHighscore = self.highscores['Classic'] is None or self.time < self.highscores['Classic']
				scoreMessage = 'Time: ' + self.formatTime(self.time)
			else:
				newHighscore = self.highscores['Timed'] is None or self.taps > self.highscores['Timed']
				scoreMessage = 'Taps: %s' % self.taps
				
			text('New Highscore!' if newHighscore else 'You Win!', self.titleF, self.titleS, w * 0.5, h * 0.9)
			text('Average Speed: ', self.f, self.s, w * 0.5, h * 0.7)
			text(str('%0.4f' % (self.speed)) + ' tp/s', self.f, self.s, w * 0.5, h * 0.63)
			text(scoreMessage, self.f, self.s, w * 0.5, h * 0.3)
			text('Continue', self.f, self.smallS, w - 5, 5, alignment=7)
		
		if self.state == 'Highscores':
			text('Highscores', self.titleF, self.titleS, w * 0.5, h * 0.9)
			text('Classic:', self.f, self.s, w * 0.5, h * 0.7)
			text(self.formatTime(self.highscores['Classic']), self.f, self.smallS, w * 0.5, h * 0.63)
			text('Timed:', self.f, self.s, w * 0.5, h * 0.5)
			text(str(self.highscores['Timed']) + ' taps', self.f, self.smallS, w * 0.5, h * 0.43)
			text('Highest Speed:', self.f, self.s, w * 0.5, h * 0.3)
			text(str('%0.2f' % (self.highscores['Speed'])) + ' tp/s', self.f, self.smallS, w * 0.5, h * 0.23)
			text('Menu', self.f, self.smallS, w - 5, 5, alignment=7)
			
	def touch_began(self, touch):
		play_effect(self.click_sound)
		w = self.size.w
		h = self.size.h
		l = touch.location
		
		def touchingText(x, y, width, height):
			if self.ipad:
				width *= 1.5
				height *= 1.5
			return l in Rect(w * x - width / 2, h * y - height / 2, width, height)
		
		if self.state == 'Menu':
			if touchingText(0.5, 0.63, 100, 60):
				self.state = 'Starting Classic'
				
			if touchingText(0.5, 0.5, 100, 60):
				self.state = 'Starting Timed'
				
			if touchingText(0.5, 0.37, 100, 60):
				self.state = 'Highscores'
		
		elif self.state.startswith('Starting'):
			if touchingText(0.85, 0.05, 100, 60):
				self.state = 'Menu'
			else:
				self.taps = 0
				self.startTime = time.time()
				self.speed = 0
				self.state = self.state[9:]
			
		elif self.state == 'Classic':
			self.taps += 1
			if self.taps >= 100:
				self.time = time.time() - self.startTime
				self.speed = 100 / self.time
				self.state = 'Classic Win'
				
		elif self.state == 'Timed':
			self.taps += 1
		
		elif self.state.endswith('Win'):
			if touchingText(0.85, 0.05, 100, 60):
				if self.state == 'Classic Win':
					if self.highscores['Classic'] is None or self.time < self.highscores['Classic']:
						self.highscores['Classic'] = self.time
				else:
					if self.highscores['Timed'] is None or self.taps > self.highscores['Timed']:
						self.highscores['Timed'] = self.taps
					
				if self.highscores['Speed'] is None or self.speed > self.highscores['Speed']:
					self.highscores['Speed'] = self.speed
			
				self.state = 'Menu'
		
		elif self.state == 'Highscores':
			if touchingText(0.85, 0.05, 100, 60):
				self.state = 'Menu'
				
	def formatTime(self, t):
		if t is None:
			return 'N/A'
		elif t >= 60:
			return '%d:%02d.%02d' % (t / 60, t % 60, (t % 1) * 100)
		else:
			return '%.02f' % t
				
	def pause(self):
		self.save()
			
	def stop(self):
		self.save()
		
	def save(self):
		with shelve.open('100TapsSave') as save:
			save['Highscores'] = self.highscores
		
run(Main(), PORTRAIT)
