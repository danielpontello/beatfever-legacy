# beatfever-legacy
![Beatfever logo](http://i.imgur.com/5zG4Sum.png)

BeatFever Mania is an rhythm action game for the Raspberry Pi, based on [osu!](http://osu.ppy.sh/)'s "Catch the Beat" mode. Fruits fall from the top of the screen along with a song, and you need to catch them before they fall to the ground. We developed this project for our university's faire, [FETIN](http://www.inatel.br/fetin/) 2015. We had no prior experience on either Python or Raspberry Pi development, and we had very little time to finish this project. Because of that, the code ended up ___very___ messy. The code published here is exactly the same we used to present on the faire, including all the (many)bugs and hacks.
A major refactor is planned Soon™, but any improvements are welcome.

## Libraries required:
- [Pi3d](https://github.com/tipam/pi3d)
- [PyGame](http://www.pygame.org/)
- [Pillow](https://python-pillow.github.io/)
- Python 2.7
- A screen with 1920x1080 resolution

You can install all of the libraries with the pip package manager:
`pip install pygame pi3d pillow`

## Development Notes
###Libraries
Our goal was to recreate the "Catch the Beat" mode from osu!, a popular rhythm game for PC, on the Raspberry Pi. First of all, we needed a library that could output hardware-accelerated graphics on the Raspberry. We tried Love2D and PyGame, but we haven't managed to get they working with the RPi's GPU. The only one we found with proper hardware-accelerated graphics was Pi3D, so we sticked with it for the rest of the development proccess.

###File Format
We planned to create our own file format for the song data, composed of a .ZIP file with a JSON file containing song information and the time and position of the fruits (where and when they should fall along with the music), and a MP3/OGG file with the audio data. However, because of the time constraints, we decided to use osu!'s [file format](https://osu.ppy.sh/wiki/Osu_(file_format)) instead. That had the added benefit of making our game compatible with osu!'s beatmaps.

With that decided, we wrote some parsing functions, found on the [FileParser.py](https://github.com/danielpontello/beatfever-legacy/blob/master/FileParser.py) file. The parser code is used to obtain the fruits (file [nota.py](https://github.com/danielpontello/beatfever-legacy/blob/master/nota.py)) and miscellaneous song info (name, artist, BPM) from the beatmap files.

###Syncing fruits with the music
With the parser done, we had all the times and positions of the fruits of a song. Now, we needed to draw them on the screen and sync them with the song. Directly defining the Y position of each fruit to the song position worked, but the fruits movement were wonky and unreliable. The solution found is described [on this reddit post](https://www.reddit.com/r/gamedev/comments/13y26t/how_do_rhythm_games_stay_in_sync_with_the_music/c78aawd); the song time is interpolated in order to obtain a more precise time value ([OsuPi.py, lines 361-369](https://github.com/danielpontello/beatfever-legacy/blob/master/OsuPi.py#L361-L369)). After implementing this fix, the fruits were moving smoothly across the screen.

###Input
The Pi3d version we used uses [ncurses](https://www.gnu.org/software/ncurses/) for input, which is a console-based way of getting keyboard input. That meant it only worked on the current terminal window, and was very limited on how much keys you could press simultaneously. To solve that, we opened a PyGame window on the background, and used the PyGame input functions instead of the Pi3d native ones.

###Drawing the background

Drawing the background every frame at 1080p resolution on Pi3d was very perfonrmance-heavy; that made the game run at <20FPS speeds. So, we made the PyGame window fullscreen and borderless, and drew the background once on it. Then, we made the Pi3d background transparent, so the PyGame window appears behind the Pi3d one. Because the PyGame window has the background drawn on it, you can see the background rendered in PyGame behind the game elements rendered on Pi3d.

## Resources
- [Pi3d Book](http://paddywwoof.github.io/pi3d_book/_build/html/)
- [Pi3d Documentation](https://pi3d.github.io/html/)
- [PyGame Documentation](https://www.pygame.org/docs/)
- [Raspberry Pi Forums](https://www.raspberrypi.org/forums/)
- [Reddit r/gamedev](https://www.reddit.com/r/gamedev)

## Thanks
We would like to thank our master and inspiration:

![We would like to thank our master and inspiration](http://i.imgur.com/jktSRrJ.jpg)

Seriously, huge thanks goes to:
 - paddyg, for helping us with Pi3D rendering and general OpenGL stuff

## Authors
Daniel Sader & Pedro Polez
