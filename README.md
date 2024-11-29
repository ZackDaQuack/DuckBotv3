# Duck Bot V3 🦆
This is the source code for a very popular bot in a server im admin it. I released this for people to learn and be able to make their own cool bot.

*This is the third time I had to rewrite it due to crappy code lol.*

# 🤖 Update 3.1: The Ai Update
Lots of new stuff was added and fixed! Here are some of the most important changes:

- **Quack AI Overhaul**
    - Migrated to Google's **JSON Structured Output** (I came up with this idea first lol)
    - Added more error handling
    - Reworked some stuff to make it more readable
    - **Quack can now:**
      - get message content from replys
      - generate ai images
      - delete user messages
      - time users out

- **New Commands**
    - **/shutdown** Shutdown the bot for emergencys
    - **/annoy** Perfect for annoying people
    - **/execute** Executes Python code on the server with access to local varriables such as ctx, message. Only the bot owner can run this. **WARNING: This will execute ANYTHING! I'm not responsible if you delete system32 💀**

- **Bug Fixes**
  - main.py as rewritten
  - more error handling
  - other small things

# ✨ Features

Well, what does it do? It has:

- duckAI, a smart chatbot that can intereact with users
- A social credit system
- Quests to obtain Social Credit
- Roblox status tracker
- Fun admin commands, such as dm user and say

# 🧠 DuckAI
Initially added as a joke, this feature became the main reason people love this bot.

The AI is powered by Google Gemini and can:

- respond to the user (obviously)
- generate ai images
- react to the user's message
- send the user a dm
- report a message to staff if it's bad
- delete a users message
- timeout users
- and more

The bot is aware if the user is a staff member, time, chanel name, status of Roblox, and finally, user info (username and id)

This *MIGHT* be the smartest chatbot on Discord.

# 💰 Social Credits
The social credit system does what you expect, it comes with commands to add and deduct credits, and quests to let users earn them on their own. All credits are tracked using an SQLite database.

# 🎮 Quests
I have no idea why I wanted to add this feature. This was the most painful and time-consuming thing to add. Anyways, it gives quests such as sending a random number of messages and stuff.

# 📈 Status Tracker
This feature was the main reason why the bot was created in the first place. It updates an embed in a status channel with Roblox updates.

# 🛠️ Commands
There are various commands to use, its kinda lacking (please contribute), but still fun. You can dm people and stuff.

# 🚀 Get Involved
Thanks for reading all the way! Feel free to look over the source code and contribute! If your contributions are cool, I will merge them into the project :)

