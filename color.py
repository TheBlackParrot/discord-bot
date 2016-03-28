from PIL import Image;
from io import BytesIO;

class ColorPreview():
	def __init__(self, color="#000000"):
		self.img = Image.new('RGB', (100, 100), color);
		self.stream = BytesIO();

		self.img.save(self.stream, format="PNG");

		self.stream.seek(0, 0);

	def getBuffer(self):
		return self.stream.getbuffer();

	def getStream(self):
		return self.stream;

	def getValue(self):
		return self.stream.getvalue();