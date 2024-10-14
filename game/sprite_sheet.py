# reference: https://youtu.be/M6e3_8LHc7A
import pygame

# Class to get an image from a spritesheet
class SpriteSheet():
	def __init__(self, image):
		self.sheet = image

	# get image from spritesheet
	def get_image(self, frame, width, height, scale, colour):
		
		image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha() # create blank surface
		image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))	# put image onto image surface
		# Create the subsurface (62x128 pixels) centered horizontally
		# image = image.subsurface((40, 0, 44, height))
		# image = pygame.transform.scale(image, (44 * scale, height * scale))	# scale the image
		image = pygame.transform.scale(image, (width * scale, height * scale))	# scale the image
		# image.set_colorkey(colour)	# set color key based on spritesheet background color (background of spritesheet is already transparent in my case therefore no color_key is required)
		return image  # return image